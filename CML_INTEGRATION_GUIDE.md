# CML Image Integration Guide for NEON

This guide explains how to integrate your existing CML (Cisco Modeling Labs) images into NEON.

## Overview

You have **17 CML images** in `F:\ISO images\CML Images\`. These are production-quality Cisco images that will enable realistic network emulation.

## Available Images

### Routers
- **IOSv 15.9.3.M3** - 55MB - Classic IOS router (PERFECT FOR OSPF!)
- **CSR1000v 17.03.02** - 1.4GB - Cloud Services Router
- **IOS-XRv 6.3.1** - 436MB - Service Provider router

### Switches
- **IOSvL2 2020** - 87MB - Layer 2 switch
- **NX-OSv 7.3.0** - 168MB - Datacenter switch (Nexus 9000)
- **NX-OSv9000 9.2.4** - Datacenter switch
- **NX-OSv9300 9.3.6** - Top-of-rack switch
- **NX-OSv9500 9.3.6** - Modular datacenter switch

### Security
- **ASAv 9.15.1** - 241MB - Adaptive Security Appliance (firewall)

### Hosts/Servers
- **Alpine Linux 3.13.2** - Lightweight container
- **Ubuntu 20.04** - Full Linux server
- **CoreOS** - Container-optimized OS

## Integration Methods

### Method 1: Direct qcow2 Integration (Recommended for Quick Start)

NEON can use qcow2 files directly without building Docker images. This is the **fastest** way to get started.

#### Step 1: Copy Images to NEON Directory

```bash
# Create images directory in NEON
mkdir -p F:/Agentic_Apps/NEON/images/qcow2

# Copy the images you want to use
cp "F:/ISO images/CML Images/iosv-159-3-m3/vios-adventerprisek9-m.spa.159-3.m3.qcow2" \
   F:/Agentic_Apps/NEON/images/qcow2/iosv-15.9.3.qcow2

cp "F:/ISO images/CML Images/iosvl2-2020/vios_l2-adventerprisek9-m.ssa.high_iron_20200929.qcow2" \
   F:/Agentic_Apps/NEON/images/qcow2/iosvl2-2020.qcow2

cp "F:/ISO images/CML Images/csr1000v-170302/csr1000v-universalk9.17.03.02-serial.qcow2" \
   F:/Agentic_Apps/NEON/images/qcow2/csr1000v-17.03.02.qcow2
```

#### Step 2: Update NEON to Use Local qcow2 Files

Add this to `backend/app/db/seed.py`:

```python
# Add after existing image definitions

# Your CML Images
cml_iosv = Image(
    id=uuid.uuid4(),
    vendor_id=cisco_vendor.id,
    name="iosv-cml",
    display_name="Cisco IOSv 15.9.3 (CML)",
    version="15.9.3.M3",
    type=ImageType.ROUTER,
    runtime=RuntimeType.QEMU,  # Direct QEMU usage
    image_uri="file:///images/qcow2/iosv-15.9.3.qcow2",
    cpu_recommended=1,
    memory_recommended=512,
    startup_time=120,
    console_type="telnet",
    default_credentials={
        "username": "cisco",
        "password": "cisco"
    },
    interfaces_definition={
        "management": "GigabitEthernet0/0",
        "data_ports": ["GigabitEthernet0/1", "GigabitEthernet0/2",
                       "GigabitEthernet0/3", "GigabitEthernet0/4",
                       "GigabitEthernet0/5", "GigabitEthernet0/6",
                       "GigabitEthernet0/7"]
    },
    is_active=True,
    tags=["cml", "ospf", "eigrp", "bgp"]
)

cml_iosvl2 = Image(
    id=uuid.uuid4(),
    vendor_id=cisco_vendor.id,
    name="iosvl2-cml",
    display_name="Cisco IOSvL2 2020 (CML)",
    version="2020",
    type=ImageType.SWITCH,
    runtime=RuntimeType.QEMU,
    image_uri="file:///images/qcow2/iosvl2-2020.qcow2",
    cpu_recommended=1,
    memory_recommended=768,
    startup_time=90,
    console_type="telnet",
    default_credentials={
        "username": "cisco",
        "password": "cisco"
    },
    interfaces_definition={
        "management": "GigabitEthernet0/0",
        "data_ports": ["GigabitEthernet0/1", "GigabitEthernet0/2",
                       "GigabitEthernet0/3", "GigabitEthernet1/0",
                       "GigabitEthernet1/1", "GigabitEthernet1/2",
                       "GigabitEthernet1/3", "GigabitEthernet2/0"]
    },
    is_active=True,
    tags=["cml", "layer2", "switching", "vlan"]
)

