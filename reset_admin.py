"""Run once to force-reset admin credentials: python reset_admin.py"""
import sys
from app.database import SessionLocal
from app.auth import hash_password, verify_password
from app import models

EMAIL = "admin@kinkyworld.com"
PASSWORD = "89HoDk0pwqEjr5KZmQhiCUPuISMnfcq1"

db = SessionLocal()
try:
    admin = db.query(models.User).filter(models.User.role == "admin").first()
    hashed = hash_password(PASSWORD)
    if admin:
        admin.email = EMAIL
        admin.hashed_password = hashed
        admin.is_active = True
        db.commit()
        print(f"✓ Admin updated: {EMAIL}")
    else:
        db.add(models.User(
            email=EMAIL,
            full_name="Admin",
            hashed_password=hashed,
            role="admin",
            is_active=True,
        ))
        db.commit()
        print(f"✓ Admin created: {EMAIL}")

    ok = verify_password(PASSWORD, db.query(models.User).filter(models.User.email == EMAIL).first().hashed_password)
    print(f"✓ Password check: {'PASS' if ok else 'FAIL'}")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
finally:
    db.close()
