from flask import Flask, request, jsonify
from flask_cors import CORS
from retrieve import retrieve_best_match
import os

# To use a real AI model, install: pip install google-generativeai
# Get a free key at https://aistudio.google.com/app/apikey
USE_AI_MODEL = True

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if USE_AI_MODEL:
    if not GEMINI_API_KEY:
        raise RuntimeError("Set GEMINI_API_KEY environment variable before running.")
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")


app = Flask(__name__)
CORS(app)  # allows the React frontend (different port) to call this API


def generate_answer(question, context):
    """
    Given a question and the retrieved context, generate an answer.
    If USE_AI_MODEL is False, returns a simple template answer so you
    can test the full flow without needing an API key yet.
    """
    if not USE_AI_MODEL:
        return f"[Demo mode - no AI call made] Based on the retrieved section, here is the relevant text: {context}"

    prompt = f"Answer the question using ONLY this context. Be concise.\n\nContext: {context}\n\nQuestion: {question}"
    response = model.generate_content(prompt)
    return response.text


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Question is required"}), 400

    # Step 1: Retrieve the most relevant document chunk
    result = retrieve_best_match(question)

    # Step 2: Decide - confident match, or abstain?
    if not result["found"]:
        return jsonify({
            "answer": "I could not find a confident answer to this in the available documents.",
            "citation": None,
            "confidence_score": result["score"]
        })

    # Step 3: Generate the answer using the retrieved context
    answer_text = generate_answer(question, result["content"])

    return jsonify({
        "answer": answer_text,
        "citation": f"{result['doc_name']} — {result['section']}",
        "confidence_score": result["score"]
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
