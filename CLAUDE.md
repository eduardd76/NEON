# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NEON (Network Emulation Orchestrated Naturally) is an AI-powered network lab platform that combines:
- Natural language interface via Claude API for topology building
- Visual topology editor using React Flow (n8n-style drag-and-drop)
- Container-based network emulation using Docker and vrnetlab
- Multi-vendor network OS image support (Cisco, Arista, Nokia, Juniper, FRRouting)

**Tech Stack:**
- Backend: Python 3.11+ with FastAPI, SQLAlchemy 2.0, PostgreSQL 15
- Frontend: React 18 + TypeScript, React Flow, Zustand, TailwindCSS
- Runtime: Docker SDK for container orchestration
- AI: Anthropic Claude API for natural language processing

## Development Commands

### Initial Setup
```bash
# Copy environment template and configure
cp .env.example .env
# Edit .env to add ANTHROPIC_API_KEY and generate SECRET_KEY

# Start all services
docker-compose up -d

# Run database migrations
docker-compose exec backend alembic upgrade head

# Seed initial data (vendors and network images)
docker-compose exec backend python -m app.db.seed
```

### Backend Development
```bash
# Local development (without Docker)
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Database migrations
alembic revision --autogenerate -m "description"  # Create migration
alembic upgrade head                               # Apply migrations
alembic downgrade -1                               # Rollback one migration

# Run seed script
python -m app.db.seed

# Access API docs
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev        # Start dev server on port 5173
npm run build      # Production build
npm run lint       # ESLint
```

### Testing
```bash
# Run E2E integration tests (Playwright)
.\test-integration.ps1   # Windows
bash test-integration.sh # Linux/Mac

# Run AI topology build demo
cd tests
python demo_complete_workflow.py     # Full workflow demo
python demo_topology_build.py        # Topology generation only

# Install test dependencies
pip install playwright pytest
playwright install chromium
```

### Docker Operations
```bash
# Start specific services
docker-compose up -d db backend    # Backend only
docker-compose up -d               # All services

# View logs
docker-compose logs -f backend
docker-compose logs -f db

# Rebuild services
docker-compose build backend
docker-compose up -d --build backend

# Stop all services
docker-compose down

# Clean volumes (WARNING: deletes all data)
docker-compose down -v
```

## Architecture

### Database Schema
The PostgreSQL database contains 10 main tables:
- **vendors** - Network equipment vendors (Cisco, Arista, Nokia, etc.)
- **images** - Container/VM images with resource specs (cpu, memory, startup_time)
- **image_interfaces** - Interface definitions per image (naming patterns)
- **image_tags** - Searchable tags (datacenter, free, fast-boot)
- **users** - Multi-tenant user accounts
- **labs** - Topology instances with status tracking
- **nodes** - Device instances within labs (position, status, container_id)
- **links** - Connections between nodes with impairment parameters
- **templates** - Pre-built topology templates
- **lab_sessions** - Audit log for lab operations

**Key Relationships:**
- Vendor → Images (one-to-many)
- Image → Nodes (one-to-many via lab context)
- Lab → Nodes, Links (one-to-many with cascade delete)
- Node → Links (source/target relationships)

### Backend Structure
```
backend/app/
├── api/v1/          # REST endpoints
│   ├── images.py    # Network image management
│   ├── labs.py      # Lab CRUD + deploy/destroy
│   ├── chat.py      # AI chat with tool calling
│   └── console.py   # WebSocket console access
├── core/
│   ├── config.py    # Settings from env vars
│   └── security.py  # Auth helpers (future)
├── db/
│   ├── models/      # SQLAlchemy ORM (10 tables)
│   ├── base.py      # Database session management
│   └── seed.py      # Initial data seeding
├── runtime/
│   ├── docker.py    # Docker SDK wrapper
│   ├── network.py   # Network/link management
│   └── manager.py   # Orchestration layer
├── services/
│   ├── ai_tools.py         # Claude tool definitions
│   └── topology_builder.py # Topology pattern generation
└── main.py          # FastAPI app entry point
```

