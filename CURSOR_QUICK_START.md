# Quick Start Guide for Cursor IDE

## 🚀 5-Minute Quick Test

### Step 1: Open Terminal in Cursor
Press **`Ctrl + \``** (backtick) or click **View → Terminal**

### Step 2: Start Services
```bash
docker-compose up -d
```

Wait 15 seconds, then verify:
```bash
docker-compose ps
```

You should see:
```
NAME            STATUS          PORTS
neon_backend    Up             0.0.0.0:8000->8000/tcp
neon_db         Up (healthy)   0.0.0.0:5432->5432/tcp
```

### Step 3: Test Backend
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy","service":"neon-backend","version":"1.0.0"}
```

### Step 4: Open Swagger UI
Open in browser: **http://localhost:8000/docs**

You'll see interactive API documentation.

### Step 5: Run Automated Tests (Windows)
```powershell
.\test-integration.ps1
```

Or on Linux/Mac:
```bash
bash test-integration.sh
```

## 📋 What You Should See in Cursor

### Terminal View
```
┌─ Terminal ─────────────────────────────────────┐
│ $ docker-compose up -d                         │
│  Container neon_db  Running                    │
│  Container neon_backend  Running               │
│                                                 │
│ $ curl http://localhost:8000/health           │
│ {"status":"healthy","service":"neon-backend"}  │
└─────────────────────────────────────────────────┘
```

### File Explorer (Left Sidebar)
```
📁 NEON
  📁 backend
    📁 app
      📁 api
        📁 v1
          📄 chat.py      ← AI chat endpoint
          📄 images.py    ← Network images API
          📄 labs.py      ← Labs management
      📁 runtime
        📄 docker.py      ← Docker runtime
        📄 manager.py     ← Runtime manager
      📄 main.py          ← FastAPI entry point
  📁 frontend
    📁 src
      📁 components
        📁 ui
          📄 button.tsx   ← UI components
  📄 docker-compose.yml   ← Service orchestration
  📄 TESTING_GUIDE.md     ← Full test guide
  📄 test-integration.ps1 ← Windows test script
```

### Multiple Terminal Tabs
You can open multiple terminals:

**Tab 1: Backend Logs**
```bash
docker-compose logs -f backend
```

**Tab 2: Testing**
```bash
curl http://localhost:8000/api/v1/images/
```

**Tab 3: Frontend** (when ready)
```bash
cd frontend
npm run dev
```

## 🔍 Quick Tests in Cursor

### Using HTTP Client

Create file: `test.http` in root directory:

```http
### Test Health
GET http://localhost:8000/health

### List All Images
GET http://localhost:8000/api/v1/images/

### Create Lab
POST http://localhost:8000/api/v1/labs/
Content-Type: application/json

{
  "name": "Quick Test",
  "description": "Testing in Cursor"
}
```

Click "Send Request" above each request in Cursor!

### Using Cursor AI (Ctrl + L)

Ask Cursor AI:
- "Explain what the Docker runtime does"
- "Show me how to create a lab via API"
- "What network images are available?"

## 🎨 Cursor Features to Use

### 1. Command Palette (Ctrl + Shift + P)
- Type "Docker" to see Docker commands
- Type "Terminal" to manage terminals
- Type "Git" for version control

### 2. Split Editor (Ctrl + \\)
- View `docker-compose.yml` and logs side-by-side
- Compare API files

### 3. Search Everything (Ctrl + Shift + F)
- Search for "deploy_node" to find deployment code
- Search for "Docker" to see all Docker-related code

### 4. Integrated Git (Ctrl + Shift + G)
- View changes
- Commit directly
- See file history

## ✅ Verification Checklist

Check these in Cursor:

- [ ] Terminal opens successfully
- [ ] `docker-compose ps` shows 2 running containers
- [ ] http://localhost:8000/health returns JSON
- [ ] http://localhost:8000/docs loads Swagger UI
- [ ] Can create a lab via API
- [ ] No errors in `docker-compose logs backend`

## 🔧 Troubleshooting in Cursor

### Problem: Docker commands not found

**Solution:**
```bash
# Check Docker is in PATH
docker --version

# If not found, restart Cursor after installing Docker Desktop
```

### Problem: Port 8000 already in use

**Solution:**
```bash
# Find what's using the port
netstat -ano | findstr :8000

# Stop the backend container
docker-compose stop backend

# Start it again
docker-compose up -d backend
```

### Problem: Backend won't start

**Solution:**
```bash
# View detailed logs
docker-compose logs backend

# Common fixes:
docker-compose down
docker-compose up -d
```

### Problem: Can't connect to database

**Solution:**
```bash
# Restart database
docker-compose restart db

# Wait 10 seconds
timeout /t 10  # Windows
# sleep 10     # Linux/Mac

# Check it's healthy
docker-compose ps
```

## 📊 Expected Test Results

When you run `test-integration.ps1`, you should see:

```
============================================
NEON Integration Test Suite
============================================

1. Checking Prerequisites
-------------------------
Testing: Docker is running... ✓ PASSED
Testing: Python is installed... ✓ PASSED
Testing: Node.js is installed... ✓ PASSED

2. Checking Services
-------------------
Testing: Database container running... ✓ PASSED
Testing: Backend container running... ✓ PASSED

3. Testing Backend API
---------------------
Testing: Health endpoint... ✓ PASSED
Testing: Vendors endpoint... ✓ PASSED
Testing: Images endpoint... ✓ PASSED
Testing: Chat suggestions... ✓ PASSED

4. Testing Lab Operations
------------------------
Creating test lab... ✓ PASSED
  Lab ID: abc123...
Adding node to lab... ✓ PASSED
Retrieving lab details... ✓ PASSED
Deleting test lab... ✓ PASSED

5. Testing Frontend
------------------
Frontend build exists: ✓ PASSED

============================================
Test Results
============================================
Tests Passed: 13
Tests Failed: 0

✓ All tests passed!
```

## 🚀 Next Steps After Testing

1. **Explore Swagger UI**
   - http://localhost:8000/docs
   - Try each endpoint interactively

2. **Start Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   - Open http://localhost:5173

3. **Create Your First Lab**
   - Use Swagger UI or curl commands
   - Add nodes and links
   - View in database

4. **Modify Code**
   - Open `backend/app/api/v1/labs.py`
   - Make changes
   - Watch auto-reload in logs
   - Test immediately

5. **Use Cursor AI**
   - Press `Ctrl + L`
   - Ask: "How do I add a new API endpoint?"
   - Get code suggestions

## 💡 Cursor Pro Tips

1. **Multi-cursor editing**: Alt + Click to place multiple cursors
2. **Rename symbol**: F2 on any function/variable name
3. **Go to definition**: Ctrl + Click on any import or function
4. **Format document**: Shift + Alt + F
5. **Toggle terminal**: Ctrl + \`
6. **Command palette**: Ctrl + Shift + P (access any command)

## 📚 Files to Explore in Order

1. `docker-compose.yml` - Understand services
2. `backend/app/main.py` - API entry point
3. `backend/app/api/v1/images.py` - Simple CRUD example
4. `backend/app/api/v1/labs.py` - Complex operations
5. `backend/app/runtime/docker.py` - Container management
6. `backend/app/api/v1/chat.py` - AI integration

Happy testing! 🎉
