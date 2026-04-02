# 🚀 GET STARTED NOW - Quick Commands

## Option 1: Automated Setup (Recommended)

### Windows (PowerShell)
```powershell
.\setup.ps1
```

### Linux/Mac
```bash
chmod +x setup.sh
./setup.sh
```

## Option 2: Manual Setup

### Step 1: Build Sandbox Image
```powershell
# Windows PowerShell
docker build -f sandbox/Dockerfile.sandbox -t ada-sandbox:latest sandbox/

# Linux/Mac
bash sandbox/provision.sh
```

### Step 2: Create Environment File
```powershell
# Copy template
copy .env.example .env

# Edit .env to add your API keys (optional for now)
```

### Step 3: Start Application
```powershell
docker-compose up --build
```

### Step 4: Access Application
- **Frontend**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **Backend**: http://localhost:8000

## 📝 First Analysis

1. Go to http://localhost:8501
2. Upload `data/sample_orders.csv`
3. Ask: "What are the top 5 products by sales?"
4. View results!

## 🧪 Run Tests

```powershell
# Install test dependencies
cd tests
pip install -r requirements.txt

# Run tests
pytest -v

# Back to root
cd ..
```

## 🔑 Add Real LLM (Optional)

### Gemini
1. Get key: https://makersuite.google.com/app/apikey
2. Edit `.env`:
   ```
   GEMINI_API_KEY=your_actual_key
   ```
3. Restart: `docker-compose restart`

### OpenAI
1. Get key: https://platform.openai.com/api-keys
2. Edit `.env`:
   ```
   OPENAI_API_KEY=your_actual_key
   ```
3. Restart: `docker-compose restart`

## 📚 Documentation

- **Quick Start**: `docs/QUICKSTART.md`
- **Development**: `docs/DEVELOPMENT.md`
- **Security**: `SECURITY.md`
- **Full README**: `README.md`
- **Summary**: `PROJECT_SUMMARY.md`

## 🐛 Troubleshooting

### Docker not found
- Install Docker Desktop
- Ensure it's running

### Port already in use
```powershell
# Windows - find and kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Linux/Mac
lsof -ti:8000 | xargs kill
```

### Sandbox image not found
```powershell
docker build -f sandbox/Dockerfile.sandbox -t ada-sandbox:latest sandbox/
```

## 🎯 What to Do Next

1. ✅ Run the application
2. ✅ Try sample analysis
3. ✅ Review generated code
4. ✅ Run tests
5. ✅ Read documentation
6. ✅ Customize for your needs
7. ✅ Add real LLM integration

## 🎉 You're All Set!

The project is complete and ready to run. Start with the automated setup script and explore!

**Need help?** Check the documentation or open a GitHub issue.

---

**Quick Links:**
- Frontend: http://localhost:8501
- API Docs: http://localhost:8000/docs
- Sample Data: `data/sample_orders.csv`
