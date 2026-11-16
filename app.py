import os
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from utils.analyzer import analyze_resume

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    if "resume" not in request.files:
        return "No file part in the request", 400

    file = request.files["resume"]

    if file.filename == "":
        return "No file selected", 400

    if not allowed_file(file.filename):
        return "Only PDF files are allowed", 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

        # Placeholder data. Your teammates' AI code will replace this later.
    score = 40
    suggestions = [
        "Add a short professional summary at the top.",
        "List your projects with the technologies used.",
        "Include measurable achievements.",
        "Add links to GitHub and LinkedIn.",
    ]

    result = analyze_resume(filepath)

    return render_template(
        "result.html",
        filename=filename,
        score=result["score"],
        suggestions=result["suggestions"],
    )

if __name__ == "__main__":
    app.run(debug=True)