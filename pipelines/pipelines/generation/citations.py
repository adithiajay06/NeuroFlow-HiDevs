import re
from dataclasses import dataclass

@dataclass
class Citation:
    reference: str
    chunk_id: str
    document_name: str
    page_number: int | None
    content_preview: str
    invalid_citation: bool = False

def parse_citations(response: str, context_result) -> list[Citation]:
    matches = re.findall(r"

\[Source (\d+)\]

", response)
    citations = []
    for m in matches:
        idx = int(m) - 1
        if idx < len(context_result["chunks_used"]):
            chunk_id = context_result["chunks_used"][idx]
            # Lookup chunk metadata (pseudo-code)
            doc_name = "doc.pdf"
            page = 3
            preview = context_result["context"][:100]
            citations.append(Citation(f"Source {m}", chunk_id, doc_name, page, preview))
        else:
            citations.append(Citation(f"Source {m}", "", "", None, "", invalid_citation=True))
    return citations
