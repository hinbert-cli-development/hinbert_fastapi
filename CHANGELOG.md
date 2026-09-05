# Contributing to hinbert-fastapi

Thank you for considering contributing! 🎉

## How to Contribute

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature`
3. **Make your changes**
4. **Run quality checks**: `ruff check . && black . && pytest`
5. **Commit changes**: `git commit -m "feat: add your feature"`
6. **Push**: `git push origin feature/your-feature`
7. **Open a Pull Request**

## Development Setup

```bash
# Clone
git clone https://github.com/HassanMalik-Al/hinbert_fastapi.git
cd hinbert_fastapi

# Setup
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

# Run tests
pytest -v --cov=app --cov-fail-under=80