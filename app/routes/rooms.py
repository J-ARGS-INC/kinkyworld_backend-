import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import require_admin
from ..config import settings
from .. import models, schemas

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("", response_model=List[schemas.RoomOut])
def get_rooms(db: Session = Depends(get_db)):
    return db.query(models.Room).filter(models.Room.is_available == True).order_by(models.Room.price).all()


@router.get("/all", response_model=List[schemas.RoomOut])
def get_all_rooms(db: Session = Depends(get_db), _=Depends(require_admin)):
    return db.query(models.Room).order_by(models.Room.price).all()


@router.get("/{slug}", response_model=schemas.RoomOut)
def get_room(slug: str, db: Session = Depends(get_db)):
    room = db.query(models.Room).filter(models.Room.slug == slug).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.patch("/{room_id}/price", response_model=schemas.RoomOut)
def update_price(room_id: str, body: schemas.RoomPriceUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    room.price = body.price
    db.commit()
    db.refresh(room)
    return room


@router.patch("/{room_id}/availability")
def toggle_availability(room_id: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    room.is_available = not room.is_available
    db.commit()
    return {"id": room.id, "is_available": room.is_available}


@router.patch("/{room_id}", response_model=schemas.RoomOut)
def update_room(room_id: str, body: schemas.RoomUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    for field, val in body.model_dump(exclude_unset=True).items():
        setattr(room, field, val)
    db.commit()
    db.refresh(room)
    return room


@router.post("/{room_id}/upload-image")
async def upload_room_image(
    room_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in (file.filename or "") else "jpg"
    if ext not in ("jpg", "jpeg", "png", "webp"):
        raise HTTPException(status_code=400, detail="Invalid file type")
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")
    filename = f"room_{room_id[:8]}_{uuid.uuid4().hex[:8]}.{ext}"
    path = os.path.join(settings.UPLOAD_DIR, filename)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    with open(path, "wb") as f:
        f.write(contents)
    url = f"/uploads/{filename}"
    images = list(room.images or [])
    images.append(url)
    room.images = images
    db.commit()
    db.refresh(room)
    return {"url": url, "images": room.images}
