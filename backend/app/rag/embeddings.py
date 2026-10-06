# Author: MilanWoj
import httpx
from app.core.config import settings


class EmbeddingError(Exception):
    pass


async def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{settings.embeddings_base_url}/embeddings",
                json={"input": texts, "model": "nomic-embed-text"},
            )
            response.raise_for_status()
        except httpx.ConnectError as exc:
            raise EmbeddingError(f"Cannot reach the embeddings server at {settings.embeddings_base_url}") from exc
        except httpx.HTTPStatusError as exc:
            raise EmbeddingError(f"Embeddings API error: {exc.response.text}") from exc

    data = response.json()
    # API doesn't guarantee ordering, re-sort by index
    sorted_items = sorted(data["data"], key=lambda item: item["index"])
    return [item["embedding"] for item in sorted_items]
