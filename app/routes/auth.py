import hmac
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import hash_password, verify_password, create_access_token
from ..config import settings
from ..deps import get_current_user
from .. import models, schemas

router = APIRouter(prefix="/auth", tags=["auth"])
log = logging.getLogger("kinkyworld.auth")


@router.post("/register", response_model=schemas.TokenResponse)
def register(body: schemas.RegisterRequest, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = models.User(
        email=body.email,
        full_name=body.full_name,
        phone=body.phone,
        hashed_password=hash_password(body.password),
        role="member",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    log.info(f"REGISTER success: id={user.id}")
    token = create_access_token({"sub": user.id})
    return {"access_token": token, "user": user}


@router.post("/login", response_model=schemas.TokenResponse)
def login(body: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    log.info(f"LOGIN success: id={user.id} role={user.role}")
    token = create_access_token({"sub": user.id})
    return {"access_token": token, "user": user}


@router.post("/admin-login", response_model=schemas.TokenResponse)
def admin_login(body: schemas.AdminLoginRequest, db: Session = Depends(get_db)):
    if not hmac.compare_digest(body.key, settings.ADMIN_KEY):
        raise HTTPException(status_code=401, detail="Invalid admin key")
    admin = db.query(models.User).filter(models.User.role == "admin").first()
    if not admin:
        raise HTTPException(status_code=500, detail="Admin account not configured")
    token = create_access_token({"sub": admin.id})
    return {"access_token": token, "user": admin}


@router.get("/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.post("/reset-password")
def reset_password(body: schemas.PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == body.email).first()
    if not user:
        return {"message": "If that email is registered, a reset link has been sent."}
    return {"message": "If that email is registered, a reset link has been sent."}
