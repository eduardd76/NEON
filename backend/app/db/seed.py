"""
Seed database with initial vendors and network images
"""
from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.db.models import Vendor, Image, ImageTag


def seed_vendors(db: Session):
    """Seed vendor data"""
    vendors_data = [
        {
            "name": "cisco",
            "display_name": "Cisco Systems",
            "logo_url": "/logos/cisco.svg",
            "website": "https://cisco.com"
        },
        {
            "name": "arista",
            "display_name": "Arista Networks",
            "logo_url": "/logos/arista.svg",
            "website": "https://arista.com"
        },
        {
            "name": "juniper",
            "display_name": "Juniper Networks",
            "logo_url": "/logos/juniper.svg",
            "website": "https://juniper.net"
        },
        {
            "name": "nokia",
            "display_name": "Nokia",
            "logo_url": "/logos/nokia.svg",
            "website": "https://nokia.com"
        },
        {
            "name": "paloalto",
            "display_name": "Palo Alto Networks",
            "logo_url": "/logos/paloalto.svg",
            "website": "https://paloaltonetworks.com"
        },
        {
            "name": "frr",
            "display_name": "FRRouting",
            "logo_url": "/logos/frr.svg",
            "website": "https://frrouting.org"
        },
        {
            "name": "linux",
            "display_name": "Linux",
            "logo_url": "/logos/linux.svg",
            "website": "https://kernel.org"
        }
    ]

    for vendor_data in vendors_data:
        existing = db.query(Vendor).filter(Vendor.name == vendor_data["name"]).first()
        if not existing:
            vendor = Vendor(**vendor_data)
            db.add(vendor)

    db.commit()
    print("✓ Vendors seeded successfully")


