from flask import Flask, render_template, request
import process_incoming as rag

app = Flask(__name__)
rag.init_database()


@app.route("/", methods=["GET", "POST"])
def home():
    answer = None
    query = None
    error = None

    if request.method == "POST":
        query = request.form.get("query", "").strip()

        try:
            answer = rag.get_answer(query)
        except Exception as exc:
            error = (
                "The RAG engine could not generate a response. "
                "Make sure Ollama is running on http://localhost:11434."
            )
            answer = str(exc)
            if query:
                rag.save_interaction(query, "", answer, "error")

    return render_template(
        "index.html",
        answer=answer,
        user_query=query,
        error=error,
    )


if __name__ == "__main__":
    print("Starting Flask server at http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
