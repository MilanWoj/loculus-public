# Author: MilanWoj
from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    chunk_index: int
    source: str


def split_into_chunks(text: str, source: str, chunk_size: int, overlap: int) -> list[Chunk]:
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    text = text.strip()
    if not text:
        return []

    chunks: list[Chunk] = []
    start = 0
    index = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        reached_end = end == text_length

        if not reached_end:
            last_period = text.rfind(".", start, end)
            if last_period != -1 and last_period > start + (chunk_size // 2):
                end = last_period + 1
                reached_end = end == text_length

        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append(Chunk(text=chunk_text, chunk_index=index, source=source))
            index += 1

        if reached_end:
            break
        start = end - overlap if end - overlap > start else end

    return chunks
