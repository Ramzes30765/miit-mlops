from dataclasses import dataclass
from typing import List
import torch
from sentence_transformers import CrossEncoder

from qdrant_retriever import RetrievedChunk


@dataclass
class RerankedChunk:
    chunk: RetrievedChunk
    rerank_score: float


class Reranker:
    def __init__(
        self,
        model_name: str = "BAAI/bge-reranker-v2-m3",
        device: str = "cuda",
    ) -> None:
        self.model = CrossEncoder(model_name, device=device)

    def rerank(
        self,
        query: str,
        chunks: List[RetrievedChunk],
        top_n: int = 5,
    ) -> List[RetrievedChunk]:
        if not chunks:
            return []

        pairs = [(query, chunk.text) for chunk in chunks]
        scores = self.model.predict(pairs)

        ranked = sorted(
            zip(chunks, scores),
            key=lambda x: x[1],
            reverse=True,
        )

        return [chunk for chunk, _ in ranked[:top_n]]