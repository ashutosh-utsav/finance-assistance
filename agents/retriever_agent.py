import os
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Any


MODEL_NAME = 'all-MiniLM-L6-v2'
FAISS_INDEX_PATH = 'faiss_index.bin'
DOCUMENTS_PATH = 'documents.pkl'
model = SentenceTransformer(MODEL_NAME)

def create_and_store_embeddings(documents: list):
    """(No changes to this function)"""
    if not documents:
        print("No documents provided to embed.")
        return
    embeddings = model.encode(documents, convert_to_tensor=False)
    d = embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(embeddings)
    faiss.write_index(index, FAISS_INDEX_PATH)
    with open(DOCUMENTS_PATH, 'wb') as f:
        pickle.dump(documents, f)

def retrieve_top_k(query: str, k: int = 3) -> Dict[str, List[Any]]:
    """
    Retrieves the top k most relevant documents AND their scores.
    NOW RETURNS A DICTIONARY.
    """

    if not os.path.exists(FAISS_INDEX_PATH):
        return {"documents": ["Error: Vector database not found."], "scores": []}

    index = faiss.read_index(FAISS_INDEX_PATH)
    with open(DOCUMENTS_PATH, 'rb') as f:
        documents = pickle.load(f)

    query_vector = model.encode([query])
    
  
    distances, indices = index.search(query_vector, k)

    valid_indices = [i for i in indices[0] if i != -1]
    
    results = [documents[i] for i in valid_indices]
    scores = [float(d) for d, i in zip(distances[0], indices[0]) if i != -1]
    
    return {"documents": results, "scores": scores}