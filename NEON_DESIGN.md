# NEON - Network Emulation Orchestrated Naturally
## Complete Application Design Document

---

## 1. Product Vision

**NEON** is the next-generation network lab platform that combines:
- 🗣️ **Natural Language Interface** - Describe topologies in plain English
- 🎨 **Visual Topology Editor** - n8n-style drag-and-drop canvas
- ⚡ **Instant Deployment** - Containers start in seconds
- 🔧 **AI-Powered Configuration** - Configure protocols conversationally
- ✅ **Built-in Testing** - Validate networks automatically

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              NEON PLATFORM                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         FRONTEND (React)                             │   │
│  │  ┌─────────────┐  ┌──────────────────┐  ┌────────────────────────┐  │   │
│  │  │   Chat      │  │  Visual Editor   │  │    Console Panel       │  │   │
│  │  │   Panel     │  │  (React Flow)    │  │    (xterm.js)          │  │   │
│  │  │             │  │                  │  │                        │  │   │
│  │  │  "Add 3     │  │  ┌──┐    ┌──┐   │  │  Router> show ip route │  │   │
│  │  │   routers"  │  │  │R1│────│R2│   │  │  C 10.0.0.0/24 ...     │  │   │
│  │  │             │  │  └──┘    └──┘   │  │                        │  │   │
│  │  └─────────────┘  └──────────────────┘  └────────────────────────┘  │   │
│  │                                                                      │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │                    Node Library Sidebar                      │    │   │
│  │  │  [Routers ▼] [Switches ▼] [Firewalls ▼] [Hosts ▼] [Cloud ▼] │    │   │
│  │  │  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐          │    │   │
│  │  │  │cEOS│ │ FRR│ │vIOS│ │SRL │ │vMX │ │PAN │ │Host│          │    │   │
│  │  │  └────┘ └────┘ └────┘ └────┘ └────┘ └────┘ └────┘          │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         BACKEND (FastAPI)                            │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────────┐   │   │
│  │  │ NL Processor │  │  Topology    │  │   Config Engine          │   │   │
│  │  │ (Claude API) │  │  Engine      │  │   (Scrapli/NAPALM)       │   │   │
│  │  └──────────────┘  └──────────────┘  └─────────────────────────┘   │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────────┐   │   │
│  │  │ Test Engine  │  │  Image       │  │   Lab Manager            │   │   │
│  │  │ (Batfish)    │  │  Registry    │  │   (State + Persistence)  │   │   │
│  │  └──────────────┘  └──────────────┘  └─────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         RUNTIME LAYER                                │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────────┐   │   │
│  │  │   Docker     │  │   QEMU/KVM   │  │   vrnetlab               │   │   │
│  │  │   Runtime    │  │   Runtime    │  │   Bridge                 │   │   │
│  │  └──────────────┘  └──────────────┘  └─────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         DATABASE (PostgreSQL)                        │   │
│  │  [Images] [Labs] [Nodes] [Links] [Configs] [Users] [Templates]      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Database Schema

### 3.1 Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     vendors     │       │     images      │       │   image_tags    │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id              │──┐    │ id              │───────│ image_id        │
│ name            │  │    │ vendor_id       │──┐    │ tag             │
│ display_name    │  └───▶│ name            │  │    └─────────────────┘
│ logo_url        │       │ display_name    │  │
│ website         │       │ version         │  │    ┌─────────────────┐
│ created_at      │       │ type            │  │    │      labs       │
└─────────────────┘       │ runtime         │  │    ├─────────────────┤
                          │ image_uri       │  │    │ id              │
