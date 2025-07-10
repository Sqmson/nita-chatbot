# vector.py
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import re

# === Load model ===
model = SentenceTransformer("all-MiniLM-L6-v2")

# === Load document from file (e.g., rag_docs.txt) ===
with open("rag_docs.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

# === Simple chunking (split by paragraph or bullet point) ===
docs = re.split(r'\n\s*\n|(?=^### )', raw_text.strip(), flags=re.MULTILINE)
docs = [doc.strip() for doc in docs if len(doc.strip()) > 40]

# === Embed all docs ===
embeddings = model.encode(docs)
dimension = embeddings.shape[1]

# === Build FAISS index ===
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))
doc_store = {i: docs[i] for i in range(len(docs))}

def get_top_k_docs(query, k=3):
    query_vec = model.encode([query])
    _, indices = index.search(query_vec, k)

    # Convert np.int64 to int and filter out -1 (invalid result)
    valid_indices = [int(i) for i in indices[0] if int(i) in doc_store]
    return [doc_store[i] for i in valid_indices]