cml_csr = Image(
    id=uuid.uuid4(),
    vendor_id=cisco_vendor.id,
    name="csr1000v-cml",
    display_name="Cisco CSR1000v 17.03.02 (CML)",
    version="17.03.02",
    type=ImageType.ROUTER,
    runtime=RuntimeType.QEMU,
    image_uri="file:///images/qcow2/csr1000v-17.03.02.qcow2",
    cpu_recommended=2,
    memory_recommended=4096,
    startup_time=180,
    console_type="telnet",
    default_credentials={
        "username": "cisco",
        "password": "cisco"
    },
    interfaces_definition={
        "management": "GigabitEthernet1",
        "data_ports": ["GigabitEthernet2", "GigabitEthernet3",
                       "GigabitEthernet4", "GigabitEthernet5"]
    },
    is_active=True,
    tags=["cml", "advanced", "bgp", "mpls", "vpn"]
)

# Add images to session
db.add(cml_iosv)
db.add(cml_iosvl2)
db.add(cml_csr)
```

#### Step 3: Update Docker Compose to Mount Images

Edit `docker-compose.yml`:

```yaml
backend:
  # ... existing config ...
  volumes:
    - ./backend:/app
    - /var/run/docker.sock:/var/run/docker.sock
    - F:/ISO images/CML Images:/images:ro  # Mount your CML images
```

### Method 2: vrnetlab Docker Integration (Production)

For production use, wrap qcow2 files in Docker containers using vrnetlab.

#### Step 1: Install vrnetlab

```bash
# Clone vrnetlab
cd F:/Agentic_Apps
git clone https://github.com/vrnetlab/vrnetlab.git
cd vrnetlab
```

#### Step 2: Build IOSv Docker Image

```bash
cd vios

# Copy your qcow2 file
cp "F:/ISO images/CML Images/iosv-159-3-m3/vios-adventerprisek9-m.spa.159-3.m3.qcow2" .

# Build Docker image
make

# This creates: vrnetlab/vios:15.9.3.M3
```

#### Step 3: Build IOSvL2 Docker Image

```bash
cd ../viosl2

# Copy your qcow2 file
cp "F:/ISO images/CML Images/iosvl2-2020/vios_l2-adventerprisek9-m.ssa.high_iron_20200929.qcow2" .

# Build Docker image
make

# This creates: vrnetlab/viosl2:2020
```

#### Step 4: Update seed.py for vrnetlab Images

```python
cml_iosv_docker = Image(
    id=uuid.uuid4(),
    vendor_id=cisco_vendor.id,
    name="iosv-vrnetlab",
    display_name="Cisco IOSv 15.9.3 (vrnetlab)",
    version="15.9.3.M3",
    type=ImageType.ROUTER,
    runtime=RuntimeType.VRNETLAB,
    image_uri="vrnetlab/vios:15.9.3.M3",  # Docker image
    cpu_recommended=1,
    memory_recommended=512,
    startup_time=120,
    console_type="telnet",
    default_credentials={
        "username": "cisco",
        "password": "cisco"
    },
    interfaces_definition={
        "management": "GigabitEthernet0/0",
        "data_ports": ["GigabitEthernet0/1", "GigabitEthernet0/2",
                       "GigabitEthernet0/3", "GigabitEthernet0/4"]
    },
    is_active=True,
    tags=["cml", "vrnetlab", "docker"]
)
```

## Quick Start: OSPF Test with Your Images

### Option A: Using IOSv (Recommended)

Your IOSv 15.9.3 is **perfect** for OSPF testing:

**Advantages:**
- ✅ Small (55MB) - fast deployment
- ✅ Full IOS feature set
- ✅ OSPF, EIGRP, BGP support
- ✅ Fast boot (~2 minutes)
- ✅ Low resource usage (512MB RAM)

**Configuration:**

```bash
# 1. Copy image
mkdir -p images/qcow2
cp "F:/ISO images/CML Images/iosv-159-3-m3/vios-adventerprisek9-m.spa.159-3.m3.qcow2" \
   images/qcow2/iosv-15.9.3.qcow2

