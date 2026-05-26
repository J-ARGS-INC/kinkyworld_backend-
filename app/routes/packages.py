from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import require_admin
from .. import models, schemas

router = APIRouter(prefix="/packages", tags=["packages"])


@router.get("", response_model=List[schemas.PackageOut])
def get_packages(db: Session = Depends(get_db)):
    return db.query(models.Package).filter(models.Package.is_active == True).all()


@router.get("/all", response_model=List[schemas.PackageOut])
def get_all_packages(db: Session = Depends(get_db), _=Depends(require_admin)):
    return db.query(models.Package).all()


@router.patch("/{package_id}", response_model=schemas.PackageOut)
def update_package(
    package_id: str,
    body: schemas.PackageUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    pkg = db.query(models.Package).filter(models.Package.id == package_id).first()
    if not pkg:
        raise HTTPException(status_code=404, detail="Package not found")
    for field, val in body.model_dump(exclude_unset=True).items():
        setattr(pkg, field, val)
    db.commit()
    db.refresh(pkg)
    return pkg