┌─────────────────┐       │ registry        │  │    │ user_id         │──┐
│     users       │       │ cpu_min         │  │    │ name            │  │
├─────────────────┤       │ cpu_recommended │  │    │ description     │  │
│ id              │       │ memory_min      │  │    │ status          │  │
│ email           │       │ memory_recommend│  │    │ topology_yaml   │  │
│ name            │       │ disk_size       │  │    │ created_at      │  │
│ role            │       │ startup_time    │  │    │ updated_at      │  │
│ created_at      │       │ console_type    │  │    └─────────────────┘  │
└─────────────────┘       │ default_creds   │  │             │           │
        │                 │ interfaces_def  │  │             │           │
        │                 │ license_required│  │             ▼           │
        │                 │ documentation   │  │    ┌─────────────────┐  │
        │                 │ is_active       │  │    │      nodes      │  │
        │                 │ created_at      │  │    ├─────────────────┤  │
        │                 └─────────────────┘  │    │ id              │  │
        │                          │           │    │ lab_id          │──┘
        │                          │           │    │ image_id        │──┘
        │                          ▼           │    │ name            │
        │                 ┌─────────────────┐  │    │ hostname        │
        │                 │ image_interfaces│  │    │ position_x      │
        │                 ├─────────────────┤  │    │ position_y      │
        │                 │ id              │  │    │ cpu             │
        │                 │ image_id        │──┘    │ memory          │
        │                 │ name            │       │ status          │
        │                 │ type            │       │ container_id    │
        │                 │ slot            │       │ mgmt_ip         │
        │                 │ mapping         │       │ console_port    │
        │                 └─────────────────┘       │ startup_config  │
        │                                           │ created_at      │
        │                                           └─────────────────┘
        │                                                    │
        │                 ┌─────────────────┐                │
        │                 │      links      │                │
        │                 ├─────────────────┤                │
        │                 │ id              │                │
        │                 │ lab_id          │                │
        │                 │ source_node_id  │────────────────┤
        │                 │ source_interface│                │
        │                 │ target_node_id  │────────────────┘
        │                 │ target_interface│
        │                 │ bandwidth       │
        │                 │ delay_ms        │
        │                 │ loss_percent    │
        │                 │ created_at      │
        │                 └─────────────────┘
        │
        │                 ┌─────────────────┐
        │                 │   templates     │
        │                 ├─────────────────┤
        │                 │ id              │
        └────────────────▶│ user_id         │
                          │ name            │
                          │ description     │
                          │ category        │
                          │ topology_yaml   │
                          │ thumbnail_url   │
                          │ is_public       │
                          │ created_at      │
                          └─────────────────┘
```

### 3.2 SQL Schema

```sql
-- =====================================================
-- NEON Database Schema
-- PostgreSQL 15+
-- =====================================================

-- Vendors (Cisco, Juniper, Arista, Nokia, etc.)
CREATE TABLE vendors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL UNIQUE,           -- 'cisco', 'juniper', 'arista'
    display_name VARCHAR(100) NOT NULL,         -- 'Cisco Systems'
    logo_url VARCHAR(500),
    website VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Network OS Images
CREATE TABLE images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id UUID REFERENCES vendors(id),
    
    -- Basic Info
    name VARCHAR(100) NOT NULL,                 -- 'ceos', 'vios', 'srlinux'
    display_name VARCHAR(200) NOT NULL,         -- 'Arista cEOS'
    version VARCHAR(50),                        -- '4.28.0F'
    description TEXT,
    
    -- Classification
    type VARCHAR(50) NOT NULL,                  -- 'router', 'switch', 'firewall', 'host'
    category VARCHAR(50),                       -- 'datacenter', 'enterprise', 'sp'
    
    -- Runtime
    runtime VARCHAR(20) NOT NULL DEFAULT 'docker',  -- 'docker', 'qemu', 'vrnetlab'
    image_uri VARCHAR(500) NOT NULL,            -- 'ghcr.io/nokia/srlinux:latest'
    registry VARCHAR(200),                      -- 'ghcr.io', 'docker.io', 'local'
    
    -- Resource Requirements
    cpu_min INTEGER DEFAULT 1,
    cpu_recommended INTEGER DEFAULT 2,
    memory_min INTEGER DEFAULT 512,             -- MB
    memory_recommended INTEGER DEFAULT 2048,    -- MB
    disk_size INTEGER DEFAULT 4096,             -- MB
    
    -- Behavior
    startup_time INTEGER DEFAULT 30,            -- seconds
    console_type VARCHAR(20) DEFAULT 'ssh',     -- 'ssh', 'telnet', 'serial'
    default_credentials JSONB,                  -- {"username": "admin", "password": "admin"}
    
    -- Interfaces
    interfaces_definition JSONB,                -- Interface naming/mapping
    max_interfaces INTEGER DEFAULT 16,
    
    -- Licensing
    license_required BOOLEAN DEFAULT false,
    license_info TEXT,
    
    -- Documentation
    documentation_url VARCHAR(500),
    notes TEXT,
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(vendor_id, name, version)
);

-- Interface definitions per image
CREATE TABLE image_interfaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    image_id UUID REFERENCES images(id) ON DELETE CASCADE,
    
    name VARCHAR(50) NOT NULL,                  -- 'Ethernet1', 'GigabitEthernet0/0'
    alias VARCHAR(50),                          -- 'eth1', 'e0/0'
    type VARCHAR(30) DEFAULT 'ethernet',        -- 'ethernet', 'management', 'serial'
    slot INTEGER DEFAULT 0,
    port INTEGER NOT NULL,
    linux_mapping VARCHAR(50),                  -- Actual Linux interface name
    
    UNIQUE(image_id, name)
);

