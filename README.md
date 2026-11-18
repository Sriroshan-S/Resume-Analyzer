## Member 3 Contribution: AI Integration & Testing
- **Prompt Engineering:** Designed structured prompts for Gemini API to extract 4 concise resume improvement suggestions, professional summaries, and interview questions.
- **AI Analyzer (`utils/ai_analyzer.py`):** Integrated Gemini API with safe fallback handling to ensure the application never crashes during offline tests or viva.
- **Testing (`tests/test_ai_analyzer.py`):** Written comprehensive Pytest test cases to validate output types, score ranges, and error handling.
- **CI/CD:** Configured GitHub Actions workflow (`.python.yml`) to automatically run tests on every push and pull request.