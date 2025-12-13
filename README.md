# NEON - Network Emulation Orchestrated Naturally

🚀 Next-generation network lab platform with AI-powered topology building

## Features

- 🗣️ **Natural Language Interface** - Describe topologies in plain English
- 🎨 **Visual Topology Editor** - n8n-style drag-and-drop canvas
- ⚡ **Instant Deployment** - Containers start in seconds
- 🔧 **AI-Powered Configuration** - Configure protocols conversationally
- ✅ **Built-in Testing** - Validate networks automatically

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

### Frontend Development (Coming Soon)

```bash
cd frontend
npm install
npm run dev
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
- **SQLAlchemy** - ORM for database operations
- **Alembic** - Database migrations
- **PostgreSQL** - Primary database
- **Anthropic Claude** - AI integration
- **Docker SDK** - Container management

### Frontend (Planned)
- **React 18** - UI framework
- **TypeScript** - Type safety
- **React Flow** - Visual topology editor
- **Zustand** - State management
- **TailwindCSS** - Styling
- **shadcn/ui** - Component library

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

---

**"Light up your network with NEON"** 💡
