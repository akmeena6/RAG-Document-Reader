import os

import chromadb
from chromadb.utils import embedding_functions

# Initialize ChromaDB client
chroma_client = chromadb.Client()

# Define the embedding function
# This ensures we use the same model for adding and querying
embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# Get or create the collection
collection = chroma_client.get_or_create_collection(
    name="doc_chunks",
    embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    ),
)


def add_chunks_to_collection(chunks, ids=None, metadatas=None):
    """Adds document chunks to the ChromaDB collection."""
    if ids is None:
        ids = [str(i) for i in range(len(chunks))]

    if metadatas is None:
        metadatas = [{"source": "pdf_document"} for _ in chunks]

    collection.add(documents=chunks, ids=ids, metadatas=metadatas)
    print(f"Added {len(chunks)} chunks to the collection.")


# --- New Semantic Search Function ---


def semantic_search(query_text: str, topk_results: int = 3):
    """
    Performs semantic search using the collection's embedding function.
    Returns: A list of the most relevant document chunks.
    """
    if not query_text:
        return []

    # Query the collection using the raw text; ChromaDB handles the embedding
    results = collection.query(query_texts=[query_text], n_results=topk_results)

    return results["documents"][0]
