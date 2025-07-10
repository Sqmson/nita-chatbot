import os
import faiss
import json
import numpy as np
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import requests
from datetime import datetime

# === Load API key ===
load_dotenv()
API_KEY = os.getenv("API_KEY")

# === Setup Flask ===
app = Flask(__name__)

# === Embedding model ===
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
embedding_dim = 384

# === Load & Chunk documents ===
chunks = []
chunk_sources = []

# Load FAQs (later extend with PDFs/DB)
with open("faq.json", "r") as f:
    faq_data = json.load(f)
    for item in faq_data:
        q, a = item["q"], item["a"]
        chunk = f"Q: {q}\nA: {a}"
        chunks.append(chunk)
        chunk_sources.append(q)

# === Create FAISS index ===
index = faiss.IndexFlatL2(embedding_dim)
chunk_embeddings = embedding_model.encode(chunks)
index.add(np.array(chunk_embeddings))

# === Helper: Retrieve top-k similar chunks ===
def retrieve_context(query, k=5):
    query_embedding = embedding_model.encode([query])
    D, I = index.search(np.array(query_embedding), k)
    return [chunks[i] for i in I[0]]

# === Flask Routes ===
@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.json.get("message", "")

    # Greeting message
    if user_message.strip().lower() in ["", "hello", "hi", "start"]:
        hour = datetime.now().hour
        if hour < 12:
            greeting = "Good morning"
        elif hour < 17:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"

        suggestions = [
            "What is NITA-U?",
            "NITA-U services",
            "What is UGhub?",
            "How to connect to NBI?",
            "Who runs CERT-UG?"
        ]
        return jsonify({
            "reply": f"{greeting}! I'm your friendly AI assistant. Ask me anything about NITA-U or choose from below:",
            "suggestions": suggestions
        })

    # Get relevant chunks
    relevant_context = retrieve_context(user_message)
    context_text = "\n\n".join(relevant_context)

    # Build prompt
    prompt = f"""
You are a helpful AI assistant for the National Information Technology Authority Uganda (NITA-U).
Use the following information to answer the question clearly and professionally.

Context:
{context_text}

User: {user_message}
"""

    # Call NVIDIA's API (Gemma)
    invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json"
    }
    payload = {
        "model": "google/gemma-3n-e4b-it",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 512,
        "temperature": 0.3,
        "top_p": 0.9,
        "stream": False
    }

    res = requests.post(invoke_url, headers=headers, json=payload)
    data = res.json()
    reply = data["choices"][0]["message"]["content"]
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)
