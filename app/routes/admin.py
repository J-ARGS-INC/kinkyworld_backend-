from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..deps import require_admin
from .. import models

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
def get_stats(db: Session = Depends(get_db), _=Depends(require_admin)):
    total_bookings = db.query(func.count(models.Booking.id)).scalar()
    pending_bookings = db.query(func.count(models.Booking.id)).filter(models.Booking.status == "pending").scalar()
    confirmed = db.query(func.count(models.Booking.id)).filter(models.Booking.status == "confirmed").scalar()
    total_revenue = db.query(func.sum(models.Booking.total_price)).filter(
        models.Booking.status.in_(["confirmed", "completed"])
    ).scalar() or 0
    unread_messages = db.query(func.count(models.Message.id)).filter(
        models.Message.is_read == False,
        models.Message.is_from_admin == False,
    ).scalar()
    total_members = db.query(func.count(models.User.id)).filter(models.User.role != "admin").scalar()
    pending_activations = db.query(func.count(models.User.id)).filter(
        models.User.role != "admin",
        models.User.is_active == False,
    ).scalar()

    return {
        "total_bookings": total_bookings,
        "pending_bookings": pending_bookings,
        "confirmed_bookings": confirmed,
        "total_revenue": float(total_revenue),
        "unread_messages": unread_messages,
        "total_members": total_members,
        "pending_activations": pending_activations,
    }


@router.get("/users")
def get_users(db: Session = Depends(get_db), _=Depends(require_admin)):
    users = db.query(models.User).filter(models.User.role != "admin").order_by(models.User.created_at.desc()).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "is_active": u.is_active,
            "membership_since": u.membership_since.isoformat() if u.membership_since else None,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]


@router.patch("/users/{user_id}/role")
def update_user_role(user_id: str, body: dict, db: Session = Depends(get_db), _=Depends(require_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = body.get("role", user.role)
    db.commit()
    return {"id": user.id, "role": user.role}


@router.patch("/users/{user_id}/activate")
def activate_user(user_id: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True
    db.commit()
    return {"id": user.id, "is_active": True}


@router.patch("/users/{user_id}/deactivate")
def deactivate_user(user_id: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    return {"id": user.id, "is_active": False}
