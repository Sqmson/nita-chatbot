from flask import Flask, render_template, request, jsonify
# from chatbot_engine import process
import requests, os
from dotenv import load_dotenv
from datetime import datetime
from vector import get_top_k_docs
import traceback

load_dotenv()
API_KEY = os.getenv("API_KEY")
app = Flask(__name__)

# Load document once
with open("rag_docs.txt") as f:
    knowledge_base = f.read()

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    question = data["message"]
    response = process(knowledge_base, question)
    if response:
        return jsonify({"answer": response})
    else:
        return jsonify({"answer": "I'm not sure about that."})

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.json.get("message", "").strip()

    try:
        # === RAG context ===
        retrieved_chunks = get_top_k_docs(user_message)
        retrieved_chunks = get_top_k_docs(user_message)
        if not retrieved_chunks or all(len(c.strip()) < 40 for c in retrieved_chunks):
            return jsonify({"reply": "⚠️ I couldn't find enough relevant information in the document."})

        context = "\n".join(f"- {chunk}" for chunk in retrieved_chunks)

        # === Prompt ===
        full_prompt = (
            "You are a knowledgeable assistant. Provide helpful, clear, and well-structured responses "
            "using **only** the context below. Be precise but informative. Use markdown for formatting "
            "and include bullet points, headings, and examples where useful.\n\n"
            f"Context:\n{context}\n\n"
            f"User: {user_message}\n"
            "Answer:"
        )

        # === NVIDIA API call ===
        url = "https://integrate.api.nvidia.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Accept": "application/json"
        }
        payload = {
            "model": "google/gemma-3n-e4b-it",
            "messages": [
                {"role": "system", "content": full_prompt},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": 512,
            "temperature": 0.3,
            "top_p": 0.9,
            "stream": False
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})

    except Exception as e:
        print("❌ ERROR:", str(e))
        traceback.print_exc()  # This will print full traceback to the console
        return jsonify({"reply": "⚠️ Sorry, an internal error occurred."}), 500


@app.route("/initial", methods=["GET"])
def initial():
    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"
    intro = f"{greeting}! I'm here to assist you with anything related to the document. Ask your question below."
    return jsonify({
        "reply": intro,
        "suggestions": ["What is UGhub?", "Who is responsible for cybersecurity?", "Explain G-Cloud in Uganda"]
    })

if __name__ == "__main__":
    app.run(debug=True)
