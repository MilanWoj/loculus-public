# Author: MilanWoj
import json
import time
from pathlib import Path
from tempfile import TemporaryDirectory

import httpx
from fastapi import APIRouter, UploadFile
from sse_starlette.sse import EventSourceResponse

from app.api.schemas import ChatRequest, HealthStatus
from app.core.config import settings
from app.core.llm_client import stream_chat_completion, LLMError
from app.core.metrics import get_host_metrics
from app.rag.orchestrator import orchestrate
from app.rag.ingest import ingest_folder

router = APIRouter()


@router.get("/health", response_model=HealthStatus)
async def health_check() -> HealthStatus:
    async def ping(url: str) -> bool:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                r = await client.get(url)
                return r.status_code < 500
        except httpx.RequestError:
            return False

    return HealthStatus(
        llm=await ping(f"{settings.llm_base_url}/models"),
        embeddings=await ping(f"{settings.embeddings_base_url}/models"),
        qdrant=await ping(f"http://{settings.qdrant_host}:6333/healthz"),
        searxng=await ping(f"{settings.searxng_base_url}/healthz"),
    )


@router.get("/metrics")
async def metrics():
    return get_host_metrics()


@router.post("/chat")
async def chat(request: ChatRequest):
    async def event_generator():
        t_start = time.perf_counter()
        try:
            result = await orchestrate(request.query, mode=request.mode)
        except Exception as exc:
            yield {"event": "error", "data": f"Orchestration failed: {exc}"}
            return

        if result.clarification:
            yield {"event": "clarification", "data": result.clarification}
            total_ms = round((time.perf_counter() - t_start) * 1000, 1)
            yield {"event": "done", "data": json.dumps({**result.timings_ms, "generation_ms": 0, "total_ms": total_ms})}
            return

        yield {"event": "sources", "data": json.dumps(result.sources, ensure_ascii=False)}
        for warning in result.warnings:
            yield {"event": "warning", "data": warning}

        t_generation_start = time.perf_counter()
        try:
            async for token in stream_chat_completion(result.messages):
                yield {"event": "token", "data": token}
        except LLMError as exc:
            yield {"event": "error", "data": str(exc)}
            return

        total_ms = round((time.perf_counter() - t_start) * 1000, 1)
        generation_ms = round((time.perf_counter() - t_generation_start) * 1000, 1)
        yield {
            "event": "done",
            "data": json.dumps({**result.timings_ms, "generation_ms": generation_ms, "total_ms": total_ms}),
        }

    return EventSourceResponse(event_generator())


@router.post("/documents/ingest")
async def ingest_documents(files: list[UploadFile]):
    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        for file in files:
            content = await file.read()
            (tmp_path / file.filename).write_bytes(content)
        await ingest_folder(tmp_path)

    return {"status": "ok", "files_ingested": len(files)}
