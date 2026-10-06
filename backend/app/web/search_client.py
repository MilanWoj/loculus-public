# Author: MilanWoj
import httpx
from app.core.config import settings


class WebSearchError(Exception):
    pass


async def search_web(query: str, limit: int | None = None, time_range: str | None = None) -> list[dict]:
    limit = limit or settings.web_search_results_limit

    params = {"q": query, "format": "json"}
    if time_range:
        params["time_range"] = time_range

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.get(
                f"{settings.searxng_base_url}/search",
                params=params,
                headers={"User-Agent": "Mozilla/5.0 (Loculus)"},
            )
            response.raise_for_status()
        except httpx.ConnectError as exc:
            raise WebSearchError(f"Cannot reach SearXNG at {settings.searxng_base_url}") from exc
        except httpx.TimeoutException as exc:
            raise WebSearchError("SearXNG timed out") from exc
        except httpx.HTTPStatusError as exc:
            raise WebSearchError(f"SearXNG error: {exc.response.status_code}") from exc

    results = response.json().get("results", [])[:limit]
    return [{"title": r.get("title", ""), "url": r.get("url", ""), "snippet": r.get("content", "")} for r in results]