-- Image tags for search/filtering
CREATE TABLE image_tags (
    image_id UUID REFERENCES images(id) ON DELETE CASCADE,
    tag VARCHAR(50) NOT NULL,
    
    PRIMARY KEY (image_id, tag)
);

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(200),
    role VARCHAR(20) DEFAULT 'user',            -- 'admin', 'user', 'viewer'
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Labs (Topology instances)
CREATE TABLE labs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    
    name VARCHAR(200) NOT NULL,
    description TEXT,
    
    -- Status
    status VARCHAR(30) DEFAULT 'draft',         -- 'draft', 'deploying', 'running', 'stopped', 'error'
    
    -- Topology (YAML representation)
    topology_yaml TEXT,
    
    -- Metadata
    tags VARCHAR(50)[],
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deployed_at TIMESTAMP,
    
    UNIQUE(user_id, name)
);

-- Nodes (Device instances in a lab)
CREATE TABLE nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lab_id UUID REFERENCES labs(id) ON DELETE CASCADE,
    image_id UUID REFERENCES images(id),
    
    -- Identity
    name VARCHAR(100) NOT NULL,                 -- 'r1', 'spine-1'
    hostname VARCHAR(100),                      -- Configured hostname
    
    -- Position on canvas
    position_x INTEGER DEFAULT 100,
    position_y INTEGER DEFAULT 100,
    
    -- Resources (override image defaults)
    cpu INTEGER,
    memory INTEGER,
    
    -- Runtime state
    status VARCHAR(30) DEFAULT 'stopped',       -- 'stopped', 'starting', 'running', 'error'
    container_id VARCHAR(100),                  -- Docker container ID
    mgmt_ip INET,                               -- Management IP
    console_port INTEGER,                       -- Console port mapping
    
    -- Configuration
    startup_config TEXT,                        -- Startup configuration
    running_config TEXT,                        -- Last known running config
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(lab_id, name)
);

-- Links (Connections between nodes)
CREATE TABLE links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lab_id UUID REFERENCES labs(id) ON DELETE CASCADE,
    
    -- Endpoints
    source_node_id UUID REFERENCES nodes(id) ON DELETE CASCADE,
    source_interface VARCHAR(50) NOT NULL,
    target_node_id UUID REFERENCES nodes(id) ON DELETE CASCADE,
    target_interface VARCHAR(50) NOT NULL,
    
    -- Link properties (for impairment)
    bandwidth VARCHAR(20),                      -- '1Gbps', '10Gbps'
    delay_ms INTEGER DEFAULT 0,                 -- Latency in ms
    loss_percent DECIMAL(5,2) DEFAULT 0,        -- Packet loss %
    jitter_ms INTEGER DEFAULT 0,                -- Jitter in ms
    
    -- State
    status VARCHAR(20) DEFAULT 'down',          -- 'up', 'down'
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(lab_id, source_node_id, source_interface),
    UNIQUE(lab_id, target_node_id, target_interface)
);

-- Pre-built topology templates
CREATE TABLE templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),          -- NULL for system templates
    
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50),                       -- 'datacenter', 'wan', 'campus', 'sp'
    
    -- Template content
    topology_yaml TEXT NOT NULL,
    
    -- Display
    thumbnail_url VARCHAR(500),
    icon VARCHAR(50),
    
    -- Visibility
    is_public BOOLEAN DEFAULT false,
    is_featured BOOLEAN DEFAULT false,
    
    -- Stats
    usage_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Lab sessions/history
