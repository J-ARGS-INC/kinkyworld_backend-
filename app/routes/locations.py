from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import require_admin
from .. import models, schemas

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("", response_model=List[schemas.LocationOut])
def get_locations(db: Session = Depends(get_db)):
    return db.query(models.Location).filter(models.Location.is_active == True).order_by(models.Location.country).all()


@router.get("/all", response_model=List[schemas.LocationOut])
def get_all_locations(db: Session = Depends(get_db), _=Depends(require_admin)):
    return db.query(models.Location).order_by(models.Location.country).all()


@router.post("", response_model=schemas.LocationOut)
def create_location(body: schemas.LocationCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    loc = models.Location(**body.model_dump())
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return loc


@router.put("/{location_id}", response_model=schemas.LocationOut)
def update_location(location_id: str, body: schemas.LocationUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    loc = db.query(models.Location).filter(models.Location.id == location_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(loc, k, v)
    db.commit()
    db.refresh(loc)
    return loc


@router.delete("/{location_id}")
def delete_location(location_id: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    loc = db.query(models.Location).filter(models.Location.id == location_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    db.delete(loc)
    db.commit()
    return {"ok": True}
