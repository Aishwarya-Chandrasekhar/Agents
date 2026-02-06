import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

class RetrieverTool:
    def __init__(self, docs_folder="sample_docs"):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.texts = self._load_docs(docs_folder)
        self.embeddings = self.model.encode(self.texts)
        self.index = self._build_index(self.embeddings)

    def _load_docs(self, folder):
        lines = []
        for file in os.listdir(folder):
            path = os.path.join(folder, file)
            with open(path, "r", encoding="utf-8") as f:
                for line in f.read().split("\n"):
                    if line.strip():
                        lines.append(line.strip())
        return lines

    def _build_index(self, embeddings):
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(np.array(embeddings).astype("float32"))
        return index

    def query(self, question: str, k: int = 3):
        q_emb = self.model.encode([question]).astype("float32")
        D, I = self.index.search(q_emb, k)
        return [self.texts[i] for i in I[0]]
