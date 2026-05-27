import uuid
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import get_current_user, require_admin
from .. import models, schemas

router = APIRouter(prefix="/bookings", tags=["bookings"])


def generate_ref() -> str:
    year = datetime.utcnow().year
    suffix = str(uuid.uuid4().int)[:4].zfill(4)
    return f"KW-{year}-{suffix}"


@router.post("", response_model=schemas.BookingOut)
def create_booking(
    body: schemas.BookingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    nights = max(1, (body.check_out - body.check_in).days)
    total_price = 0.0

    if body.room_id:
        room = db.query(models.Room).filter(
            models.Room.id == body.room_id,
            models.Room.is_available == True,
        ).first()
        if not room:
            raise HTTPException(status_code=404, detail="Room not found or unavailable")
        total_price += float(room.price) * nights

    if body.package_id:
        pkg = db.query(models.Package).filter(
            models.Package.id == body.package_id,
            models.Package.is_active == True,
        ).first()
        if not pkg:
            raise HTTPException(status_code=404, detail="Package not found or inactive")
        total_price += float(pkg.price)

    if total_price == 0:
        raise HTTPException(status_code=400, detail="No valid room or package selected")

    booking = models.Booking(
        **body.model_dump(),
        user_id=current_user.id,
        booking_ref=generate_ref(),
        status="pending",
        total_price=total_price,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.get("/me", response_model=List[schemas.BookingOut])
def my_bookings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.Booking)
        .filter(models.Booking.user_id == current_user.id)
        .order_by(models.Booking.created_at.desc())
        .all()
    )


@router.get("", response_model=List[schemas.BookingOut])
def all_bookings(db: Session = Depends(get_db), _=Depends(require_admin)):
    return db.query(models.Booking).order_by(models.Booking.created_at.desc()).all()


@router.patch("/{booking_id}/status", response_model=schemas.BookingOut)
def update_status(
    booking_id: str,
    body: schemas.BookingStatusUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.status = body.status
    if body.admin_notes:
        booking.admin_notes = body.admin_notes
    db.commit()
    db.refresh(booking)
    return booking
