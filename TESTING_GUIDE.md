# NEON Testing Guide for Cursor IDE

## Prerequisites

Before testing, ensure you have:
- ✅ Docker Desktop running
- ✅ Node.js 18+ installed
- ✅ Python 3.11+ installed (optional, for local backend dev)
- ✅ Cursor IDE installed

## Step 1: Open Project in Cursor

1. Launch Cursor IDE
2. Click `File > Open Folder`
3. Navigate to `F:\Agentic_Apps\NEON`
4. Click "Select Folder"

## Step 2: Verify Environment Files

### Check .env file exists and is configured:

```bash
# In Cursor terminal (Ctrl + ` or View > Terminal)
cat .env
```

You should see:
```
POSTGRES_USER=neon
POSTGRES_PASSWORD=neon
POSTGRES_DB=neon
DATABASE_URL=postgresql://neon:neon@db:5432/neon
ANTHROPIC_API_KEY=sk-ant-...
SECRET_KEY=your-secret-key
```

**If .env doesn't exist:**
```bash
cp .env.example .env
# Then edit .env and add your ANTHROPIC_API_KEY
```

## Step 3: Start Backend Services

### Option A: Using Docker Compose (Recommended)

Open Cursor terminal and run:

```bash
# Start database
docker-compose up -d db

# Wait 10 seconds for database to be ready
# You can check with:
docker-compose logs db

# Start backend
docker-compose up -d backend

# Check backend logs
docker-compose logs -f backend
```

You should see:
```
🚀 Starting NEON - Network Emulation Orchestrated Naturally v1.0.0
📚 API Documentation: http://localhost:8000/docs
```

Press `Ctrl+C` to stop following logs.

### Option B: Run Backend Locally (Alternative)

```bash
cd backend

# Create virtual environment (first time only)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Run backend
uvicorn app.main:app --reload
```

## Step 4: Test Backend API

### Method 1: Using Cursor Terminal

Open a new terminal tab in Cursor (click + in terminal panel):

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected output:
# {"status":"healthy","service":"neon-backend","version":"1.0.0"}
```

```bash
# Test vendors endpoint
curl http://localhost:8000/api/v1/images/vendors/

# Expected: JSON with 7 vendors (Cisco, Arista, Nokia, etc.)
```

```bash
# Test images endpoint
curl http://localhost:8000/api/v1/images/

# Expected: JSON with 7 network images
```

```bash
# Test chat suggestions
curl http://localhost:8000/api/v1/chat/suggestions

# Expected: JSON with suggested prompts
```

### Method 2: Using Swagger UI (Visual)

1. Open your browser
2. Navigate to: http://localhost:8000/docs
3. You'll see interactive API documentation
4. Click on any endpoint (e.g., GET /api/v1/images/)
5. Click "Try it out"
6. Click "Execute"
7. View the response

**Screenshot what you should see:**
- List of all API endpoints
- Green "Try it out" buttons
- Interactive request/response testing

### Method 3: Using Cursor's HTTP Client

Create a new file: `test-api.http` in the root directory:

```http
### Health Check
GET http://localhost:8000/health

### List Vendors
GET http://localhost:8000/api/v1/images/vendors/

### List Images
GET http://localhost:8000/api/v1/images/

### Create Lab
POST http://localhost:8000/api/v1/labs/
Content-Type: application/json

{
  "name": "My Test Lab",
  "description": "Testing NEON in Cursor"
}

### Chat Suggestions
GET http://localhost:8000/api/v1/chat/suggestions
```

Click the "Send Request" button that appears above each request.

## Step 5: Create a Test Lab

In Cursor terminal:

```bash
# Create a lab
curl -X POST http://localhost:8000/api/v1/labs/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Cursor Test Lab", "description": "My first NEON lab"}'

# Copy the "id" from the response (it will be a UUID like "abc123...")
```

**Save the lab ID for next steps!**

```bash
# Get first available image ID
curl http://localhost:8000/api/v1/images/ | grep -o '"id":"[^"]*"' | head -1

# Save this image ID too
```

```bash
# Add a node to your lab (replace LAB_ID and IMAGE_ID with actual values)
curl -X POST http://localhost:8000/api/v1/labs/YOUR_LAB_ID/nodes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Router1",
    "image_id": "YOUR_IMAGE_ID",
    "position_x": 100,
    "position_y": 100
  }'
```

```bash
# View your lab details
curl http://localhost:8000/api/v1/labs/YOUR_LAB_ID
```

## Step 6: Test Frontend

### Start Frontend Development Server

Open a new terminal in Cursor:

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start dev server
npm run dev
```

You should see:
```
  VITE v7.2.7  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**Open browser:** http://localhost:5173/

You should see the React application loading.

### Test Frontend Build

