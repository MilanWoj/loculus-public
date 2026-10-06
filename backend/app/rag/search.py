# Author: MilanWoj
from qdrant_client import QdrantClient
from app.core.config import settings
from app.rag.embeddings import embed_texts


async def search_documents(query: str, top_k: int | None = None) -> list[dict]:
    top_k = top_k or settings.top_k_results
    client = QdrantClient(host=settings.qdrant_host, grpc_port=settings.qdrant_grpc_port, prefer_grpc=True)

    if not client.collection_exists(settings.qdrant_collection):
        return []  # nothing has been ingested yet

    query_vector = (await embed_texts([query]))[0]

    results = client.query_points(
        collection_name=settings.qdrant_collection,
        query=query_vector,
        limit=top_k,
    ).points

    return [
        {"text": r.payload["text"], "source": r.payload["source"], "score": round(r.score, 4)}
        for r in results
    ]