import httpx
import trafilatura
import urllib.robotparser
from . import ExtractedPage

async def extract_url(url: str) -> list[ExtractedPage]:
    pages: list[ExtractedPage] = []

    # Check robots.txt
    parsed = urllib.robotparser.RobotFileParser()
    robots_url = url.split("/")[0] + "//" + url.split("/")[2] + "/robots.txt"
    try:
        parsed.set_url(robots_url)
        parsed.read()
        if not parsed.can_fetch("*", url):
            raise PermissionError(f"Fetching {url} disallowed by robots.txt")
    except Exception:
        # If robots.txt missing or error, proceed cautiously
        pass

    # Fetch page
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        html = resp.text

    # Extract main content
    extracted = trafilatura.extract(html, include_tables=True, output_format="json")
    if not extracted:
        return []

    data = trafilatura.extract(html, include_tables=True, output_format="json", with_metadata=True)
    metadata = {
        "title": data.get("title"),
        "author": data.get("author"),
        "canonical_url": data.get("url"),
        "publish_date": data.get("date"),
    }

    pages.append(
        ExtractedPage(
            page_number=1,
            content=data.get("text", ""),
            content_type="text",
            metadata=metadata,
        )
    )

    return pages
