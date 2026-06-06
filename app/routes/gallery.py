import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import require_admin
from ..config import settings
from .. import models, schemas

router = APIRouter(prefix="/gallery", tags=["gallery"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE_MB = 10


@router.get("", response_model=List[schemas.GalleryImageOut])
def get_gallery(db: Session = Depends(get_db)):
    return (
        db.query(models.GalleryImage)
        .filter(models.GalleryImage.is_active == True)
        .order_by(models.GalleryImage.sort_order)
        .all()
    )


@router.get("/admin", response_model=List[schemas.GalleryImageOut])
def get_gallery_admin(db: Session = Depends(get_db), _=Depends(require_admin)):
    return (
        db.query(models.GalleryImage)
        .order_by(models.GalleryImage.sort_order, models.GalleryImage.created_at)
        .all()
    )


@router.post("/upload", response_model=schemas.GalleryImageOut)
async def upload_image(
    file: UploadFile = File(...),
    title: str = Form(None),
    category: str = Form("general"),
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, WebP or GIF images are allowed")

    contents = await file.read()
    if len(contents) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File too large (max {MAX_SIZE_MB}MB)")

    ext = file.filename.rsplit(".", 1)[-1].lower()
    filename = f"{uuid.uuid4()}.{ext}"
    storage_path = os.path.join(settings.UPLOAD_DIR, filename)

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    with open(storage_path, "wb") as f:
        f.write(contents)

    image = models.GalleryImage(
        title=title,
        url=f"/uploads/{filename}",
        storage_path=storage_path,
        category=category,
        uploaded_by=admin.id,
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


@router.patch("/{image_id}", response_model=schemas.GalleryImageOut)
def update_image(
    image_id: str,
    body: schemas.GalleryImageUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    image = db.query(models.GalleryImage).filter(models.GalleryImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(image, field, value)
    db.commit()
    db.refresh(image)
    return image


@router.delete("/{image_id}")
def delete_image(image_id: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    image = db.query(models.GalleryImage).filter(models.GalleryImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    if image.storage_path and os.path.exists(image.storage_path):
        os.remove(image.storage_path)
    db.delete(image)
    db.commit()
    return {"ok": True}