CREATE TABLE lab_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lab_id UUID REFERENCES labs(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    
    action VARCHAR(50) NOT NULL,                -- 'deploy', 'destroy', 'save', 'export'
    details JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Indexes
-- =====================================================

CREATE INDEX idx_images_vendor ON images(vendor_id);
CREATE INDEX idx_images_type ON images(type);
CREATE INDEX idx_images_runtime ON images(runtime);
CREATE INDEX idx_images_active ON images(is_active);

CREATE INDEX idx_nodes_lab ON nodes(lab_id);
CREATE INDEX idx_nodes_status ON nodes(status);

CREATE INDEX idx_links_lab ON links(lab_id);

CREATE INDEX idx_labs_user ON labs(user_id);
CREATE INDEX idx_labs_status ON labs(status);

CREATE INDEX idx_templates_category ON templates(category);
CREATE INDEX idx_templates_public ON templates(is_public);

-- Full text search on images
CREATE INDEX idx_images_search ON images 
    USING gin(to_tsvector('english', name || ' ' || display_name || ' ' || COALESCE(description, '')));
```

### 3.3 Sample Data - Network Images

```sql
-- Insert Vendors
INSERT INTO vendors (name, display_name, logo_url, website) VALUES
('cisco', 'Cisco Systems', '/logos/cisco.svg', 'https://cisco.com'),
('arista', 'Arista Networks', '/logos/arista.svg', 'https://arista.com'),
('juniper', 'Juniper Networks', '/logos/juniper.svg', 'https://juniper.net'),
('nokia', 'Nokia', '/logos/nokia.svg', 'https://nokia.com'),
('paloalto', 'Palo Alto Networks', '/logos/paloalto.svg', 'https://paloaltonetworks.com'),
('frr', 'FRRouting', '/logos/frr.svg', 'https://frrouting.org'),
('linux', 'Linux', '/logos/linux.svg', 'https://kernel.org');

-- Insert Images
INSERT INTO images (
    vendor_id, name, display_name, version, type, runtime, 
    image_uri, cpu_min, memory_min, startup_time, 
    console_type, default_credentials, interfaces_definition
) VALUES

-- Arista cEOS
((SELECT id FROM vendors WHERE name='arista'), 
 'ceos', 'Arista cEOS', '4.32.0F', 'switch', 'docker',
 'ghcr.io/arista/ceos:4.32.0F', 1, 2048, 60,
 'ssh', '{"username": "admin", "password": "admin"}',
 '{"pattern": "Ethernet{n}", "start": 1, "max": 64}'
),

-- Nokia SR Linux
((SELECT id FROM vendors WHERE name='nokia'),
 'srlinux', 'Nokia SR Linux', '24.7.1', 'switch', 'docker',
 'ghcr.io/nokia/srlinux:24.7.1', 1, 2048, 45,
 'ssh', '{"username": "admin", "password": "NokiaSrl1!"}',
 '{"pattern": "ethernet-1/{n}", "start": 1, "max": 32}'
),

-- FRRouting
((SELECT id FROM vendors WHERE name='frr'),
 'frr', 'FRRouting', '10.1', 'router', 'docker',
 'quay.io/frrouting/frr:10.1.0', 1, 256, 5,
 'ssh', '{"username": "root", "password": ""}',
 '{"pattern": "eth{n}", "start": 0, "max": 16}'
),

-- Cisco IOSv (vrnetlab)
((SELECT id FROM vendors WHERE name='cisco'),
 'vios', 'Cisco IOSv', '15.9', 'router', 'vrnetlab',
 'vrnetlab/cisco_iosv:15.9', 1, 512, 180,
 'telnet', '{"username": "admin", "password": "admin"}',
 '{"pattern": "GigabitEthernet0/{n}", "start": 0, "max": 8}'
),

-- Cisco IOSv L2 (vrnetlab)
((SELECT id FROM vendors WHERE name='cisco'),
 'viosl2', 'Cisco IOSvL2', '15.2', 'switch', 'vrnetlab',
 'vrnetlab/cisco_viosl2:15.2', 1, 768, 180,
 'telnet', '{"username": "admin", "password": "admin"}',
 '{"pattern": "GigabitEthernet0/{n}", "start": 0, "max": 16}'
),

-- Cisco CSR1000v (vrnetlab)
((SELECT id FROM vendors WHERE name='cisco'),
 'csr1000v', 'Cisco CSR1000v', '17.3', 'router', 'vrnetlab',
 'vrnetlab/cisco_csr1000v:17.3', 1, 4096, 300,
 'ssh', '{"username": "admin", "password": "admin"}',
 '{"pattern": "GigabitEthernet{n}", "start": 1, "max": 8}'
),

-- Juniper vMX (vrnetlab)
((SELECT id FROM vendors WHERE name='juniper'),
 'vmx', 'Juniper vMX', '23.4R1', 'router', 'vrnetlab',
 'vrnetlab/juniper_vmx:23.4R1', 2, 8192, 600,
 'ssh', '{"username": "root", "password": "Juniper"}',
 '{"pattern": "ge-0/0/{n}", "start": 0, "max": 16}'
),

-- Juniper cRPD (container)
((SELECT id FROM vendors WHERE name='juniper'),
 'crpd', 'Juniper cRPD', '23.4R1', 'router', 'docker',
 'crpd:23.4R1', 1, 512, 15,
 'ssh', '{"username": "root", "password": "cRPD123"}',
 '{"pattern": "eth{n}", "start": 0, "max": 16}'
),

-- Palo Alto VM-Series (vrnetlab)
((SELECT id FROM vendors WHERE name='paloalto'),
 'panos', 'Palo Alto VM-Series', '11.1', 'firewall', 'vrnetlab',
 'vrnetlab/paloalto_panos:11.1', 2, 6144, 600,
 'ssh', '{"username": "admin", "password": "admin"}',
 '{"pattern": "ethernet1/{n}", "start": 1, "max": 8}'
),

-- Alpine Linux (host)
((SELECT id FROM vendors WHERE name='linux'),
 'alpine', 'Alpine Linux', '3.19', 'host', 'docker',
 'alpine:3.19', 1, 64, 2,
 'ssh', '{"username": "root", "password": ""}',
 '{"pattern": "eth{n}", "start": 0, "max": 8}'
),

-- Ubuntu (host)
((SELECT id FROM vendors WHERE name='linux'),
 'ubuntu', 'Ubuntu Server', '24.04', 'host', 'docker',
 'ubuntu:24.04', 1, 256, 3,
 'ssh', '{"username": "root", "password": "ubuntu"}',
 '{"pattern": "eth{n}", "start": 0, "max": 8}'
);

-- Add tags
INSERT INTO image_tags (image_id, tag)
SELECT id, 'datacenter' FROM images WHERE name IN ('ceos', 'srlinux');

INSERT INTO image_tags (image_id, tag)
SELECT id, 'free' FROM images WHERE name IN ('frr', 'srlinux', 'alpine', 'ubuntu');

INSERT INTO image_tags (image_id, tag)
SELECT id, 'fast-boot' FROM images WHERE startup_time < 30;
```

---

## 4. UI Design (n8n-Style Visual Editor)

### 4.1 Technology Stack

| Component | Technology | Reason |
|-----------|------------|--------|
| **Framework** | React 18 + TypeScript | Type safety, ecosystem |
| **Canvas** | React Flow | Best node-based UI library |
| **State** | Zustand | Simple, performant |
| **Styling** | Tailwind CSS | Rapid development |
| **Components** | shadcn/ui | Beautiful, accessible |
| **Icons** | Lucide React | Clean, consistent |
| **Terminal** | xterm.js | Real terminal emulation |
| **Layout** | ELKjs | Auto-layout algorithm |

### 4.2 UI Layout

```
┌──────────────────────────────────────────────────────────────────────────┐
│  NEON                                    [Lab: my-dc-lab] [Deploy] [⚙️]  │
├──────────────┬───────────────────────────────────────────────┬───────────┤
│              │                                               │           │
│   SIDEBAR    │              CANVAS (React Flow)              │  PANEL    │
│              │                                               │           │
│ ┌──────────┐ │    ┌──────┐         ┌──────┐                 │ Properties│
│ │ 🔍 Search │ │    │      │         │      │                 │           │
│ └──────────┘ │    │  R1  │─────────│  R2  │                 │ Name: R1  │
│              │    │      │         │      │                 │ Image:cEOS│
│ ▼ Routers    │    └──────┘         └──────┘                 │ CPU: 2    │
│   ┌────┐     │         │               │                    │ RAM: 2048 │
│   │cEOS│     │         │               │                    │           │
│   └────┘     │         │    ┌──────┐   │                    │ Interfaces│
│   ┌────┐     │         └────│      │───┘                    │ ├ eth1    │
│   │FRR │     │              │  SW1 │                        │ ├ eth2    │
│   └────┘     │              │      │                        │ └ eth3    │
│   ┌────┐     │              └──────┘                        │           │
│   │vIOS│     │                  │                           │ [Config]  │
│   └────┘     │              ┌──────┐                        │ [Console] │
│              │              │      │                        │           │
│ ▼ Switches   │              │ Host │                        │───────────│
│   ┌────┐     │              │      │                        │           │
│   │SRL │     │              └──────┘                        │   CHAT    │
│   └────┘     │                                               │           │
│              │                                               │ You:      │
│ ▼ Firewalls  │   [+] [-] [⟲] [Auto Layout] [100%]          │ Add OSPF  │
│   ┌────┐     │                                               │ to all    │
│   │PAN │     │                                               │ routers   │
│   └────┘     │                                               │           │
│              │                                               │ NEON:     │
│ ▼ Hosts      │                                               │ ✓ Done    │
│   ┌────┐     │                                               │           │
│   │🐧 │     │                                               │ [────────]│
│   └────┘     │                                               │ [  Ask   ]│
│              │                                               │           │
├──────────────┴───────────────────────────────────────────────┴───────────┤
│  [Status: 4 nodes running] [CPU: 23%] [RAM: 8.2GB/32GB]                  │
└──────────────────────────────────────────────────────────────────────────┘
```

### 4.3 React Flow Node Components

```tsx
// src/components/nodes/NetworkNode.tsx
import { Handle, Position, NodeProps } from 'reactflow';
import { cn } from '@/lib/utils';

interface NetworkNodeData {
  label: string;
  type: 'router' | 'switch' | 'firewall' | 'host';
  vendor: string;
  image: string;
  status: 'stopped' | 'starting' | 'running' | 'error';
  mgmtIp?: string;
}

const statusColors = {
  stopped: 'bg-gray-400',
  starting: 'bg-yellow-400 animate-pulse',
  running: 'bg-green-400',
  error: 'bg-red-400',
};

const typeIcons = {
  router: '🔀',
  switch: '🔌',
  firewall: '🛡️',
  host: '🖥️',
};

export function NetworkNode({ data, selected }: NodeProps<NetworkNodeData>) {
  return (
    <div
      className={cn(
        'px-4 py-2 rounded-lg border-2 bg-white shadow-md min-w-[120px]',
        'transition-all duration-200',
        selected ? 'border-blue-500 shadow-lg' : 'border-gray-200',
        'hover:shadow-lg'
      )}
    >
      {/* Connection handles - top, bottom, left, right */}
      <Handle type="target" position={Position.Top} className="w-3 h-3" />
      <Handle type="source" position={Position.Bottom} className="w-3 h-3" />
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      <Handle type="source" position={Position.Right} className="w-3 h-3" />

      {/* Status indicator */}
      <div className="absolute -top-1 -right-1">
        <div className={cn('w-3 h-3 rounded-full', statusColors[data.status])} />
      </div>

      {/* Node content */}
      <div className="flex flex-col items-center gap-1">
        <span className="text-2xl">{typeIcons[data.type]}</span>
        <span className="font-semibold text-sm">{data.label}</span>
        <span className="text-xs text-gray-500">{data.image}</span>
        {data.mgmtIp && (
          <span className="text-xs text-blue-600 font-mono">{data.mgmtIp}</span>
        )}
      </div>
    </div>
  );
}
```

### 4.4 Sidebar Component

```tsx
// src/components/sidebar/NodeLibrary.tsx
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ChevronDown, Search } from 'lucide-react';
import { Input } from '@/components/ui/input';

