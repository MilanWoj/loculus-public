# Author: MilanWoj
import asyncio
import time
from dataclasses import dataclass, field
from typing import Literal

from app.core.prompts import SYSTEM_PROMPT, NO_CONTEXT_SYSTEM_PROMPT, build_context_block
from app.rag.search import search_documents
from app.rag.embeddings import EmbeddingError
from app.rag.clarify import check_ambiguity
from app.rag.query_rewrite import rewrite_for_search
from app.web.search_client import search_web, WebSearchError

SearchMode = Literal["auto", "web", "docs"]


@dataclass
class OrchestrationResult:
    messages: list[dict]
    sources: list[dict]
    timings_ms: dict = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    clarification: str | None = None


async def orchestrate(query: str, mode: SearchMode = "auto") -> OrchestrationResult:
    warnings: list[str] = []
    timings: dict[str, float] = {}

    t0 = time.perf_counter()
    clarification = await check_ambiguity(query)
    timings["ambiguity_check_ms"] = round((time.perf_counter() - t0) * 1000, 1)
    if clarification:
        return OrchestrationResult(messages=[], sources=[], timings_ms=timings, clarification=clarification)

    async def timed_docs():
        t0 = time.perf_counter()
        try:
            results = await search_documents(query)
        except EmbeddingError as exc:
            warnings.append(f"Document search unavailable: {exc}")
            results = []
        timings["retrieval_docs_ms"] = round((time.perf_counter() - t0) * 1000, 1)
        return results

    async def timed_web():
        t0 = time.perf_counter()
        try:
            search_query, time_range = await rewrite_for_search(query)
            results = await search_web(search_query, time_range=time_range)
        except WebSearchError as exc:
            warnings.append(f"Web search unavailable: {exc}")
            results = []
        timings["retrieval_web_ms"] = round((time.perf_counter() - t0) * 1000, 1)
        return results

    doc_sources: list[dict] = []
    web_sources: list[dict] = []

    if mode == "docs":
        doc_sources = await timed_docs()
    elif mode == "web":
        web_sources = await timed_web()
    else:
        doc_sources, web_sources = await asyncio.gather(timed_docs(), timed_web())

    all_sources = [
        {"title": s["title"], "url": s["url"], "snippet": s["snippet"], "origin": "web"}
        for s in web_sources
    ] + [
        {"title": s["source"], "url": None, "snippet": s["text"], "origin": "document"}
        for s in doc_sources
    ]

    if all_sources:
        context_block = build_context_block([
            {"title": s["title"], "url": s.get("url") or s["title"], "snippet": s["snippet"]}
            for s in all_sources
        ])
        system_prompt = SYSTEM_PROMPT.format(context=context_block)
    else:
        system_prompt = NO_CONTEXT_SYSTEM_PROMPT
        warnings.append("No source found (web and documents); unverified answer.")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query},
    ]

    return OrchestrationResult(messages=messages, sources=all_sources, timings_ms=timings, warnings=warnings)
