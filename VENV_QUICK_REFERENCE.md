# ✅ VENV SETUP COMPLETE - Quick Reference

## Your Setup
- **System Python**: 3.8.10 (for ML projects) ✅
- **This Project**: Python 3.12.3 in venv ✅
- **Status**: Virtual environment created and ready!

## 🚀 Quick Start Commands

### Activate Virtual Environment (Always do this first!)
```powershell
.\venv\Scripts\activate
```

You'll see `(venv)` in your prompt when active.

### Option 1: Run Without Docker (Recommended for Development)

**Terminal 1 - Backend:**
```powershell
# Activate venv
.\venv\Scripts\activate

# Install dependencies (first time only)
cd backend
pip install -r requirements.txt

# Run backend
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```powershell
# Activate venv
.\venv\Scripts\activate

# Install dependencies (first time only)
cd frontend
pip install -r requirements.txt

# Run frontend
streamlit run streamlit_app.py
```

### Option 2: Run With Docker (No venv needed for runtime)

```powershell
# Build sandbox (one time)
docker build -f sandbox/Dockerfile.sandbox -t ada-sandbox:latest sandbox/

# Run everything
docker-compose up --build
```

### Run Tests
```powershell
# Activate venv
.\venv\Scripts\activate

# Install test dependencies (first time only)
cd tests
pip install -r requirements.txt

# Run tests
pytest -v
```

### Deactivate When Done
```powershell
deactivate
```

## 📝 First Time Setup (Do Once)

```powershell
# 1. Activate venv
.\venv\Scripts\activate

# 2. Install all dependencies
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
pip install -r tests/requirements.txt

# 3. Build sandbox (if using Docker)
docker build -f sandbox/Dockerfile.sandbox -t ada-sandbox:latest sandbox/

# 4. Create .env file
copy .env.example .env
```

## 🎯 First Analysis

1. **Start backend** (Terminal 1):
   ```powershell
   .\venv\Scripts\activate
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Start frontend** (Terminal 2):
   ```powershell
   .\venv\Scripts\activate
   cd frontend
   streamlit run streamlit_app.py
   ```

3. **Open browser**: http://localhost:8501

4. **Upload**: `data/sample_orders.csv`

5. **Ask**: "What are the top 5 products by sales?"

6. **View results!** 🎉

## 🔄 Switching Between Projects

### For This Project (Python 3.12)
```powershell
cd "E:\SANJAY PC OFFICIAL FILES\SANJAY pc\SEMESTER 5\agent ai"
.\venv\Scripts\activate
python --version  # Shows 3.12.3
```

### For ML Projects (Python 3.8)
```powershell
deactivate  # Exit this venv first
cd your-ml-project
python --version  # Shows 3.8.10
# Or activate your ML project's venv
```

## 🛠️ Useful Commands

```powershell
# Check active Python version
python --version

# Check installed packages
pip list

# Install new package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt

# Check if venv is active (should see (venv) in prompt)
# If not, run: .\venv\Scripts\activate
```

## 📊 What You Have Now

- ✅ Python 3.12 virtual environment
- ✅ Isolated from your system Python 3.8
- ✅ Ready to install project dependencies
- ✅ Can run backend, frontend, and tests
- ✅ Compatible with all project requirements

## 🐛 Troubleshooting

### "python" still shows 3.8
**Fix**: Make sure you activated the venv:
```powershell
.\venv\Scripts\activate
# You should see (venv) in your prompt
```

### Can't activate venv
**Fix**: Run from project root:
```powershell
cd "E:\SANJAY PC OFFICIAL FILES\SANJAY pc\SEMESTER 5\agent ai"
.\venv\Scripts\activate
```

### Module not found error
**Fix**: Install dependencies:
```powershell
.\venv\Scripts\activate
pip install -r backend/requirements.txt
```

### Want to start fresh
**Fix**: Delete and recreate venv:
```powershell
deactivate
Remove-Item -Recurse -Force venv
py -3.12 -m venv venv
.\venv\Scripts\activate
```

## 💡 Pro Tips

- **Always activate venv** before running project commands
- **Each terminal needs activation** if you open new ones
- **Venv is local** - won't affect other projects
- **Can delete venv folder** anytime and recreate
- **Don't commit venv** - it's already in .gitignore

## 📚 Documentation

- **Setup Guide**: `SETUP_VENV.md` (detailed version)
- **Quick Start**: `docs/QUICKSTART.md`
- **Development**: `docs/DEVELOPMENT.md`
- **Main README**: `README.md`

---

## ⚡ READY TO GO!

Your venv is set up with Python 3.12. Your system Python 3.8 is untouched.

**Next step**: Run the automated setup script:
```powershell
.\setup-venv.ps1
```

Or start manually with the commands above! 🚀
