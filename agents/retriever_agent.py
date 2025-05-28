import os
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer

# --- Configuration ---
# 'all-MiniLM-L6-v2' is a great starting model: fast and effective.
MODEL_NAME = 'all-MiniLM-L6-v2'
FAISS_INDEX_PATH = 'faiss_index.bin'
DOCUMENTS_PATH = 'documents.pkl'

# Initialize the embedding model
# This will download the model from the internet on its first run.
model = SentenceTransformer(MODEL_NAME)

def create_and_store_embeddings(documents: list):
    """
    Takes a list of text documents, embeds them, and stores them in a FAISS index.

    Args:
        documents (list): A list of strings, where each string is a document.
    """
    if not documents:
        print("No documents provided to embed.")
        return

    print(f"Embedding {len(documents)} documents using '{MODEL_NAME}'...")
    # 1. THE LIBRARIAN: Create vector embeddings for each document
    embeddings = model.encode(documents, convert_to_tensor=False)
    
    # The dimension of our vectors
    d = embeddings.shape[1]
    
    # 2. THE CARD CATALOG: Build the FAISS index
    # We use IndexFlatL2, a standard index for L2 distance (Euclidean distance).
    index = faiss.IndexFlatL2(d)
    index.add(embeddings)
    
    print(f"Saving FAISS index to '{FAISS_INDEX_PATH}'...")
    # Save the index to a file
    faiss.write_index(index, FAISS_INDEX_PATH)
    
    # We also need to save the original documents to map back from an index ID
    # to the actual text. We use pickle for this.
    with open(DOCUMENTS_PATH, 'wb') as f:
        pickle.dump(documents, f)
        
    print("Embedding and storage complete.")

def retrieve_top_k(query: str, k: int = 3) -> list:
    """
    Retrieves the top k most relevant documents for a given query.

    Args:
        query (str): The user's query.
        k (int): The number of top documents to retrieve.

    Returns:
        list: A list of the top k relevant document chunks.
    """
    # First, check if our database files exist
    if not os.path.exists(FAISS_INDEX_PATH) or not os.path.exists(DOCUMENTS_PATH):
        return ["Error: Vector database not found. Please run 'create_and_store_embeddings' first."]

    # Load the FAISS index and the documents
    index = faiss.read_index(FAISS_INDEX_PATH)
    with open(DOCUMENTS_PATH, 'rb') as f:
        documents = pickle.load(f)

    # 3. THE QUERY: Embed the user's query into a vector
    # model.encode expects a list, so we pass [query]
    query_vector = model.encode([query])
    
    # 4. THE RETRIEVAL: Search the index for the top k most similar vectors
    # index.search returns two NumPy arrays: D (distances) and I (indices)
    distances, indices = index.search(query_vector, k)
    
    # The 'indices' array contains the positions of the top results in our original list.
    top_k_indices = indices[0]
    
    # Map the indices back to the original documents
    results = [documents[i] for i in top_k_indices]
    
    return results

# This part allows you to test the file directly
if __name__ == '__main__':
    print("--- Retriever Agent Test ---")
    
    # --- Step 1: Create and store the knowledge base ---
    # In a real app, you would get these docs from your scraper_agent
    sample_docs = [
        "[BABA] Alibaba Beats Revenue Estimates On E-Commerce Strength, but profit margins fell.",
        "[TSM] TSMC forecasts strong Q3 revenue between $19.6 billion and $20.4 billion, citing massive AI chip demand.",
        "[BIDU] Baidu's quarterly revenue rises as advertising rebounds, beating market expectations.",
        "[005930.KS] Samsung Electronics flags a likely 96% plunge in Q2 profit due to a chip glut.",
        "[TSM] TSMC reports a slight miss on Q2 earnings per share but remains optimistic on AI growth."
    ]
    
    create_and_store_embeddings(sample_docs)
    
    print("\n--- Step 2: Query the knowledge base ---")
    
    # --- Test Query 1 ---
    test_query_1 = "What was the revenue forecast for TSMC?"
    print(f"Query: '{test_query_1}'")
    retrieved_docs_1 = retrieve_top_k(test_query_1, k=2)
    print("Results:")
    for doc in retrieved_docs_1:
        print(f" - {doc}")
        
    print("-" * 20)

    # --- Test Query 2 ---
    test_query_2 = "Which company saw profits fall?"
    print(f"Query: '{test_query_2}'")
    retrieved_docs_2 = retrieve_top_k(test_query_2, k=2)
    print("Results:")
    for doc in retrieved_docs_2:
        print(f" - {doc}")