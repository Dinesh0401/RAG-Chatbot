import io
import time
import uuid
from typing import List, Tuple, Optional

from dotenv import load_dotenv
load_dotenv()

from utils.logging_config import get_logger
logger = get_logger("rag_service")

from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma

import pypdf


class RAGError(Exception):
    pass


class RAGService:
    def __init__(self, chroma_path: str = "chroma_db", collection_name: str = "example_collection"):
        self.logger = logger
        self.chroma_path = chroma_path
        self.collection_name = collection_name

        # initialize models and vector store with error handling
        try:
            self.logger.info("Initializing embeddings model")
            self.embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")
        except Exception as e:
            self.logger.exception("Failed to initialize embeddings model")
            raise RAGError("Embeddings initialization failed") from e

        try:
            self.logger.info("Initializing LLM")
            self.llm = ChatOpenAI(temperature=0.5, model='gpt-4o-mini')
        except Exception:
            self.logger.exception("Failed to initialize LLM")
            # don't expose internals
            raise RAGError("LLM initialization failed")

        try:
            self.logger.info("Connecting to Chroma vector store")
            self.vector_store = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings_model,
                persist_directory=self.chroma_path,
            )
        except Exception:
            self.logger.exception("Failed to connect to ChromaDB")
            raise RAGError("ChromaDB unavailable")

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=100,
            length_function=len,
            is_separator_regex=False,
        )

        self.logger.info("RAGService initialized")

    def _pdf_bytes_to_documents(self, filename: str, file_bytes: bytes) -> List[Document]:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        docs: List[Document] = []
        for i, page in enumerate(reader.pages):
            try:
                text = page.extract_text() or ""
            except Exception:
                text = ""
            metadata = {"source": filename, "page": i + 1}
            docs.append(Document(page_content=text, metadata=metadata))
        return docs

    def ingest_bytes_list(self, files: List[Tuple[str, bytes]]):
        if not files:
            self.logger.warning("ingest_bytes_list called with empty file list")
            raise ValueError("No files provided for ingestion")

        all_chunks = []
        total_docs = 0
        for filename, b in files:
            self.logger.info(f"Ingesting file: {filename}")
            try:
                documents = self._pdf_bytes_to_documents(filename, b)
            except Exception as e:
                self.logger.exception(f"Failed to parse PDF: {filename}")
                continue

            total_docs += len(documents)

            if not any((d.page_content or "").strip() for d in documents):
                self.logger.warning(f"No text extracted from {filename}")
                continue

            try:
                chunks = self.text_splitter.split_documents(documents)
            except Exception:
                self.logger.exception(f"Failed to split document: {filename}")
                continue

            # attach filename metadata is already present on docs; chunks preserve metadata
            all_chunks.extend(chunks)
            self.logger.info(f"Created {len(chunks)} chunks for {filename}")

        if not all_chunks:
            self.logger.warning("No chunks to add to vector store after processing files")
            return

        uuids = [str(uuid.uuid4()) for _ in range(len(all_chunks))]
        try:
            self.vector_store.add_documents(documents=all_chunks, ids=uuids)
            # some Chroma wrappers offer persist; guard call
            try:
                if hasattr(self.vector_store, "persist"):
                    self.vector_store.persist()
            except Exception:
                self.logger.debug("Chroma persist() not available or failed; continuing")
        except Exception:
            self.logger.exception("Failed to upsert documents into ChromaDB")
            raise RAGError("Failed to write to vector store")

        self.logger.info(f"Upserted {len(all_chunks)} chunks into ChromaDB from {total_docs} pages")

    def _build_knowledge(self, docs: List[Document]) -> str:
        knowledge = ""
        for doc in docs:
            knowledge += (doc.page_content or "") + "\n\n"
        return knowledge

    def query(self, question: str, k: int = 5) -> Tuple[str, List[dict]]:
        if not question or not question.strip():
            raise ValueError("Empty question provided")

        try:
            retriever = self.vector_store.as_retriever(search_kwargs={"k": k})
        except Exception:
            self.logger.exception("Failed to create retriever")
            raise RAGError("Retrieval layer unavailable")

        # try multiple retriever method names for compatibility
        docs = []
        try:
            if hasattr(retriever, "get_relevant_documents"):
                docs = retriever.get_relevant_documents(question)
            elif hasattr(retriever, "retrieve"):
                docs = retriever.retrieve(question)
            elif hasattr(retriever, "invoke"):
                docs = retriever.invoke(question)
            else:
                raise RAGError("Retriever has no supported retrieval method")
        except Exception:
            self.logger.exception("Retrieval failed")
            raise RAGError("Retrieval failed")

        self.logger.info(f"Retrieved {len(docs)} documents for the question")

        knowledge = self._build_knowledge(docs)

        rag_prompt = f"""
    You are an assistant which answers questions based only on the knowledge provided in the "The knowledge" section below.
    Do not use external or internal world knowledge beyond the provided knowledge.
    Keep the answer concise (max ~150 words). At the end, do NOT repeat the full source text — instead answer, then the system will provide exact source snippets separately.

    Question: {question}

    The knowledge:
    {knowledge}
    """

        # retry logic for LLM call
        attempts = 0
        max_attempts = 2
        answer = ""
        last_err: Optional[Exception] = None
        while attempts < max_attempts:
            try:
                self.logger.info(f"Calling LLM (attempt {attempts + 1})")
                for response in self.llm.stream(rag_prompt):
                    # response may be a delta with .content
                    answer += getattr(response, "content", str(response))

                sources = [
                    {"source": getattr(d, "metadata", {}).get("source"),
                     "page": getattr(d, "metadata", {}).get("page"),
                     "snippet": (d.page_content or "")[:300]}
                    for d in docs
                ]
                self.logger.info("LLM call succeeded")
                return answer, sources
            except Exception as e:
                last_err = e
                attempts += 1
                self.logger.warning(f"LLM call failed (attempt {attempts}): {e}")
                time.sleep(1)

        self.logger.exception("LLM call failed after retries")
        raise RAGError("LLM call failed") from last_err
