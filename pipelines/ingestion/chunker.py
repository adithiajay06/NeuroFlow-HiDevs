import re
import numpy as np
import tiktoken
from sklearn.metrics.pairwise import cosine_similarity
from backend.providers.client import NeuroFlowClient
from backend.providers.router import RoutingCriteria
from backend.providers.base import ChatMessage

def sentence_split(text: str) -> list[str]:
    # Simple sentence splitter
    return re.split(r'(?<=[.!?]) +', text)

def fixed_size_chunk(text: str, target_tokens=512, overlap=64, model="gpt-4o-mini") -> list[str]:
    enc = tiktoken.encoding_for_model(model)
    sentences = sentence_split(text)
    chunks = []
    current = []
    current_tokens = 0

    for sent in sentences:
        sent_tokens = len(enc.encode(sent))
        if current_tokens + sent_tokens > target_tokens:
            # finalize current chunk
            chunks.append(" ".join(current))
            # overlap
            overlap_sents = current[-overlap:] if overlap < len(current) else current
            current = overlap_sents + [sent]
            current_tokens = sum(len(enc.encode(s)) for s in current)
        else:
            current.append(sent)
            current_tokens += sent_tokens

    if current:
        chunks.append(" ".join(current))
    return chunks

async def semantic_chunk(text: str, client: NeuroFlowClient, model="text-embedding-3-small") -> list[str]:
    sentences = sentence_split(text)
    embeddings = await client.embed(sentences, RoutingCriteria(task_type="embedding"))
    sims = cosine_similarity(embeddings[:-1], embeddings[1:])
    chunks = []
    current = [sentences[0]]

    for i, sim in enumerate(sims.flatten()):
        if sim < 0.7:
            chunks.append(" ".join(current))
            current = [sentences[i+1]]
        else:
            current.append(sentences[i+1])

    if current:
        chunks.append(" ".join(current))
    return chunks

def hierarchical_chunk(pages: list, headings_key="level") -> list[dict]:
    chunks = []
    current_parent = None

    for page in pages:
        if headings_key in page.metadata:
            level = page.metadata[headings_key]
            if level == "h1":
                current_parent = {"parent": page.content, "children": []}
                chunks.append(current_parent)
            else:
                if current_parent:
                    current_parent["children"].append(page.content)
        else:
            if current_parent:
                current_parent["children"].append(page.content)
            else:
                chunks.append({"parent": None, "children": [page.content]})
    return chunks

def auto_chunk(pages: list, client: NeuroFlowClient) -> list:
    results = []
    for page in pages:
        if page.content_type == "table":
            chunks = fixed_size_chunk(page.content)
        elif "level" in page.metadata:
            chunks = hierarchical_chunk([page])
        elif page.metadata.get("page_count", 0) > 50:
            # semantic for long PDFs
            chunks = asyncio.run(semantic_chunk(page.content, client))
        else:
            chunks = fixed_size_chunk(page.content)
        results.extend(chunks)
    return results
