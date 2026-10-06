# Author: MilanWoj
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.core.config import settings

FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"LLM: {settings.llm_base_url}")
    print(f"Embeddings: {settings.embeddings_base_url}")
    print(f"Qdrant: {settings.qdrant_host}:{settings.qdrant_grpc_port}")
    print(f"SearXNG: {settings.searxng_base_url}")
    if FRONTEND_DIST.exists():
        print(f"Serving frontend from {FRONTEND_DIST}")
    yield


app = FastAPI(title="Loculus", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