interface ImageGroup {
  type: string;
  images: Image[];
}

export function NodeLibrary() {
  const [search, setSearch] = useState('');
  const [expanded, setExpanded] = useState<string[]>(['router', 'switch']);

  const { data: images } = useQuery({
    queryKey: ['images'],
    queryFn: () => fetch('/api/images').then(r => r.json()),
  });

  const grouped = groupByType(images || []);

  const onDragStart = (event: React.DragEvent, image: Image) => {
    event.dataTransfer.setData('application/neon-node', JSON.stringify(image));
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <div className="w-64 bg-gray-50 border-r flex flex-col h-full">
      {/* Search */}
      <div className="p-3 border-b">
        <div className="relative">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search images..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      {/* Categories */}
      <div className="flex-1 overflow-y-auto p-2">
        {grouped.map((group) => (
          <div key={group.type} className="mb-2">
            {/* Category header */}
            <button
              onClick={() => toggleExpanded(group.type)}
              className="flex items-center gap-2 w-full p-2 hover:bg-gray-100 rounded"
            >
              <ChevronDown
                className={cn(
                  'h-4 w-4 transition-transform',
                  !expanded.includes(group.type) && '-rotate-90'
                )}
              />
              <span className="font-medium capitalize">{group.type}s</span>
              <span className="text-xs text-gray-500 ml-auto">
                {group.images.length}
              </span>
            </button>

            {/* Images */}
            {expanded.includes(group.type) && (
              <div className="grid grid-cols-2 gap-2 p-2">
                {group.images
                  .filter((img) =>
                    img.displayName.toLowerCase().includes(search.toLowerCase())
                  )
                  .map((image) => (
                    <div
                      key={image.id}
                      draggable
                      onDragStart={(e) => onDragStart(e, image)}
                      className={cn(
                        'p-2 bg-white rounded border cursor-grab',
                        'hover:border-blue-400 hover:shadow-sm',
                        'active:cursor-grabbing'
                      )}
                    >
                      <div className="flex flex-col items-center gap-1">
                        <img
                          src={image.vendor.logoUrl}
                          alt={image.vendor.name}
                          className="w-8 h-8 object-contain"
                        />
                        <span className="text-xs font-medium text-center">
                          {image.displayName}
                        </span>
                      </div>
                    </div>
                  ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
```

### 4.5 Main Canvas Component

```tsx
// src/components/canvas/TopologyCanvas.tsx
import { useCallback } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  Connection,
  Edge,
  ReactFlowProvider,
} from 'reactflow';
import 'reactflow/dist/style.css';

import { NetworkNode } from '../nodes/NetworkNode';
import { useLabStore } from '@/store/labStore';

const nodeTypes = {
  networkNode: NetworkNode,
};

export function TopologyCanvas() {
  const { lab, addNode, addLink } = useLabStore();
  const [nodes, setNodes, onNodesChange] = useNodesState(lab?.nodes || []);
  const [edges, setEdges, onEdgesChange] = useEdgesState(lab?.links || []);

  // Handle new connections
  const onConnect = useCallback(
    (params: Connection) => {
      setEdges((eds) => addEdge(params, eds));
      addLink({
        sourceNodeId: params.source!,
        sourceInterface: params.sourceHandle!,
        targetNodeId: params.target!,
        targetInterface: params.targetHandle!,
      });
    },
    [setEdges, addLink]
  );

  // Handle drop from sidebar
  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      const imageData = event.dataTransfer.getData('application/neon-node');
      if (!imageData) return;

      const image = JSON.parse(imageData);
      const position = {
        x: event.clientX - 60,
        y: event.clientY - 30,
      };

      const newNode = {
        id: `${image.name}-${Date.now()}`,
        type: 'networkNode',
        position,
        data: {
          label: `${image.name.toUpperCase()}${nodes.length + 1}`,
          type: image.type,
          vendor: image.vendor.name,
          image: image.displayName,
          status: 'stopped',
        },
      };

      setNodes((nds) => [...nds, newNode]);
      addNode(newNode);
    },
    [nodes, setNodes, addNode]
  );

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  return (
    <div className="flex-1 h-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onDrop={onDrop}
        onDragOver={onDragOver}
        nodeTypes={nodeTypes}
        fitView
        snapToGrid
        snapGrid={[15, 15]}
      >
        <Background color="#e5e7eb" gap={15} />
        <Controls />
        <MiniMap 
          nodeColor={(node) => {
            switch (node.data?.status) {
              case 'running': return '#22c55e';
              case 'starting': return '#eab308';
              case 'error': return '#ef4444';
              default: return '#9ca3af';
            }
          }}
        />
      </ReactFlow>
    </div>
  );
}
```

### 4.6 Chat Panel Component

```tsx
// src/components/chat/ChatPanel.tsx
import { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { useLabStore } from '@/store/labStore';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  actions?: Action[];
}

export function ChatPanel() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { lab, applyActions } = useLabStore();

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          labContext: lab,
        }),
      });

      const data = await response.json();
      
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.response,
          actions: data.actions,
        },
      ]);

      // Apply any topology changes
      if (data.actions?.length > 0) {
        applyActions(data.actions);
      }
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Error processing request.' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-80 border-l flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="p-3 border-b bg-white">
        <h3 className="font-semibold">AI Assistant</h3>
        <p className="text-xs text-gray-500">
          Describe what you want to build
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={cn(
              'p-3 rounded-lg text-sm',
              msg.role === 'user'
                ? 'bg-blue-500 text-white ml-6'
                : 'bg-white border mr-6'
            )}
          >
            <p className="whitespace-pre-wrap">{msg.content}</p>
            
            {/* Show applied actions */}
            {msg.actions && msg.actions.length > 0 && (
              <div className="mt-2 pt-2 border-t border-gray-200">
                {msg.actions.map((action, j) => (
                  <div key={j} className="flex items-center gap-1 text-xs text-green-600">
                    <span>✓</span>
                    <span>{action.description}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
        
        {loading && (
          <div className="flex items-center gap-2 text-gray-500">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span className="text-sm">Thinking...</span>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-3 border-t bg-white">
        <div className="flex gap-2">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Add 3 routers with OSPF..."
            className="resize-none"
            rows={2}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
          />
          <Button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            size="icon"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
        
        {/* Quick actions */}
        <div className="flex gap-1 mt-2 flex-wrap">
          {['Add router', 'Add switch', 'Connect all', 'Deploy lab'].map((action) => (
            <button
              key={action}
              onClick={() => setInput(action)}
              className="text-xs px-2 py-1 bg-gray-100 rounded hover:bg-gray-200"
            >
              {action}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
```

---

## 5. API Endpoints

### 5.1 Images API

```python
# /api/v1/images

@router.get("/images")
async def list_images(
    type: Optional[str] = None,      # router, switch, firewall, host
    vendor: Optional[str] = None,
    runtime: Optional[str] = None,   # docker, qemu, vrnetlab
    tag: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List available network images with filtering"""
    query = db.query(Image).filter(Image.is_active == True)
    
    if type:
        query = query.filter(Image.type == type)
    if vendor:
        query = query.filter(Image.vendor.has(name=vendor))
    if runtime:
        query = query.filter(Image.runtime == runtime)
    if tag:
        query = query.filter(Image.tags.any(tag=tag))
    if search:
        query = query.filter(
            Image.display_name.ilike(f"%{search}%") |
            Image.name.ilike(f"%{search}%")
        )
    
    return query.all()

@router.get("/images/{image_id}")
async def get_image(image_id: UUID, db: Session = Depends(get_db)):
    """Get detailed image info including interfaces"""
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(404, "Image not found")
    return image
```

### 5.2 Labs API

```python
# /api/v1/labs

@router.post("/labs")
async def create_lab(
    lab: LabCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new lab"""
    db_lab = Lab(
        user_id=user.id,
        name=lab.name,
        description=lab.description
    )
    db.add(db_lab)
    db.commit()
    return db_lab

@router.post("/labs/{lab_id}/deploy")
async def deploy_lab(
    lab_id: UUID,
    db: Session = Depends(get_db),
    runtime: RuntimeManager = Depends(get_runtime)
):
    """Deploy all nodes in a lab"""
    lab = db.query(Lab).filter(Lab.id == lab_id).first()
    if not lab:
        raise HTTPException(404, "Lab not found")
    
    lab.status = "deploying"
    db.commit()
    
    try:
        # Deploy each node
        for node in lab.nodes:
            container_id = await runtime.create_node(node)
            node.container_id = container_id
            node.status = "starting"
            db.commit()
            
            # Wait for startup
            await runtime.wait_for_ready(node)
            node.status = "running"
            node.mgmt_ip = await runtime.get_mgmt_ip(container_id)
            db.commit()
        
        # Create links
        for link in lab.links:
            await runtime.create_link(link)
            link.status = "up"
            db.commit()
        
        lab.status = "running"
        lab.deployed_at = datetime.utcnow()
        db.commit()
        
    except Exception as e:
        lab.status = "error"
        db.commit()
        raise HTTPException(500, str(e))
    
    return lab
```

---

## 6. Project Structure

```
neon/
├── frontend/                      # React application
│   ├── src/
│   │   ├── components/
│   │   │   ├── canvas/           # React Flow canvas
│   │   │   ├── nodes/            # Custom node components
│   │   │   ├── sidebar/          # Node library
│   │   │   ├── panel/            # Properties panel
│   │   │   ├── chat/             # AI chat interface
│   │   │   ├── console/          # xterm.js terminal
│   │   │   └── ui/               # shadcn components
│   │   ├── store/                # Zustand stores
│   │   ├── hooks/                # Custom hooks
│   │   ├── lib/                  # Utilities
│   │   └── App.tsx
│   ├── package.json
│   └── tailwind.config.js
│
├── backend/                       # FastAPI application
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── images.py
│   │   │   │   ├── labs.py
│   │   │   │   ├── nodes.py
│   │   │   │   ├── links.py
│   │   │   │   ├── chat.py
│   │   │   │   └── console.py
│   │   │   └── deps.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── ai.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   ├── session.py
│   │   │   └── models/
│   │   ├── runtime/
│   │   │   ├── docker.py
│   │   │   ├── qemu.py
│   │   │   ├── vrnetlab.py
│   │   │   └── network.py
│   │   ├── schemas/
│   │   └── main.py
│   ├── alembic/                  # DB migrations
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml
├── docker-compose.dev.yml
└── README.md
```

---

## 7. Next Steps

1. **Phase 1 (Week 1-2)**: Database + API
   - Set up PostgreSQL
   - Implement image registry API
   - Basic lab CRUD

2. **Phase 2 (Week 3-4)**: React Flow UI
   - Canvas with drag-drop
   - Node library sidebar
   - Properties panel

3. **Phase 3 (Week 5-6)**: AI Integration
   - Claude function calling
   - NL → topology actions
   - Chat panel

4. **Phase 4 (Week 7-8)**: Runtime
   - Docker runtime
   - Link management
   - Console access

5. **Phase 5 (Week 9-10)**: Polish
   - Templates
   - Export/import
   - Testing engine

---

## 8. Conclusion

NEON combines:
- **EVE-NG's** visual approach and multi-vendor support
- **Containerlab's** speed and declarative model
- **n8n's** beautiful node-based UI
- **AI's** natural language understanding

The result: Network engineers describe what they want, and NEON builds it.

**"Light up your network with NEON"** 💡
