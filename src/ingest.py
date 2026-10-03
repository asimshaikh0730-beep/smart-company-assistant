"""Build the search index from the documents.  Run:  python -m src.ingest"""
from src import config, vector_store
from src.chunker import chunk_text
from src.loader import load_documents


def build_index() -> int:
    docs = load_documents()
    if not docs:
        raise SystemExit(f"No documents found in {config.POLICIES_DIR}")

    chunks = []
    for doc in docs:
        pieces = chunk_text(doc["text"], config.CHUNK_SIZE, config.CHUNK_OVERLAP)
        for i, piece in enumerate(pieces):
            chunks.append({"id": f"{doc['source']}::{i}", "source": doc["source"], "text": piece})

    print(f"Loaded {len(docs)} documents -> {len(chunks)} chunks. Embedding...")
    vector_store.build_index(chunks)
    print("Index built.")
    return len(chunks)


if __name__ == "__main__":
    build_index()
