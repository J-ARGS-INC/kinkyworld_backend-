from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import require_admin
from .. import models, schemas

router = APIRouter(prefix="/contact", tags=["contact"])


@router.post("", response_model=schemas.ContactInquiryOut)
def submit_inquiry(body: schemas.ContactInquiryCreate, db: Session = Depends(get_db)):
    inquiry = models.ContactInquiry(**body.model_dump())
    db.add(inquiry)
    db.commit()
    db.refresh(inquiry)
    return inquiry


@router.get("", response_model=List[schemas.ContactInquiryOut])
def get_inquiries(db: Session = Depends(get_db), _=Depends(require_admin)):
    return (
        db.query(models.ContactInquiry)
        .order_by(models.ContactInquiry.created_at.desc())
        .all()
    )


@router.patch("/{inquiry_id}/read")
def mark_read(inquiry_id: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    inquiry = db.query(models.ContactInquiry).filter(models.ContactInquiry.id == inquiry_id).first()
    if inquiry:
        inquiry.is_read = True
        db.commit()
    return {"ok": True}


@router.delete("/{inquiry_id}")
def delete_inquiry(inquiry_id: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    inquiry = db.query(models.ContactInquiry).filter(models.ContactInquiry.id == inquiry_id).first()
    if inquiry:
        db.delete(inquiry)
        db.commit()
    return {"ok": True}
