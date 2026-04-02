# Development Guide

## Project Structure

```
agent-ai/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py          # Application entry
│   │   ├── api.py           # API endpoints
│   │   ├── schemas.py       # Pydantic models
│   │   ├── llm_client.py    # LLM integration
│   │   ├── safety.py        # Code validator
│   │   ├── sandbox_runner.py # Sandbox executor
│   │   ├── report_generator.py # Report builder
│   │   └── utils.py         # Helper functions
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/            # Streamlit UI
│   ├── streamlit_app.py
│   ├── requirements.txt
│   └── Dockerfile
├── sandbox/             # Isolated executor
│   ├── Dockerfile.sandbox
│   └── provision.sh
├── tests/               # Unit and integration tests
│   ├── test_safety.py
│   └── test_api_smoke.py
├── prompts/             # LLM prompts
│   └── templates.md
├── data/                # Data storage
│   ├── uploads/         # User datasets
│   ├── tasks/           # Task results
│   └── sample_orders.csv
└── docs/                # Documentation
```

## Setting Up Development Environment

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd agent-ai
```

### 2. Create Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt

# Tests
cd ../tests
pip install -r requirements.txt

# Frontend
cd ../frontend
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Build Sandbox Image

```bash
# Windows (PowerShell)
docker build -f sandbox/Dockerfile.sandbox -t ada-sandbox:latest sandbox/

# Linux/Mac (or use provision.sh)
bash sandbox/provision.sh
```

## Running Locally

### Option 1: Docker Compose (Recommended)

```bash
docker-compose up --build
```

Access:
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Separate Processes

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
streamlit run streamlit_app.py
```

## Running Tests

### All Tests

```bash
pytest tests/ -v
```

### Specific Test File

```bash
pytest tests/test_safety.py -v
```

### With Coverage

```bash
pytest tests/ --cov=backend/app --cov-report=html
```

View coverage report: `htmlcov/index.html`

## Code Quality

### Linting

```bash
# Install tools
pip install flake8 black isort

# Run flake8
flake8 backend/app --max-line-length=120

# Format with black
black backend/app

# Sort imports
isort backend/app
```

### Type Checking

```bash
pip install mypy
mypy backend/app
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Write code following style guidelines
- Add docstrings to functions
- Update tests for new functionality

### 3. Test Your Changes

```bash
# Run tests
pytest tests/ -v

# Check code quality
flake8 backend/app
black --check backend/app
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: description of your feature"
```

Commit message format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `test:` - Tests
- `refactor:` - Code refactoring
- `chore:` - Maintenance

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Create pull request on GitHub.

## Adding New Features

### Adding New LLM Provider

Edit `backend/app/llm_client.py`:

```python
def _generate_with_new_provider(question, dataset_info, context):
    # Your implementation
    pass

# Add to generate_code_for_question()
if new_provider_key:
    return _generate_with_new_provider(...)
```

### Adding New Safety Check

Edit `backend/app/safety.py`:

```python
def new_safety_check(code: str) -> Tuple[bool, str]:
    # Your check logic
    pass

# Add to full_validation()
```

Add tests in `tests/test_safety.py`.

### Adding New API Endpoint

Edit `backend/app/api.py`:

```python
@router.get("/your-endpoint")
async def your_handler():
    # Implementation
    pass
```

Add schema in `backend/app/schemas.py`.

## Debugging

### Backend Debugging

Add breakpoints or print statements:

```python
import logging
logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

### Frontend Debugging

Use Streamlit's debug mode:

```python
st.write("Debug:", variable)
```

### Docker Debugging

View logs:

```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

Enter container:

```bash
docker exec -it ada-backend bash
```

## Common Issues

### Issue: Docker sandbox image not found

**Solution:**
```bash
docker build -f sandbox/Dockerfile.sandbox -t ada-sandbox:latest sandbox/
```

### Issue: Import errors in tests

**Solution:** Ensure you're running from project root and tests are installed:
```bash
cd tests
pip install -r requirements.txt
```

### Issue: Port already in use

**Solution:** Kill process or use different port:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Linux/Mac
lsof -ti:8000 | xargs kill
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Ensure CI passes
5. Submit pull request

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [Docker Docs](https://docs.docker.com/)
- [Pandas Docs](https://pandas.pydata.org/)

## Getting Help

- GitHub Issues: Report bugs
- GitHub Discussions: Ask questions
- Documentation: Check `docs/` folder
