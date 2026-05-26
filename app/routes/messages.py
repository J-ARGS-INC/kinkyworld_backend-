from typing import List
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import get_current_user, require_admin
from ..auth import decode_token
from .. import models, schemas

router = APIRouter(prefix="/messages", tags=["messages"])


class ConnectionManager:
    def __init__(self):
        self.active: dict[str, WebSocket] = {}

    async def connect(self, user_id: str, ws: WebSocket):
        await ws.accept()
        self.active[user_id] = ws

    def disconnect(self, user_id: str):
        self.active.pop(user_id, None)

    async def send_to(self, user_id: str, data: dict):
        ws = self.active.get(user_id)
        if ws:
            try:
                await ws.send_json(data)
            except Exception:
                self.disconnect(user_id)


manager = ConnectionManager()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(ws: WebSocket, user_id: str, token: str = Query(None)):
    if not token:
        await ws.close(code=4001)
        return
    payload = decode_token(token)
    if not payload or payload.get("sub") != user_id:
        await ws.close(code=4001)
        return
    await manager.connect(user_id, ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)


@router.get("/conversations")
def get_conversations(db: Session = Depends(get_db), admin: models.User = Depends(require_admin)):
    all_users = (
        db.query(models.User)
        .filter(models.User.role != "admin")
        .order_by(models.User.created_at.desc())
        .all()
    )

    result = []
    for user in all_users:
        uid = user.id
        last_msg = (
            db.query(models.Message)
            .filter(
                (models.Message.from_user_id == uid) | (models.Message.to_user_id == uid)
            )
            .order_by(models.Message.created_at.desc())
            .first()
        )
        unread_count = (
            db.query(models.Message)
            .filter(models.Message.from_user_id == uid, models.Message.is_read == False)
            .count()
        )
        result.append({
            "user_id": uid,
            "full_name": user.full_name or user.email,
            "email": user.email,
            "is_active": user.is_active,
            "last_message": last_msg.content[:100] if last_msg else "",
            "last_message_at": last_msg.created_at.isoformat() if last_msg else None,
            "unread_count": unread_count,
        })

    # Users with messages first (sorted newest), then users without messages
    result.sort(key=lambda x: x["last_message_at"] or "", reverse=True)
    return result


@router.get("/conversation/{user_id}")
def get_conversation(user_id: str, db: Session = Depends(get_db), admin: models.User = Depends(require_admin)):
    msgs = (
        db.query(models.Message)
        .filter(
            (models.Message.from_user_id == user_id) | (models.Message.to_user_id == user_id)
        )
        .order_by(models.Message.created_at.asc())
        .all()
    )
    db.query(models.Message).filter(
        models.Message.from_user_id == user_id,
        models.Message.is_read == False,
    ).update({"is_read": True})
    db.commit()

    return [
        {
            "id": m.id,
            "content": m.content,
            "is_from_admin": m.is_from_admin,
            "created_at": m.created_at.isoformat(),
            "sender_name": m.sender.full_name if m.sender else "Support",
        }
        for m in msgs
    ]


@router.get("/me", response_model=List[schemas.MessageOut])
def my_messages(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    msgs = (
        db.query(models.Message)
        .filter(
            (models.Message.from_user_id == current_user.id) |
            (models.Message.to_user_id == current_user.id)
        )
        .order_by(models.Message.created_at.asc())
        .all()
    )
    result = []
    for m in msgs:
        out = schemas.MessageOut.model_validate(m)
        out.sender_name = m.sender.full_name if m.sender else "Support"
        result.append(out)
    return result


@router.post("", response_model=schemas.MessageOut)
async def send_message(
    body: schemas.MessageCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Account must be activated before messaging.")
    admin = db.query(models.User).filter(models.User.role == "admin").first()
    msg = models.Message(
        from_user_id=current_user.id,
        to_user_id=admin.id if admin else None,
        subject=body.subject,
        content=body.content,
        booking_id=body.booking_id,
        is_from_admin=False,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    if admin:
        await manager.send_to(admin.id, {
            "type": "new_message",
            "message": {
                "id": msg.id,
                "content": msg.content,
                "is_from_admin": False,
                "created_at": msg.created_at.isoformat(),
                "sender_name": current_user.full_name or current_user.email,
                "from_user_id": current_user.id,
            },
        })

    out = schemas.MessageOut.model_validate(msg)
    out.sender_name = current_user.full_name or current_user.email
    return out


@router.get("", response_model=List[dict])
def all_messages(db: Session = Depends(get_db), _=Depends(require_admin)):
    msgs = db.query(models.Message).order_by(models.Message.created_at.desc()).all()
    return [
        {
            "id": m.id,
            "from_user_id": m.from_user_id,
            "to_user_id": m.to_user_id,
            "subject": m.subject,
            "content": m.content,
            "is_from_admin": m.is_from_admin,
            "is_read": m.is_read,
            "created_at": m.created_at.isoformat(),
            "sender_name": m.sender.full_name if m.sender else "Unknown",
            "sender_email": m.sender.email if m.sender else None,
        }
        for m in msgs
    ]


@router.post("/reply", response_model=schemas.MessageOut)
async def admin_reply(
    body: schemas.AdminReplyCreate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin),
):
    msg = models.Message(
        from_user_id=admin.id,
        to_user_id=body.to_user_id,
        subject=body.subject,
        content=body.content,
        booking_id=body.booking_id,
        is_from_admin=True,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    db.query(models.Message).filter(
        models.Message.from_user_id == body.to_user_id,
        models.Message.is_read == False,
    ).update({"is_read": True})
    db.commit()

    await manager.send_to(body.to_user_id, {
        "type": "new_message",
        "message": {
            "id": msg.id,
            "content": msg.content,
            "is_from_admin": True,
            "created_at": msg.created_at.isoformat(),
            "sender_name": "Support",
        },
    })

    out = schemas.MessageOut.model_validate(msg)
    out.sender_name = "Support"
    return out