**Database Session Management:**
- Uses SQLAlchemy 2.0 async patterns
- Sessions managed via `SessionLocal()` context
- Models use UUID primary keys with `gen_random_uuid()`
- All timestamps use `timezone=True` with server defaults

**Runtime Architecture:**
- **DockerRuntime** (`runtime/docker.py`): Low-level container operations (create, start, stop, exec)
- **NetworkManager** (`runtime/network.py`): veth pair creation, bridge management, traffic control
- **RuntimeManager** (`runtime/manager.py`): High-level orchestration (deploy_node, create_link, check_ready)

### Frontend Structure
```
frontend/src/
├── components/
│   ├── canvas/      # TopologyCanvas.tsx - React Flow integration
│   ├── nodes/       # NetworkNode.tsx - Custom node components
│   ├── sidebar/     # NodeLibrary.tsx - Draggable image library
│   └── chat/        # ChatPanel.tsx - AI assistant interface
├── store/           # labStore.ts - Zustand state management
├── lib/             # api.ts, utils.ts - API client and utilities
└── types/           # TypeScript type definitions
```

**State Management (Zustand):**
- `labStore` manages topology state (nodes, edges, lab metadata)
- React Flow handles canvas state (node positions, connections)
- API calls use Axios with base URL from env

## Critical Patterns

### AI Tool Calling Architecture
The chat endpoint (`/api/v1/chat/`) uses Claude's structured tool calling for topology manipulation:
- **Tools Defined**: `app/services/ai_tools.py` contains 5 tools (add_nodes, add_links, create_topology_pattern, deploy_lab, get_lab_status)
- **Tool Execution**: `execute_tool_call()` in `chat.py` routes to TopologyBuilder methods
- **Response Format**: Returns ChatAction objects with type, description, data, and status
- **Model**: Currently uses `claude-3-sonnet-20240229` (may need update for newer API versions)

### Topology Builder Patterns
Located in `app/services/topology_builder.py`, supports 4 topology patterns:
- **ring**: Circular connectivity (each node connects to next)
- **mesh**: Full mesh (every node connects to every other)
- **star**: Central hub with spokes
- **spine-leaf**: Datacenter architecture with spine_count and leaf_count parameters

### Image Runtime Types
- **docker**: Native containers (cEOS, SR Linux, FRR, Alpine/Ubuntu) - fast startup
- **vrnetlab**: VM-based images wrapped in Docker (IOSv, CSR1000v, vMX) - slow startup
- **qemu**: Direct QEMU/KVM management (future support)

### Node Status Flow
```
stopped → starting → running → (error possible at any stage)
```
Managed via `nodes.status` column and container lifecycle.

### Link Status Flow
```
down → creating → up → (error possible during creation)
```
Links use veth pairs created by NetworkManager in `runtime/network.py`.

### API Design Conventions
- All endpoints under `/api/v1/` prefix
- UUID parameters in path (e.g., `/images/{image_id}`)
- Filtering via query params (type, vendor, runtime, tag, search)
- Response models include nested relationships (vendor in image response)
- Database dependencies injected via `Depends(get_db)`

### Frontend-Backend Communication
- API base URL: `http://localhost:8000` (configurable via `VITE_API_URL`)
- CORS enabled for all origins in development (restrict in production)
- Future: WebSocket support for real-time lab updates at `/api/v1/ws/{lab_id}`

## Development Workflow

### Adding a New Network Image
1. Add vendor if not exists (seed or via API)
2. Define image in `seed.py` with all required fields
3. Add interface pattern in `interfaces_definition` JSONB
4. Tag appropriately (datacenter, free, fast-boot)
5. Run seed script or create via API

### Creating a New API Endpoint
1. Add route handler in `backend/app/api/v1/{resource}.py`
2. Import and register in `main.py` with `app.include_router()`
3. Use dependency injection for database session
4. Return Pydantic models or ORM objects (FastAPI auto-serializes)