# 2. Update seed file (add CML image definition above)

# 3. Reseed database
docker-compose exec backend python -m app.db.seed

# 4. Create topology via API using new CML images
# (Same REST API calls as before, but with CML image IDs)
```

### Option B: Using CSR1000v (Advanced Features)

For advanced OSPF features (stub areas, virtual links, authentication):

**Advantages:**
- ✅ Latest IOS-XE code
- ✅ All modern OSPF features
- ✅ BGP, MPLS, VPN support
- ⚠️ Larger (1.4GB)
- ⚠️ More resources (4GB RAM)
- ⚠️ Slower boot (~3 minutes)

## Comparison: Your CML vs Default NEON Images

| Feature | Your CML IOSv | Default vrnetlab IOSv |
|---------|---------------|------------------------|
| **Availability** | ✅ Already have | ❌ Need to download |
| **Size** | 55MB | ~50MB |
| **Version** | 15.9.3.M3 | Varies |
| **Licensing** | ✅ CML licensed | ⚠️ Need IOS image |
| **Integration** | Copy file | Build with vrnetlab |
| **Boot Time** | ~2 min | ~2 min |
| **OSPF Support** | ✅ Full | ✅ Full |
| **Trust** | ✅ You've used it | ❓ Unknown source |

**Winner: Your CML images!** You already have them, they're licensed, and you know they work.

## Complete CML Image Definitions

Here's the complete seed file addition for **all** your CML images:

```python
# File: backend/app/db/seed_cml.py

from app.db.models import Image, ImageType, RuntimeType
import uuid

