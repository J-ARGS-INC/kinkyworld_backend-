import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import require_admin
from ..config import settings
from .. import models, schemas

router = APIRouter(prefix="/content", tags=["content"])


@router.post("/upload-image")
async def upload_content_image(
    page: str = Query(...),
    key: str = Query(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in (file.filename or "") else "jpg"
    if ext not in ("jpg", "jpeg", "png", "webp", "gif"):
        raise HTTPException(status_code=400, detail="Invalid file type")
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")
    filename = f"content_{uuid.uuid4().hex}.{ext}"
    path = os.path.join(settings.UPLOAD_DIR, filename)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    with open(path, "wb") as f:
        f.write(contents)
    url = f"/uploads/{filename}"

    item = db.query(models.SiteContent).filter(
        models.SiteContent.page == page,
        models.SiteContent.key == key,
    ).first()
    if not item:
        item = models.SiteContent(page=page, key=key, value=url, value_type="image")
        db.add(item)
    else:
        item.value = url
        item.value_type = "image"
    db.commit()
    return {"url": url, "page": page, "key": key}


@router.get("")
def get_all_content(db: Session = Depends(get_db)):
    items = db.query(models.SiteContent).all()
    result: dict = {}
    for item in items:
        if item.page not in result:
            result[item.page] = {}
        result[item.page][item.key] = {"value": item.value, "type": item.value_type}
    return result


@router.get("/{page}")
def get_page_content(page: str, db: Session = Depends(get_db)):
    items = db.query(models.SiteContent).filter(models.SiteContent.page == page).all()
    return {item.key: {"value": item.value, "type": item.value_type} for item in items}


@router.put("/{page}/{key}")
def update_content(
    page: str,
    key: str,
    body: schemas.SiteContentUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    item = db.query(models.SiteContent).filter(
        models.SiteContent.page == page,
        models.SiteContent.key == key,
    ).first()
    if not item:
        item = models.SiteContent(
            page=page, key=key,
            value=body.value,
            value_type=body.value_type or "text",
        )
        db.add(item)
    else:
        item.value = body.value
        if body.value_type:
            item.value_type = body.value_type
    db.commit()
    db.refresh(item)
    return {"page": item.page, "key": item.key, "value": item.value, "type": item.value_type}
