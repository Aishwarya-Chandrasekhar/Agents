import faiss
import numpy as np

def build_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index

def search(query_embedding, index, texts, k=3):
    D, I = index.search(query_embedding, k)
    return [texts[i] for i in I[0]]