def seed_images(db: Session):
    """Seed network image data"""
    # Get vendor references
    vendors = {v.name: v for v in db.query(Vendor).all()}

    images_data = [
        # Arista cEOS
        {
            "vendor_id": vendors["arista"].id,
            "name": "ceos",
            "display_name": "Arista cEOS",
            "version": "4.32.0F",
            "type": "switch",
            "runtime": "docker",
            "image_uri": "ghcr.io/arista/ceos:4.32.0F",
            "cpu_min": 1,
            "memory_min": 2048,
            "startup_time": 60,
            "console_type": "ssh",
            "default_credentials": {"username": "admin", "password": "admin"},
            "interfaces_definition": {"pattern": "Ethernet{n}", "start": 1, "max": 64}
        },
        # Nokia SR Linux
        {
            "vendor_id": vendors["nokia"].id,
            "name": "srlinux",
            "display_name": "Nokia SR Linux",
            "version": "24.7.1",
            "type": "switch",
            "runtime": "docker",
            "image_uri": "ghcr.io/nokia/srlinux:24.7.1",
            "cpu_min": 1,
            "memory_min": 2048,
            "startup_time": 45,
            "console_type": "ssh",
            "default_credentials": {"username": "admin", "password": "NokiaSrl1!"},
            "interfaces_definition": {"pattern": "ethernet-1/{n}", "start": 1, "max": 32}
        },
        # FRRouting
        {
            "vendor_id": vendors["frr"].id,
            "name": "frr",
            "display_name": "FRRouting",
            "version": "10.1",
            "type": "router",
            "runtime": "docker",
            "image_uri": "quay.io/frrouting/frr:10.1.0",
            "cpu_min": 1,
            "memory_min": 256,
            "startup_time": 5,
            "console_type": "ssh",
            "default_credentials": {"username": "root", "password": ""},
            "interfaces_definition": {"pattern": "eth{n}", "start": 0, "max": 16}
        },
        # Cisco IOSv (vrnetlab)
        {
            "vendor_id": vendors["cisco"].id,
            "name": "vios",
            "display_name": "Cisco IOSv",
            "version": "15.9",
            "type": "router",
            "runtime": "vrnetlab",
            "image_uri": "vrnetlab/cisco_iosv:15.9",
            "cpu_min": 1,
            "memory_min": 512,
            "startup_time": 180,
            "console_type": "telnet",
            "default_credentials": {"username": "admin", "password": "admin"},
            "interfaces_definition": {"pattern": "GigabitEthernet0/{n}", "start": 0, "max": 8}
        },
        # Cisco IOSvL2 (vrnetlab)
        {
            "vendor_id": vendors["cisco"].id,
            "name": "viosl2",
            "display_name": "Cisco IOSvL2",
            "version": "15.2",
            "type": "switch",
            "runtime": "vrnetlab",
            "image_uri": "vrnetlab/cisco_viosl2:15.2",
            "cpu_min": 1,
            "memory_min": 768,
            "startup_time": 180,
            "console_type": "telnet",
            "default_credentials": {"username": "admin", "password": "admin"},
            "interfaces_definition": {"pattern": "GigabitEthernet0/{n}", "start": 0, "max": 16}
        },
        # Cisco IOSv 15.9.3 (CML - Direct QEMU)
        {
            "vendor_id": vendors["cisco"].id,
            "name": "iosv-cml",
            "display_name": "Cisco IOSv 15.9.3 (CML)",
            "version": "15.9.3.M3",
            "type": "router",
            "runtime": "qemu",
            "image_uri": "/app/images/qcow2/iosv-15.9.3.qcow2",
            "cpu_min": 1,
            "cpu_recommended": 1,
            "memory_min": 384,
            "memory_recommended": 512,
            "startup_time": 120,
            "console_type": "telnet",
            "default_credentials": {"username": "cisco", "password": "cisco"},
            "interfaces_definition": {"pattern": "GigabitEthernet0/{n}", "start": 0, "max": 7}
        },
        # Cisco IOSvL2 2020 (CML - Direct QEMU)
        {
            "vendor_id": vendors["cisco"].id,
            "name": "iosvl2-cml",
            "display_name": "Cisco IOSvL2 2020 (CML)",
            "version": "2020",
            "type": "switch",
            "runtime": "qemu",
            "image_uri": "/app/images/qcow2/iosvl2-2020.qcow2",
            "cpu_min": 1,
            "cpu_recommended": 1,
            "memory_min": 512,
            "memory_recommended": 768,
            "startup_time": 90,
            "console_type": "telnet",
            "default_credentials": {"username": "cisco", "password": "cisco"},
            "interfaces_definition": {"pattern": "GigabitEthernet0/{n}", "start": 0, "max": 15}
        },
        # Alpine Linux (host)
        {
            "vendor_id": vendors["linux"].id,
            "name": "alpine",
            "display_name": "Alpine Linux",
            "version": "3.19",
            "type": "host",
            "runtime": "docker",
            "image_uri": "alpine:3.19",
            "cpu_min": 1,
            "memory_min": 64,
            "startup_time": 2,
            "console_type": "ssh",
            "default_credentials": {"username": "root", "password": ""},
            "interfaces_definition": {"pattern": "eth{n}", "start": 0, "max": 8}
        },
        # Ubuntu (host)
        {
            "vendor_id": vendors["linux"].id,
            "name": "ubuntu",
            "display_name": "Ubuntu Server",
            "version": "24.04",
            "type": "host",
            "runtime": "docker",
            "image_uri": "ubuntu:24.04",
            "cpu_min": 1,
            "memory_min": 256,
            "startup_time": 3,
            "console_type": "ssh",
            "default_credentials": {"username": "root", "password": "ubuntu"},
            "interfaces_definition": {"pattern": "eth{n}", "start": 0, "max": 8}
        }
    ]

    for image_data in images_data:
        existing = db.query(Image).filter(
            Image.vendor_id == image_data["vendor_id"],
            Image.name == image_data["name"],
            Image.version == image_data["version"]
        ).first()

        if not existing:
            image = Image(**image_data)
            db.add(image)
            db.flush()  # Get the ID

            # Add tags
            if image.name in ["ceos", "srlinux"]:
                tag = ImageTag(image_id=image.id, tag="datacenter")
                db.add(tag)

            if image.name in ["frr", "srlinux", "alpine", "ubuntu"]:
                tag = ImageTag(image_id=image.id, tag="free")
                db.add(tag)

            if image.startup_time < 30:
                tag = ImageTag(image_id=image.id, tag="fast-boot")
                db.add(tag)

            # CML image tags
            if image.name in ["iosv-cml", "iosvl2-cml"]:
                cml_tag = ImageTag(image_id=image.id, tag="cml")
                db.add(cml_tag)
                ospf_tag = ImageTag(image_id=image.id, tag="ospf")
                db.add(ospf_tag)
                production_tag = ImageTag(image_id=image.id, tag="production-ready")
                db.add(production_tag)

    db.commit()
    print("✓ Images seeded successfully")


def run_seed():
    """Run all seed functions"""
    db = SessionLocal()
    try:
        print("Starting database seeding...")
        seed_vendors(db)
        seed_images(db)
        print("\n🌱 Database seeded successfully!")
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
