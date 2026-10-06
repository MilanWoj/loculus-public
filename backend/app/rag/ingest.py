# Author: MilanWoj
import asyncio
import sys
import uuid
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from tqdm import tqdm

from app.core.config import settings
from app.rag.chunking import split_into_chunks
from app.rag.embeddings import embed_texts, EmbeddingError
from app.rag.extract import extract_text, UnsupportedFormatError

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(host=settings.qdrant_host, grpc_port=settings.qdrant_grpc_port, prefer_grpc=True)


def ensure_collection(client: QdrantClient) -> None:
    collections = [c.name for c in client.get_collections().collections]
    if settings.qdrant_collection not in collections:
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=settings.embedding_dim, distance=Distance.COSINE),
        )


async def ingest_folder(folder: Path) -> None:
    files = [f for f in folder.rglob("*") if f.suffix.lower() in SUPPORTED_EXTENSIONS]
    if not files:
        print(f"No supported document found in {folder} ({SUPPORTED_EXTENSIONS})")
        return

    client = get_qdrant_client()
    ensure_collection(client)

    total_chunks = 0
    total_errors = 0

    for file_path in tqdm(files, desc="Ingesting documents"):
        try:
            raw_text = extract_text(file_path)
        except UnsupportedFormatError as exc:
            print(f"Skipped {file_path.name}: {exc}")
            total_errors += 1
            continue
        except Exception as exc:
            print(f"Failed to extract {file_path.name}: {exc}")
            total_errors += 1
            continue

        chunks = split_into_chunks(
            raw_text, source=file_path.name,
            chunk_size=settings.chunk_size, overlap=settings.chunk_overlap,
        )
        if not chunks:
            continue

        try:
            vectors = await embed_texts([c.text for c in chunks])
        except EmbeddingError as exc:
            print(f"Failed to embed {file_path.name}: {exc}")
            total_errors += 1
            continue

        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={"text": chunk.text, "source": chunk.source, "chunk_index": chunk.chunk_index},
            )
            for chunk, vector in zip(chunks, vectors)
        ]
        client.upsert(collection_name=settings.qdrant_collection, points=points)
        total_chunks += len(points)

    print(f"Done: {total_chunks} chunks indexed, {total_errors} error(s).")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m app.rag.ingest /path/to/folder")
        sys.exit(1)

    folder_path = Path(sys.argv[1]).expanduser().resolve()
    if not folder_path.is_dir():
        print(f"Not a directory: {folder_path}")
        sys.exit(1)

    asyncio.run(ingest_folder(folder_path))
