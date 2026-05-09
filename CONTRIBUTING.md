# Contributing to Customer Support Chatbot

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone <your-fork-url>`
3. Create a virtual environment: `python -m venv .venv`
4. Activate virtual environment:
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Copy `.env.example` to `.env` and configure as needed

## Development Workflow

1. Create a new branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Run tests: `pytest tests/`
4. Commit your changes: `git commit -m "Description of changes"`
5. Push to your fork: `git push origin feature/your-feature-name`
6. Create a Pull Request

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small
- Add type hints where appropriate

## Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Run tests with: `pytest tests/`
- Check coverage with: `pytest tests/ --cov=app`

## Commit Messages

- Use clear and descriptive commit messages
- Start with a verb in present tense (Add, Fix, Update, etc.)
- Keep the first line under 50 characters
- Add detailed description if needed

Examples:
- `Add product search functionality`
- `Fix order status query bug`
- `Update README with new installation steps`

## Pull Request Process

1. Update README.md if you're adding new features
2. Ensure all tests pass
3. Update documentation as needed
4. Request review from maintainers
5. Address any feedback

## Questions?

Feel free to open an issue for any questions or concerns.
