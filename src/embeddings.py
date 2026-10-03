"""Turn text into vectors (lists of numbers) - free, runs on your own machine.

We use Chroma's built-in ONNX MiniLM model: small (no PyTorch needed), so it
also fits on free hosting. It downloads once (~80 MB) on first use.
"""
import math
from functools import lru_cache

from chromadb.utils.embedding_functions import DefaultEmbeddingFunction


@lru_cache(maxsize=1)
def _model():
    return DefaultEmbeddingFunction()


def embed(texts: list[str]) -> list[list[float]]:
    vectors = _model()(texts)
    return [[float(x) for x in v] for v in vectors]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """1.0 = same direction (very similar), 0 = unrelated, -1 = opposite."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0