def seed_cml_images(db, cisco_vendor):
    """Seed CML images from F:/ISO images/CML Images"""

    images = []

    # ===== ROUTERS =====

    # Cisco IOSv 15.9.3 - Perfect for OSPF labs
    images.append(Image(
        id=uuid.uuid4(),
        vendor_id=cisco_vendor.id,
        name="iosv-15.9.3-cml",
        display_name="Cisco IOSv 15.9.3 (CML)",
        version="15.9.3.M3",
        type=ImageType.ROUTER,
        runtime=RuntimeType.QEMU,
        image_uri="file:///images/qcow2/iosv-15.9.3.qcow2",
        cpu_recommended=1,
        memory_recommended=512,
        startup_time=120,
        console_type="telnet",
        default_credentials={"username": "cisco", "password": "cisco"},
        interfaces_definition={
            "mgmt": "GigabitEthernet0/0",
            "data": ["GigabitEthernet0/1-7"]
        },
        is_active=True,
        tags=["cml", "ospf", "eigrp", "bgp", "lightweight"]
    ))

    # Cisco CSR1000v 17.03.02 - Advanced features
    images.append(Image(
        id=uuid.uuid4(),
        vendor_id=cisco_vendor.id,
        name="csr1000v-17.03-cml",
        display_name="Cisco CSR1000v 17.03.02 (CML)",
        version="17.03.02",
        type=ImageType.ROUTER,
        runtime=RuntimeType.QEMU,
        image_uri="file:///images/qcow2/csr1000v-17.03.02.qcow2",
        cpu_recommended=2,
        memory_recommended=4096,
        startup_time=180,
        console_type="telnet",
        default_credentials={"username": "cisco", "password": "cisco"},
        interfaces_definition={
            "mgmt": "GigabitEthernet1",
            "data": ["GigabitEthernet2-5"]
        },
        is_active=True,
        tags=["cml", "advanced", "ios-xe", "bgp", "mpls"]
    ))

    # Cisco IOS-XRv 6.3.1 - Service Provider
    images.append(Image(
        id=uuid.uuid4(),
        vendor_id=cisco_vendor.id,
        name="iosxrv-6.3.1-cml",
        display_name="Cisco IOS-XRv 6.3.1 (CML)",
        version="6.3.1",
        type=ImageType.ROUTER,
        runtime=RuntimeType.QEMU,
        image_uri="file:///images/qcow2/iosxrv-6.3.1.qcow2",
        cpu_recommended=2,
        memory_recommended=4096,
        startup_time=300,
        console_type="telnet",
        default_credentials={"username": "cisco", "password": "cisco"},
        interfaces_definition={
            "mgmt": "MgmtEth0/0/CPU0/0",
            "data": ["GigabitEthernet0/0/0/0-3"]
        },
        is_active=True,
        tags=["cml", "service-provider", "mpls", "segment-routing"]
    ))

    # ===== SWITCHES =====

    # Cisco IOSvL2 - Layer 2 Switch
    images.append(Image(
        id=uuid.uuid4(),
        vendor_id=cisco_vendor.id,
        name="iosvl2-2020-cml",
        display_name="Cisco IOSvL2 2020 (CML)",
        version="2020",
        type=ImageType.SWITCH,
        runtime=RuntimeType.QEMU,
        image_uri="file:///images/qcow2/iosvl2-2020.qcow2",
        cpu_recommended=1,
        memory_recommended=768,
        startup_time=90,
        console_type="telnet",
        default_credentials={"username": "cisco", "password": "cisco"},
        interfaces_definition={
            "mgmt": "GigabitEthernet0/0",
            "data": ["GigabitEthernet0/1-3", "GigabitEthernet1/0-3"]
        },
        is_active=True,
        tags=["cml", "switch", "layer2", "vlan", "stp"]
    ))

    # Cisco NX-OSv 7.3.0 - Datacenter Switch
    images.append(Image(
        id=uuid.uuid4(),
        vendor_id=cisco_vendor.id,
        name="nxosv-7.3.0-cml",
        display_name="Cisco NX-OSv 7.3.0 (CML)",
        version="7.3.0",
        type=ImageType.SWITCH,
        runtime=RuntimeType.QEMU,
        image_uri="file:///images/qcow2/nxosv-7.3.0.qcow2",
        cpu_recommended=2,
        memory_recommended=4096,
        startup_time=240,
        console_type="telnet",
        default_credentials={"username": "admin", "password": "admin"},
        interfaces_definition={
            "mgmt": "mgmt0",
            "data": ["Ethernet1/1-48"]
        },
        is_active=True,
        tags=["cml", "datacenter", "vxlan", "fabricpath", "nexus"]
    ))

    # ===== SECURITY =====

    # Cisco ASAv 9.15.1 - Firewall
    images.append(Image(
        id=uuid.uuid4(),
        vendor_id=cisco_vendor.id,
        name="asav-9.15.1-cml",
        display_name="Cisco ASAv 9.15.1 (CML)",
        version="9.15.1",
        type=ImageType.FIREWALL,
        runtime=RuntimeType.QEMU,
        image_uri="file:///images/qcow2/asav-9.15.1.qcow2",
        cpu_recommended=2,
        memory_recommended=2048,
        startup_time=180,
        console_type="telnet",
        default_credentials={"username": "admin", "password": "Admin123"},
        interfaces_definition={
            "mgmt": "Management0/0",
            "data": ["GigabitEthernet0/0-3"]
        },
        is_active=True,
        tags=["cml", "firewall", "security", "vpn", "asa"]
    ))

    # Add all images to session
    for image in images:
        db.add(image)

    return images
```

## Next Steps

1. **Choose Integration Method:**
   - Method 1 (Direct qcow2): Fastest, good for development
   - Method 2 (vrnetlab): Better for production, containerized

2. **Start with IOSv for OSPF Test:**
   - Copy IOSv qcow2 file
   - Add to seed file
   - Reseed database
   - Create topology
   - Deploy and configure OSPF

3. **Expand to Other Images:**
   - Add CSR1000v for advanced features
   - Add ASAv for security labs
   - Add NX-OS for datacenter scenarios

## Recommended: IOSv for Your OSPF Test

For your **3 routers + OSPF area 0** test, I recommend:

**Routers:** 3x IOSv 15.9.3 (55MB each = 165MB total)
**Switch:** 1x IOSvL2 2020 (87MB)
**Total:** ~250MB

**Benefits:**
- ✅ Fast deployment (<5 minutes total)
- ✅ Low resource usage (~2.5GB RAM total)
- ✅ Full Cisco IOS OSPF implementation
- ✅ You already have the images
- ✅ Real Cisco CLI experience

Would you like me to create the integration now? I can:
1. Update the seed file with your CML images
2. Create a deployment script
3. Re-run the OSPF E2E test with your real Cisco images
