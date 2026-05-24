# Contributing to RAG Chatbot

Thank you for your interest in contributing to the RAG Chatbot project! We welcome contributions from developers of all skill levels. By contributing to this repository, you help make document-based conversational AI more accessible to everyone.

---

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please report any unacceptable behavior to the project maintainers.

---

## How Can I Contribute?

### 1. Reporting Bugs
- Search the issue tracker to ensure the bug hasn't already been reported.
- If you can't find an existing issue, open a new one using the **Bug Report** template.
- Include clear steps to reproduce the issue, along with any relevant error logs, configurations, and details about your operating system.

### 2. Suggesting Enhancements
- Open an issue using the **Feature Request** template.
- Describe the feature in detail, why it would be valuable, and how it fits into the current RAG architecture.

### 3. Submitting Pull Requests
1. **Fork the Repository**: Create your own copy of the codebase.
2. **Create a Branch**: Create a feature branch off the main branch (e.g., `git checkout -b feature/awesome-new-capability`).
3. **Write Code & Tests**: Make your changes, maintaining the coding standards.
4. **Run Code Linters**: Format python files using `black`, `flake8`, or similar formatting helpers.
5. **Commit Changes**: Write clear, descriptive commit messages.
6. **Push and Submit**: Push to your fork and submit a Pull Request (PR) against our `main` branch. Use the provided PR Template.

---

## Local Development Setup

To set up the project locally:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/abubakarshahid16/Rag-chatbot.git
   cd Rag-chatbot
   ```

2. **Backend Setup**:
   ```bash
   cd Backend
   python -m venv venv
   # Windows: venv\Scripts\activate
   # Unix: source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**:
   ```bash
   cd ../Frontend
   python -m venv venv
   # Windows: venv\Scripts\activate
   # Unix: source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Verify Environment Variables**:
   Ensure you copy `Backend/.env.example` to `Backend/.env` and insert your API keys for testing.