### Database Schema Changes
1. Modify model in `backend/app/db/models/`
2. Run `alembic revision --autogenerate -m "description"`
3. Review generated migration in `alembic/versions/`
4. Apply with `alembic upgrade head`
5. Never modify existing migrations once applied in production

### Working with AI Chat API
Natural language commands are processed through Claude's tool calling:
```python
# Example user commands:
"Add 3 Arista routers"
"Create a ring topology with 5 routers"
"Build a spine-leaf datacenter with 2 spines and 4 leaves"
"Connect R1 to R2"
"Deploy the lab"
```

The AI selects appropriate tools and the backend executes them via TopologyBuilder.
Key implementation files:
- `backend/app/api/v1/chat.py` - Chat endpoint with tool calling
- `backend/app/services/ai_tools.py` - Tool definitions
- `backend/app/services/topology_builder.py` - Topology generation logic

## Known Configuration

- Backend runs on port 8000
- Frontend runs on port 5173 (Vite dev server)
- PostgreSQL on port 5432
- Backend mounts `/var/run/docker.sock` for container management
- Frontend volume mounts exclude `node_modules` (populated in container)

## Current Development Status

**Version 2.5 - Completed:**
- ✅ Database schema (10 tables with relationships)
- ✅ Alembic migrations infrastructure
- ✅ Vendor and image seed data (7 vendors, 8+ images)
- ✅ FastAPI app with CORS and health endpoints
- ✅ Images API (list, get, filter by type/vendor/runtime)
- ✅ Labs API (CRUD operations + deploy/destroy)
- ✅ **AI Tool Calling** (Claude with structured tools)
- ✅ **Topology Builder** (ring, mesh, star, spine-leaf patterns)
- ✅ **Console Access** (xterm.js + WebSocket)
- ✅ **Link Creation** (veth pairs + network bridges)
- ✅ Docker Compose setup for all services
- ✅ Docker runtime layer (container lifecycle management)
- ✅ Runtime manager (node deployment orchestration)
- ✅ Frontend React app with complete UI
  - ✅ React Flow topology canvas
  - ✅ Drag-and-drop device library
  - ✅ AI chat panel with action visualization
  - ✅ Node properties panel
  - ✅ shadcn/ui components
- ✅ Pydantic schemas for request/response validation
- ✅ Production Dockerfile for frontend (nginx)
- ✅ **Playwright E2E Tests** (8 tests with 100% pass rate)
- ✅ Comprehensive documentation

**In Progress/Planned (v3.0):**
- ⏳ Configuration engine (Scrapli/NAPALM)
- ⏳ Testing engine (Batfish integration)
- ⏳ User authentication and authorization
- ⏳ Template system for pre-built topologies

## Important Notes

### Security & Configuration
- The `.env` file contains sensitive credentials - never commit it
- Generate SECRET_KEY using: `openssl rand -hex 32`
- ANTHROPIC_API_KEY is required for AI chat features
- Container runtime requires Docker socket access - security consideration for production

### Known Issues & Considerations
- **Claude Model Version**: `chat.py:108` uses `claude-3-sonnet-20240229` - may need updating for newer Anthropic API versions
- **Network Images**: URIs point to public registries except vrnetlab (requires local build)
- **Alembic Migrations**: Auto-generate may miss certain changes - always review before applying
- **React Flow**: Requires specific handle positioning for proper connection behavior
- **Console Access**: Requires container exec permissions and proper TTY allocation
- **Link Creation**: Uses Linux veth pairs - requires host networking capabilities

### Test Coverage
- 8 Playwright E2E tests covering: health checks, vendors, images, labs, nodes, links, topology build, console access
- Test scripts: `test-integration.ps1` (Windows) and `test-integration.sh` (Linux/Mac)
- Demo scripts: `tests/demo_complete_workflow.py` and `tests/demo_topology_build.py`
