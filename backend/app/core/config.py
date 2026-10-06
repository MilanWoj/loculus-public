# Author: MilanWoj
import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_host: str = os.getenv("APP_HOST", "127.0.0.1")
    app_port: int = int(os.getenv("APP_PORT", "8000"))
    cors_origins: list = field(default_factory=lambda: os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(","))

    llm_base_url: str = os.getenv("LLM_BASE_URL", "http://127.0.0.1:8080/v1")
    embeddings_base_url: str = os.getenv("EMBEDDINGS_BASE_URL", "http://127.0.0.1:8081/v1")
    embedding_dim: int = int(os.getenv("EMBEDDING_DIM", "768"))  # nomic-embed-text-v1.5

    qdrant_host: str = os.getenv("QDRANT_HOST", "127.0.0.1")
    qdrant_grpc_port: int = int(os.getenv("QDRANT_GRPC_PORT", "6334"))
    qdrant_collection: str = os.getenv("QDRANT_COLLECTION", "local_documents")

    chunk_size: int = int(os.getenv("CHUNK_SIZE", "800"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "150"))

    top_k_results: int = int(os.getenv("TOP_K_RESULTS", "5"))

    searxng_base_url: str = os.getenv("SEARXNG_BASE_URL", "http://127.0.0.1:8888")
    web_search_results_limit: int = int(os.getenv("WEB_SEARCH_RESULTS_LIMIT", "5"))

    host_metrics_path: str = os.getenv(
        "HOST_METRICS_PATH",
        str(Path(__file__).resolve().parent.parent.parent.parent / "infra" / "run" / "host-metrics.json"),
    )


settings = Settings()
