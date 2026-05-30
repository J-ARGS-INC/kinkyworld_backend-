from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import require_admin
from .. import models, schemas

router = APIRouter(prefix="/testimonials", tags=["testimonials"])


@router.get("", response_model=List[schemas.TestimonialOut])
def get_testimonials(db: Session = Depends(get_db)):
    return (
        db.query(models.Testimonial)
        .filter(models.Testimonial.is_active == True)
        .order_by(models.Testimonial.sort_order, models.Testimonial.created_at)
        .all()
    )


@router.get("/all", response_model=List[schemas.TestimonialOut])
def get_all_testimonials(db: Session = Depends(get_db), _=Depends(require_admin)):
    return (
        db.query(models.Testimonial)
        .order_by(models.Testimonial.sort_order, models.Testimonial.created_at)
        .all()
    )


@router.post("", response_model=schemas.TestimonialOut)
def create_testimonial(
    body: schemas.TestimonialCreate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    t = models.Testimonial(**body.model_dump())
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@router.patch("/{testimonial_id}", response_model=schemas.TestimonialOut)
def update_testimonial(
    testimonial_id: str,
    body: schemas.TestimonialUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    t = db.query(models.Testimonial).filter(models.Testimonial.id == testimonial_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Testimonial not found")
    for field, val in body.model_dump(exclude_unset=True).items():
        setattr(t, field, val)
    db.commit()
    db.refresh(t)
    return t


@router.delete("/{testimonial_id}")
def delete_testimonial(
    testimonial_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    t = db.query(models.Testimonial).filter(models.Testimonial.id == testimonial_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Testimonial not found")
    db.delete(t)
    db.commit()
    return {"ok": True}
