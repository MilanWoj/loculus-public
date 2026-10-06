# Author: MilanWoj
from typing import Literal
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1)
    mode: Literal["auto", "web", "docs"] = "auto"


class Source(BaseModel):
    title: str
    url: str | None = None
    snippet: str
    origin: Literal["web", "document"]


class HealthStatus(BaseModel):
    llm: bool
    embeddings: bool
    qdrant: bool
    searxng: bool
