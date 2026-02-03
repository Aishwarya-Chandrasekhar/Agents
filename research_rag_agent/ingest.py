import os

def load_documents(folder="sample_docs"):
    docs = []
    for file in os.listdir(folder):
        with open(os.path.join(folder, file)) as f:
            docs.extend(f.read().split("\n"))
    return [d for d in docs if d.strip()]
