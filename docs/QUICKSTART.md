# Quick Start Guide

This guide will get you running the Autonomous Data Analyst Agent in under 5 minutes!

## Prerequisites

- Docker Desktop installed and running
- Python 3.11+ (for local development)
- Git

## 🚀 Quick Start with Docker

### 1. Build the Sandbox Image

```powershell
# Windows PowerShell
docker build -f sandbox/Dockerfile.sandbox -t ada-sandbox:latest sandbox/
```

### 2. Start the Application

```powershell
docker-compose up --build
```

Wait for services to start (~30 seconds).

### 3. Open the Application

- **Frontend**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

## 📝 First Analysis

### Step 1: Upload Sample Data

1. Go to http://localhost:8501
2. Click "Upload Data" tab
3. Upload `data/sample_orders.csv`
4. Click "Upload Dataset"

### Step 2: Ask a Question

1. Switch to "Ask Question" tab
2. Enter: "What are the top 5 products by sales?"
3. Click "Generate & Run"

### Step 3: View Results

1. Go to "View Results" tab
2. Wait for execution to complete (~5 seconds)
3. See generated code, output, and results!

## 🛠️ Local Development (Without Docker)

### 1. Set Up Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2. Set Up Frontend (New Terminal)

```powershell
cd frontend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

**Note:** Without Docker, code runs with rlimit fallback (less secure).

## 🔑 Adding Real LLM (Optional)

### For Gemini:

1. Get API key from https://makersuite.google.com/app/apikey
2. Create `.env` file:
   ```
   GEMINI_API_KEY=your_actual_key_here
   ```
3. Restart services

### For OpenAI:

1. Get API key from https://platform.openai.com/api-keys
2. Add to `.env`:
   ```
   OPENAI_API_KEY=your_actual_key_here
   ```
3. Restart services

## 🧪 Running Tests

```powershell
# Install test dependencies
cd tests
pip install -r requirements.txt

# Run all tests
pytest -v

# Run with coverage
pytest --cov=backend/app
```

## 📊 Example Questions to Try

- "What are the top 5 products by revenue?"
- "Show monthly sales trends"
- "What is the average order value by customer segment?"
- "Which category has the most orders?"
- "Calculate total sales by month"

## 🐛 Troubleshooting

### Backend won't start
- Check if port 8000 is available
- Verify Python 3.11+ is installed
- Check `backend/requirements.txt` is installed

### Frontend won't connect
- Ensure backend is running first
- Check BACKEND_URL in frontend (default: http://localhost:8000)

### Sandbox image not found
```powershell
docker build -f sandbox/Dockerfile.sandbox -t ada-sandbox:latest sandbox/
```

### Docker daemon not running
- Start Docker Desktop
- Wait for it to fully start
- Try command again

## 🎉 Next Steps

- Read full [README.md](../README.md)
- Check [DEVELOPMENT.md](DEVELOPMENT.md) for advanced topics
- Review [SECURITY.md](../SECURITY.md) before production use
- Customize prompts in `prompts/templates.md`

## 💡 Tips

- Use placeholder mode first (no API key needed)
- Review generated code before execution
- Start with simple questions
- Check logs if something fails
- Sample data in `data/sample_orders.csv`

## 📞 Need Help?

- Check [DEVELOPMENT.md](DEVELOPMENT.md)
- Open GitHub Issue
- Review API docs at http://localhost:8000/docs

---

**Happy Analyzing! 📊🚀**