```bash
# In frontend directory
npm run build

# Expected output:
# ✓ 1932 modules transformed
# dist/index.html
# dist/assets/...
```

## Step 7: Full Stack Integration Test

### With all services running:

1. **Backend:** http://localhost:8000/docs
2. **Frontend:** http://localhost:5173/
3. **Database:** localhost:5432 (running in Docker)

### Test the complete flow:

```bash
# 1. Create a lab
LAB_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/labs/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Integration Test", "description": "Full stack test"}')

# 2. Extract lab ID (on Windows with Git Bash)
LAB_ID=$(echo $LAB_RESPONSE | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

echo "Created lab: $LAB_ID"

# 3. Get an image
IMAGE_ID=$(curl -s http://localhost:8000/api/v1/images/ | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

echo "Using image: $IMAGE_ID"

# 4. Add nodes
curl -X POST http://localhost:8000/api/v1/labs/$LAB_ID/nodes \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"R1\", \"image_id\": \"$IMAGE_ID\", \"position_x\": 100, \"position_y\": 100}"

curl -X POST http://localhost:8000/api/v1/labs/$LAB_ID/nodes \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"R2\", \"image_id\": \"$IMAGE_ID\", \"position_x\": 300, \"position_y\": 100}"

# 5. View lab
curl http://localhost:8000/api/v1/labs/$LAB_ID
```

## Step 8: Test Docker Runtime (Advanced)

**⚠️ Note:** Deployment requires network device Docker images to be available.

```bash
# Check available Docker images
docker images | grep -E "nokia|arista|frr"

# If you have FRR image available (easiest to test):
docker pull quay.io/frrouting/frr:10.1.0
```

```bash
# Try deploying a lab (if you have the images)
curl -X POST http://localhost:8000/api/v1/labs/$LAB_ID/deploy

# Check deployment status
curl http://localhost:8000/api/v1/labs/$LAB_ID

# View running containers
docker ps | grep neon

# Destroy lab
curl -X POST http://localhost:8000/api/v1/labs/$LAB_ID/destroy
```

## Common Issues & Solutions

### Issue 1: Port already in use

```bash
# Check what's using port 8000
netstat -ano | findstr :8000

# Stop the process or use different port
```

### Issue 2: Database connection error

```bash
# Restart database
docker-compose restart db

# Check database logs
docker-compose logs db
```

### Issue 3: Frontend won't start

```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue 4: Docker not accessible

```
# Make sure Docker Desktop is running
# Restart Docker Desktop if needed
```

## Using Cursor Features

### 1. Integrated Terminal
- Press `Ctrl + `` (backtick) to open terminal
- Click `+` to open multiple terminals
- Use split view for backend and frontend

### 2. File Navigation
- `Ctrl + P` - Quick open file
- `Ctrl + Shift + F` - Search across files
- `Ctrl + B` - Toggle sidebar

### 3. Git Integration
- Click Source Control icon (left sidebar)
- View changes, commit, push directly in Cursor

### 4. AI Assistant
- `Ctrl + L` - Open Cursor AI chat
- Ask questions about the code
- Get explanations for errors

### 5. Debug Mode
- Set breakpoints by clicking left of line numbers
- Press `F5` to start debugging
- Use debug console to inspect variables

## Verification Checklist

Use this checklist to verify everything is working:

- [ ] Docker Desktop is running
- [ ] .env file exists with valid values
- [ ] Database container is running (`docker ps | grep neon_db`)
- [ ] Backend container is running (`docker ps | grep neon_backend`)
- [ ] Backend responds to health check (http://localhost:8000/health)
- [ ] Swagger UI loads (http://localhost:8000/docs)
- [ ] Can list vendors
- [ ] Can list images (7 images visible)
- [ ] Can create a lab
- [ ] Can add nodes to lab
- [ ] Frontend builds successfully (`npm run build`)
- [ ] Frontend dev server runs (http://localhost:5173/)

## Quick Reference Commands

```bash
# Start everything
docker-compose up -d

# Stop everything
docker-compose down

# View all logs
docker-compose logs -f

# Rebuild backend after changes
docker-compose build backend
docker-compose up -d backend

# Run frontend locally
cd frontend && npm run dev

# Check service status
docker-compose ps

# Database shell access
docker-compose exec db psql -U neon -d neon
```

## Next Steps

Once testing is complete:

1. Explore the Swagger UI to understand all API endpoints
2. Modify frontend components in `frontend/src/components/`
3. Add new API endpoints in `backend/app/api/v1/`
4. Test with real network device images
5. Integrate AI chat functionality

## Support

If you encounter issues:

1. Check `docker-compose logs backend`
2. Check `docker-compose logs db`
3. Verify .env file is configured
4. Ensure all ports are available (8000, 5173, 5432)
5. Restart Docker Desktop if containers won't start
