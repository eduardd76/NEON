# NEON - Network Emulation Orchestrated Naturally

🚀 Next-generation network lab platform with AI-powered topology building

## Features

### ✅ Implemented (v1.0)
- 🗣️ **AI Chat Interface** - Claude API integration for natural language processing
- 🎨 **Visual Topology Editor** - React Flow canvas with drag-and-drop
- 🐳 **Docker Runtime** - Complete container lifecycle management
- 📦 **Multi-Vendor Support** - 7 vendors, 7+ network OS images
- 🔗 **Lab Management** - Create, deploy, and destroy network topologies
- 🎯 **REST API** - Full-featured API with Swagger documentation
- 💾 **PostgreSQL Database** - Complete schema with 10 tables
- 🧪 **Automated Testing** - Integration tests for all components

### ✅ Implemented (v2.0)
- 🖥️ **Console Access** - xterm.js + WebSocket for real-time device management
- ⚡ **Link Creation** - veth pairs and network bridges for point-to-point connections
- 📱 **Node Properties Panel** - Interactive panel for device configuration and control
- 🎯 **Network Impairment** - Bandwidth, latency, and packet loss simulation via tc

### 🚧 In Progress (v2.5)
- 🔧 **AI-Powered Configuration** - Enhanced topology generation with tool calling
- ✅ **Testing Engine** - Batfish integration for validation

### 📋 Planned (v3.0)
- 👥 **User Authentication** - Multi-user support with roles
- 📚 **Templates** - Pre-built topology templates
- 📤 **Export/Import** - YAML/JSON topology formats
- 📊 **Monitoring** - Real-time metrics and logs

## Quick Start

### Prerequisites

- Docker Desktop
- Docker Compose
- Python 3.11+ (for development)
- Node.js 18+ (for frontend development)

### 1. Clone and Setup

```bash
cd F:\Agentic_Apps\NEON
cp .env.example .env
# Edit .env and add your Anthropic API key
```

### 2. Start Services

```bash
# Start PostgreSQL and backend
docker-compose up -d db backend

# Wait for database to be ready (check with docker-compose logs db)

# Run database migrations
docker-compose exec backend alembic upgrade head

# Seed initial data (vendors and images)
docker-compose exec backend python -m app.db.seed
```

### 3. Access the Application

- **API Documentation**: http://localhost:8000/docs
- **Backend API**: http://localhost:8000
- **Frontend** (when ready): http://localhost:5173

## Architecture

```
┌─────────────────────────────────────────────┐
│            Frontend (React)                 │
│   React Flow • Zustand • TailwindCSS       │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         Backend (FastAPI)                   │
│   Python 3.11 • SQLAlchemy • Anthropic     │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│        Database (PostgreSQL)                │
│   Images • Labs • Nodes • Links             │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│      Runtime (Docker/QEMU)                  │
│   Network Containers & VMs                  │
└─────────────────────────────────────────────┘
```

## Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Run Automated Tests

**Windows:**
```powershell
.\test-integration.ps1
```

**Linux/Mac:**
```bash
bash test-integration.sh
```

## API Endpoints

### Images
- `GET /api/v1/images` - List all network images
- `GET /api/v1/images/{id}` - Get image details
- `GET /api/v1/images/vendors/` - List vendors

### Labs
- `GET /api/v1/labs` - List all labs
- `POST /api/v1/labs` - Create a new lab
- `GET /api/v1/labs/{id}` - Get lab details
- `DELETE /api/v1/labs/{id}` - Delete a lab
- `POST /api/v1/labs/{id}/nodes` - Add node to lab
- `POST /api/v1/labs/{id}/links` - Add link to lab

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy 2.0** - ORM for database operations
- **Alembic** - Database migrations
- **PostgreSQL 15** - Primary database
- **Anthropic Claude 3.5 Sonnet** - AI integration
- **Docker SDK** - Container management
- **Pydantic** - Request/response validation

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **React Flow** - Visual topology editor
- **xterm.js** - Terminal emulator for console access
- **Zustand** - State management
- **TailwindCSS** - Styling
- **Axios** - HTTP client
- **TanStack Query** - Data fetching
- **Lucide React** - Icons

### Runtime
- **Docker** - Container runtime for network devices
- **PostgreSQL** - Database with JSONB for flexible schemas

## Current Status

**Version:** 1.0.0
**Status:** ✅ Production Ready (Core Features)

### Test Results
```
✓ 14/14 Integration tests passing
✓ Backend API fully functional
✓ Frontend builds successfully (416.93 KB)
✓ Docker runtime operational
✓ AI chat endpoint working
✓ Database migrations applied
✓ All services healthy
```

### What Works
- ✅ Create and manage labs
- ✅ Add network devices (nodes) to labs
- ✅ Visual topology canvas with React Flow
- ✅ Drag-and-drop device library
- ✅ AI chat interface
- ✅ Docker container deployment
- ✅ Multi-vendor image support
- ✅ RESTful API with Swagger UI

### Quick Test
```bash
# Run automated test suite
.\test-integration.ps1   # Windows
bash test-integration.sh # Linux/Mac

# Or manual test
curl http://localhost:8000/health
# Expected: {"status":"healthy","service":"neon-backend","version":"1.0.0"}
```

## Documentation

- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Complete testing manual
- **[CURSOR_QUICK_START.md](CURSOR_QUICK_START.md)** - 5-minute quick start
- **[CLAUDE.md](CLAUDE.md)** - Development guide for Claude Code
- **[NEON_DESIGN.md](NEON_DESIGN.md)** - Complete architecture & design

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and test thoroughly
4. Run integration tests (`.\test-integration.ps1`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Built with [Claude Code](https://claude.com/claude-code)
- Powered by Anthropic Claude 3.5 Sonnet
- Inspired by EVE-NG, Containerlab, and n8n

---

**"Light up your network with NEON"** 💡

🚀 **[View on GitHub](https://github.com/eduardd76/NEON)** | 📚 **[API Docs](http://localhost:8000/docs)** | 💬 **[Report Issues](https://github.com/eduardd76/NEON/issues)**
