# Autonomous Data Analyst Agent (ADA)

A secure, autonomous agent that accepts CSV data uploads, processes natural language questions, generates and executes pandas code in an isolated sandbox, and provides downloadable analysis reports.

## 🎯 Features

- **CSV Upload & Analysis**: Upload datasets and ask questions in natural language
- **Safe Code Generation**: LLM-generated pandas code with AST-based validation
- **Sandboxed Execution**: Docker-based isolated environment with no network access
- **Report Generation**: Automatic HTML reports with code, results, and visualizations
- **Security First**: Multiple layers of validation and isolation

## 🏗️ Architecture

```
├── backend/          # FastAPI backend server
│   ├── app/
│   │   ├── main.py           # FastAPI entrypoint
│   │   ├── api.py            # API endpoints
│   │   ├── schemas.py        # Pydantic models
│   │   ├── llm_client.py     # LLM integration (placeholder + real)
│   │   ├── safety.py         # AST-based code validator
│   │   ├── sandbox_runner.py # Docker sandbox executor
│   │   ├── report_generator.py # Report generation
│   │   └── utils.py          # Helper functions
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/         # Streamlit UI
│   ├── streamlit_app.py
│   ├── requirements.txt
│   └── Dockerfile
├── sandbox/          # Isolated execution environment
│   ├── Dockerfile.sandbox
│   └── provision.sh
├── prompts/          # LLM prompt templates
│   └── templates.md
├── data/             # Data storage
│   ├── uploads/      # Uploaded CSV files
│   ├── tasks/        # Task execution results
│   └── sample_orders.csv
├── tests/            # Unit tests
│   ├── test_safety.py
│   └── test_api_smoke.py
└── docker-compose.yml
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (or use Python 3.12 in venv - see below)
- Git

> **📌 Using Python 3.8?** You can use a virtual environment with Python 3.11/3.12 for this project only! See **[SETUP_VENV.md](SETUP_VENV.md)** for detailed instructions or run `.\setup-venv.ps1`

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd agent-ai
cp .env.example .env
```

### 2. Build the Sandbox Image

```bash
# Option 1: Using the provision script
bash sandbox/provision.sh

# Option 2: Manual build
docker build -f sandbox/Dockerfile.sandbox -t ada-sandbox:latest sandbox/
```

### 3. Run with Docker Compose

```bash
# Start all services
docker-compose up --build

# Access the application
# - Frontend: http://localhost:8501
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### 4. Run Locally (Development)

#### Backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend:
```bash
cd frontend
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 🔑 LLM Integration

### Using Placeholder (Default)

The app runs out-of-the-box with a placeholder LLM client that returns safe, example pandas code. No API key required.

### Integrating Gemini

1. Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Add to `.env`:
   ```
   GEMINI_API_KEY=your_actual_key_here
   ```
3. The `llm_client.py` will automatically use Gemini when the key is present

### Integrating OpenAI

1. Get API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Add to `.env`:
   ```
   OPENAI_API_KEY=your_actual_key_here
   ```
3. Modify `llm_client.py` to use OpenAI client (see code comments)

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend/app tests/

# Run specific test file
pytest tests/test_safety.py -v
```

## 🔒 Security Features

### 1. AST-Based Code Validation
- Blocks dangerous functions: `eval`, `exec`, `compile`, `open`, `__import__`
- Whitelist-only imports: pandas, numpy, matplotlib
- Prevents OS/subprocess/socket access
- Rejects dunder method abuse

### 2. Docker Sandbox
- **No network access** (`--network none`)
- **Resource limits**: 256MB RAM, 0.5 CPU
- **Read-only dataset mount**
- **Timeout enforcement** (30s default)
- Separate output directory

### 3. Fallback Safety (rlimit)
When Docker unavailable, uses Python `resource` module:
- ⚠️ **WARNING**: Less secure than Docker
- Only for local development
- Sets CPU, memory, and file size limits

## 📊 Usage Example

1. **Upload CSV**: Upload `data/sample_orders.csv` or your own dataset
2. **Ask Question**: "What are the top 5 products by revenue?"
3. **Review Code**: See the generated pandas code
4. **Execute**: Run in sandbox and view results
5. **Download Report**: Get HTML report with analysis

## 📝 API Endpoints

- `POST /api/upload` - Upload CSV dataset
- `POST /api/ask` - Submit analysis question
- `GET /api/status/{task_id}` - Check task status
- `GET /api/report/{task_id}` - Download HTML report
- `GET /health` - Health check

## ⚠️ Important Notes

### For Production Deployment:

1. **Never expose publicly without hardening**
2. **Add authentication** (OAuth, API keys)
3. **Use secrets manager** (not .env files)
4. **Implement rate limiting**
5. **Add audit logging**
6. **Enhanced validators** (semantic analysis)
7. **Kubernetes + gVisor** for better isolation
8. **Review all generated code** before execution

### Current Limitations:

- Placeholder LLM returns fixed code (until you add real API key)
- Basic validator (AST only, no semantic analysis)
- No multi-user support
- No persistent database
- Limited error handling for edge cases

## 🛠️ Development

### Project Structure Philosophy

- **Modularity**: Each component is independent and testable
- **Security Layers**: Validation → Sandbox → Resource Limits
- **Clear Contracts**: Pydantic schemas for all data
- **Fail-Safe**: Default to safe/placeholder behavior

### Adding New Features

1. Create feature branch: `git checkout -b feature/your-feature`
2. Implement with tests
3. Update README if user-facing
4. Submit PR with clear description

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Write tests for new code
4. Ensure CI passes
5. Submit pull request

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- FastAPI for the backend framework
- Streamlit for rapid UI development
- Docker for containerization and sandboxing

## 📞 Support

For issues and questions:
- GitHub Issues: [Project Issues]
- Documentation: `docs/` folder
- Security concerns: See SECURITY.md

---

**Built with security and extensibility in mind** 🔒🚀
