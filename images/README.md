# NEON Network OS Images

This directory contains network operating system images used by NEON for device emulation.

## Directory Structure

```
images/
└── qcow2/          # QEMU qcow2 disk images
    ├── iosv-*.qcow2       # Cisco IOSv router images
    ├── iosvl2-*.qcow2     # Cisco IOSvL2 switch images
    └── ...                # Other vendor images
```

## Obtaining CML Images

The `.qcow2` files in this directory are **not included in the repository** due to size and licensing.

### Cisco Modeling Labs (CML) Images

If you have a Cisco CML/VIRL license, you can obtain these images:

1. **Cisco IOSv (Router)**
   - Download from Cisco CML image repository
   - Typical size: 50-60 MB
   - Place in: `images/qcow2/iosv-15.9.3.qcow2` (or your version)

2. **Cisco IOSvL2 (Switch)**
   - Download from Cisco CML image repository
   - Typical size: 80-90 MB
   - Place in: `images/qcow2/iosvl2-2020.qcow2` (or your version)

### Image Sources

- **Cisco CML/VIRL**: Official Cisco images (requires license)
- **EVE-NG**: Compatible qcow2 images
- **GNS3**: Some images can be converted to qcow2 format

## Adding New Images

1. Place `.qcow2` files in `images/qcow2/`
2. Update `backend/app/db/seed.py` with image metadata:
   ```python
   {
       "vendor_id": vendors["cisco"].id,
       "name": "your-image-name",
       "display_name": "Cisco Your Image",
       "version": "1.0",
       "type": "router",  # or "switch", "firewall", etc.
       "runtime": "qemu",
       "image_uri": "/app/images/qcow2/your-image.qcow2",
       "cpu_min": 1,
       "cpu_recommended": 1,
       "memory_min": 512,
       "memory_recommended": 1024,
       "startup_time": 120,  # seconds
       "console_type": "telnet",
       "default_credentials": {"username": "admin", "password": "admin"},
       "interfaces_definition": {"pattern": "GigabitEthernet0/{n}", "start": 0, "max": 7}
   }
   ```
3. Reseed database: `docker-compose exec backend python -m app.db.seed`

## Docker Volume Mount

The `images/` directory is mounted read-only in the backend container:

```yaml
# docker-compose.yml
volumes:
  - ./images:/app/images:ro
```

This allows NEON to access images without copying them into the container.

## License Notice

**IMPORTANT**: Cisco IOS images are proprietary and require valid licensing from Cisco.

- Do not distribute Cisco images without proper authorization
- Ensure compliance with Cisco licensing terms
- CML/VIRL subscriptions include image access

## Support

For image-related issues:
- Check image path in seed.py matches actual file location
- Verify file permissions (must be readable by Docker)
- Ensure sufficient disk space for image files
- Check logs: `docker-compose logs backend`
