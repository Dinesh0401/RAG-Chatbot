import os
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler

from utils.logging_config import get_logger
from rag_service import RAGService, RAGError

logger = get_logger("app")

app = FastAPI(title="RAG Chatbot API")
service = None


@app.on_event("startup")
def startup_event():
    global service
    try:
        service = RAGService()
    except Exception as e:
        logger.exception("Failed to initialize RAGService on startup")


@app.post("/chat")
async def chat(
    question: str = Form(...), files: Optional[List[UploadFile]] = File(None), k: int = Form(5)
):
    if not question or not question.strip():
        raise HTTPException(status_code=400, detail="Question is required")

    # ingest uploaded files, if any
    if files:
        file_bytes = []
        for f in files:
            try:
                content = await f.read()
            except Exception:
                logger.exception("Failed to read uploaded file")
                raise HTTPException(status_code=400, detail=f"Failed to read file {f.filename}")
            file_bytes.append((f.filename, content))

        try:
            service.ingest_bytes_list(file_bytes)
        except ValueError as e:
            logger.warning("Ingestion called with no files or empty files")
            raise HTTPException(status_code=400, detail=str(e))
        except RAGError as e:
            logger.exception("Ingestion error")
            raise HTTPException(status_code=500, detail=str(e))
        except Exception:
            logger.exception("Unexpected ingestion error")
            raise HTTPException(status_code=500, detail="Ingestion failed")

    try:
        answer, sources = service.query(question, k)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RAGError as e:
        logger.exception("RAGService error during query")
        raise HTTPException(status_code=502, detail=str(e))
    except Exception:
        logger.exception("Unhandled error during query")
        raise HTTPException(status_code=500, detail="Internal server error")

    return JSONResponse({"answer": answer, "sources": sources})


@app.get("/health")
def health():
    return JSONResponse({"status": "ok"})


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP error: {exc.detail}")
    return await http_exception_handler(request, exc)


@app.exception_handler(Exception)
async def unexpected_exception_handler(request: Request, exc: Exception):
    logger.exception("Unexpected server error")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000)
