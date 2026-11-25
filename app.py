import os
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from utils.ai_analyzer import analyze_resume
from utils.analyzer import analyze_resume as local_analyze

app = Flask(__name__)

# Folder to temporarily store uploaded resumes
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    if "resume" not in request.files:
        return "No file uploaded", 400

    file = request.files["resume"]

    if file.filename == "":
        return "No file selected", 400

    if not file.filename.lower().endswith(".pdf"):
        return "Only PDF files are allowed", 400

    # Save the uploaded PDF safely
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    careers = []
    try:
        # Call your teammate's analyzer function
        result = analyze_resume(filepath) or {}
        # Career matches from our own resume-processing code
        try:
            careers = local_analyze(filepath)["careers"]
        except Exception:
            careers = []
    finally:
        # Remove the temporary uploaded file after analysis (even if it fails)
        if os.path.exists(filepath):
            os.remove(filepath)

    # Pass every required variable to result.html
    return render_template(
        "result.html",
        filename=filename,
        score=result.get("score", 0),
        suggestions=result.get("suggestions", []),
        summary=result.get("summary", ""),
        roadmap=result.get("roadmap", []),
        interview_questions=result.get("interview_questions", []),
        careers=careers,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
