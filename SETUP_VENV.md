# Setup with Python 3.12 Virtual Environment

## Your Situation
- System Python: 3.8.10 (for ML projects) ✅
- Available: Python 3.12 (for this project) ✅
- Solution: Use venv with Python 3.12 for this project only

## Quick Setup (Recommended)

### Step 1: Create Virtual Environment with Python 3.12

```powershell
# Create venv using Python 3.12
py -3.12 -m venv venv

# Activate the virtual environment
.\venv\Scripts\activate

# Verify Python version (should show 3.12)
python --version
```

### Step 2: Install Backend Dependencies

```powershell
# Install backend requirements
cd backend
pip install -r requirements.txt
cd ..

# Install test requirements
cd tests
pip install -r requirements.txt
cd ..
```

### Step 3: Build Sandbox Docker Image

```powershell
docker build -f sandbox/Dockerfile.sandbox -t ada-sandbox:latest sandbox/
```

### Step 4: Run the Application

#### Option A: Run Backend Only (Terminal 1)
```powershell
# Make sure venv is activated
.\venv\Scripts\activate

cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Option B: Run Frontend (Terminal 2)
```powershell
# Open new terminal, activate venv
.\venv\Scripts\activate

cd frontend
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Step 5: Access the Application
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Alternative: Use Docker (No venv needed)

If you prefer Docker (doesn't affect your system Python):

```powershell
# Just build and run with Docker Compose
docker-compose up --build
```

This completely isolates the project and uses Python 3.11 inside containers.

## Verify Your Setup

```powershell
# Activate venv
.\venv\Scripts\activate

# Check Python version (should be 3.12)
python --version

# Check installed packages
pip list

# Run tests
cd tests
pytest -v
```

## Switching Between Projects

### For This Project (Python 3.12)
```powershell
cd "E:\SANJAY PC OFFICIAL FILES\SANJAY pc\SEMESTER 5\agent ai"
.\venv\Scripts\activate
python --version  # Shows 3.12
```

### For ML Projects (Python 3.8)
```powershell
deactivate  # Exit this venv first
cd your-ml-project
# Use your ML project's venv or system Python 3.8
```

## Troubleshooting

### Issue: "python" still shows 3.8 after activating venv
**Solution:** Make sure you see `(venv)` in your prompt. If not:
```powershell
# Deactivate and reactivate
deactivate
.\venv\Scripts\activate
```

### Issue: pip install fails
**Solution:** Upgrade pip first:
```powershell
python -m pip install --upgrade pip
```

### Issue: Can't find py launcher
**Solution:** Use full path:
```powershell
C:\Users\YourUsername\AppData\Local\Programs\Python\Python312\python.exe -m venv venv
```

## Benefits of This Approach

✅ **Isolated**: Project has its own Python 3.12 + dependencies
✅ **No Conflicts**: Your ML projects stay on Python 3.8
✅ **Clean**: Easy to delete venv and start fresh
✅ **Portable**: venv folder can be recreated anytime
✅ **Standard**: This is the recommended Python workflow

## Quick Commands Reference

```powershell
# Create venv with Python 3.12
py -3.12 -m venv venv

# Activate venv
.\venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Run backend
cd backend
uvicorn app.main:app --reload

# Run frontend (new terminal)
.\venv\Scripts\activate
cd frontend
streamlit run streamlit_app.py

# Deactivate when done
deactivate
```

## Notes

- The `venv` folder is already in `.gitignore` - won't be committed
- You can have multiple venvs for different projects
- Recreating venv is safe: just delete folder and run `py -3.12 -m venv venv` again
- Docker option doesn't need venv at all

---

**Ready to start?** Run the commands in Step 1 above! 🚀
