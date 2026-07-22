# Contributing to AI Campus Placement System

## Development Setup

```bash
# Clone repository
git clone https://github.com/campus-placement-ai/campus-placement-ai.git
cd campus-placement-ai

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt
pip install -r requirements.txt[dev]   # via pyproject.toml

# Download spaCy model
python -m spacy download en_core_web_sm

# Initialize system (generate data + train models)
python initialize.py
```

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=src

# Run specific test file
python -m pytest tests/test_models.py -v
```

## Code Style

- **Formatter**: Black (line length 120)
- **Import sorting**: isort (profile: black)
- **Linting**: flake8 (max-line length 120, ignore E501,W503)
- **Type hints**: Encouraged but not enforced

```bash
# Format code
black src/ tests/ app.py config/
isort src/ tests/ app.py config/

# Lint
flake8 src/ tests/ app.py config/
```

## Project Structure

```
CampusPlacementAI/
├── app.py                  # Main Streamlit application
├── initialize.py           # System initialization
├── config/                 # Configuration dataclasses
├── src/
│   ├── ml/                 # ML models and scoring
│   ├── nlp/                # NLP processing
│   ├── utils/              # Utilities (email, reports, helpers)
│   ├── database/           # SQLAlchemy models + DB manager
│   ├── api/                # FastAPI REST endpoints (optional)
│   └── dashboard/          # Modular Streamlit page components
├── tests/                  # Unit and integration tests
├── data/                   # Datasets and DB schema
├── docs/                   # Documentation
├── templates/              # HTML email templates
└── static/                 # CSS and images
```

## Adding New Features

1. Create feature code in the appropriate `src/` subdirectory
2. Add unit tests in `tests/`
3. Add integration tests in `tests/test_integration.py`
4. Update documentation if needed
5. Run full test suite before submitting

## Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit with descriptive message
4. Push to your fork
5. Open a Pull Request
