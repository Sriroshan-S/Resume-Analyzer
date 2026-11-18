# AI Resume Analyzer & Career Coach

A Flask web application where users upload a PDF resume and receive a score with improvement suggestions.

## Features

- Upload a resume in PDF format (max 5 MB)
- File validation for type and size
- Result page with score and suggestions

## Tech Stack

- Python 3
- Flask
- HTML and CSS
- pytest
- Deployed on Render

## Project Structure

    resume-analyzer/
    ├── app.py              # Flask routes
    ├── requirements.txt    # Python dependencies
    ├── templates/          # HTML pages
    ├── static/             # CSS
    ├── utils/              # Analysis logic
    ├── tests/              # Automated tests
    └── README.md

## How to Run Locally

1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Run the app: `python app.py`
5. Open http://127.0.0.1:5000

## How to Run Tests

    python -m pytest

## Team

- Member 1: Flask backend, frontend, deployment
- Member 2: (Resume Parser,ATS score,Carrer Recommendation)
- Member 3: (AI,Prompt Engineering,Testing,Github Actions)
