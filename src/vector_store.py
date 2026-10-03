"""Store and search chunk vectors in Chroma (free, local, saved on disk)."""
import chromadb

from src import config
from src.embeddings import embed


def _client():
    return chromadb.PersistentClient(path=str(config.CHROMA_DIR))


def _collection():
    return _client().get_or_create_collection(
        name=config.COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )


def count() -> int:
    return _collection().count()


def build_index(chunks: list[dict]) -> None:
    """chunks: [{'id', 'source', 'text'}]. Wipes the old index and rebuilds it."""
    client = _client()
    try:
        client.delete_collection(config.COLLECTION_NAME)
    except Exception:
        pass  # nothing to delete the first time
    col = _collection()
    texts = [c["text"] for c in chunks]
    col.add(
        ids=[c["id"] for c in chunks],
        documents=texts,
        embeddings=embed(texts),
        metadatas=[{"source": c["source"]} for c in chunks],
    )


def search(query: str, k: int = config.TOP_K) -> list[dict]:
    """Return the k closest chunks: [{'text', 'source', 'distance'}]."""
    col = _collection()
    if col.count() == 0:
        return []
    res = col.query(query_embeddings=embed([query]), n_results=min(k, col.count()))
    return [
        {"text": doc, "source": meta["source"], "distance": dist}
        for doc, meta, dist in zip(
            res["documents"][0], res["metadatas"][0], res["distances"][0]
        )
    ]
