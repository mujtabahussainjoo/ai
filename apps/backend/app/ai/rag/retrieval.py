"""RAG retrieval over stored document chunks.

Keyword-first retrieval (BM25) so that RAG works fully offline out of the box,
matching the default ``EMBEDDING_PROVIDER=keyword`` configuration.
"""

from __future__ import annotations

import re
import uuid

from rank_bm25 import BM25Okapi
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.repositories.document import DocumentChunkRepository
from app.schemas.documents import RAGRetrievalItem


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


async def retrieve_context(
    session: AsyncSession,
    *,
    document_ids: list[uuid.UUID],
    query: str,
    top_k: int | None = None,
    min_score: float | None = None,
) -> list[RAGRetrievalItem]:
    """Return the most relevant chunks for ``query`` across ``document_ids``."""
    if not document_ids or not query.strip():
        return []
    chunks = await DocumentChunkRepository(session).chunks_for_documents(document_ids)
    if not chunks:
        return []
    top_k = top_k or settings.RETRIEVAL_TOP_K
    threshold = min_score if min_score is not None else settings.RETRIEVAL_MIN_SCORE

    corpus = [_tokenize(chunk.content) for chunk in chunks]
    query_tokens = _tokenize(query)
    bm25 = BM25Okapi(corpus)
    scores = bm25.get_scores(query_tokens)
    ranked = sorted(zip(chunks, scores), key=lambda pair: pair[1], reverse=True)
    selected = [(chunk, score) for chunk, score in ranked if score >= threshold]
    if not selected and ranked:
        # BM25 IDF is negative for tiny corpora (single/few documents); the user
        # explicitly selected these documents, so always surface the best chunks.
        selected = ranked[: max(1, top_k)]
    return [
        RAGRetrievalItem(
            document_id=chunk.document_id,
            chunk_index=chunk.chunk_index,
            content=chunk.content,
            score=max(0.0, round(score, 4)),
        )
        for chunk, score in selected[:top_k]
    ]


def format_context(items: list[RAGRetrievalItem]) -> str:
    """Build the prompt-ready document context block."""
    if not items:
        return ""
    sections = [
        f"[source {item.document_id}] chunk {item.chunk_index}:\n{item.content}" for item in items
    ]
    return "\n\n---\n\n".join(sections)