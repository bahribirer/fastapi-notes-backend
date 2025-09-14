from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.services.summarizer import run_summarize, MAX_ATTEMPTS

from app.api.deps import get_db, get_current_user
from app.models.note import Note, NoteStatus
from app.models.user import User, UserRole
from app.schemas.note import NoteCreate, NoteOut

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("/", response_model=NoteOut)
def create_note(
    payload: NoteCreate,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 0) Idempotency key kontrolü
    if payload.idempotency_key:
        existing = db.query(Note).filter(
            Note.user_id == current_user.id,
            Note.idempotency_key == payload.idempotency_key
        ).first()
        if existing:
            return existing

    # 1) Notu queued olarak kaydet
    note = Note(
        raw_text=payload.raw_text,
        user_id=current_user.id,
        status=NoteStatus.queued,
        idempotency_key=payload.idempotency_key,
    )
    db.add(note)
    db.commit()
    db.refresh(note)

    # 2) Arka plana iş at
    background.add_task(run_summarize, note.id)

    return note


@router.get("/", response_model=List[NoteOut])
def list_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == UserRole.ADMIN:
        return db.query(Note).all()
    return db.query(Note).filter(Note.user_id == current_user.id).all()


@router.get("/{note_id}", response_model=NoteOut)
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if current_user.role != UserRole.ADMIN and note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    return note


@router.post("/{note_id}/retry", response_model=NoteOut)
def retry_note(
    note_id: int,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if current_user.role != UserRole.ADMIN and note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    # Eğer max deneme hakkı dolmuşsa artık retry etme
    if note.attempts >= MAX_ATTEMPTS:
        note.status = NoteStatus.failed
        db.commit()
        db.refresh(note)
        return note

    # Tekrar kuyruğa al
    note.status = NoteStatus.queued
    db.commit()
    db.refresh(note)

    # Arka plana yeni summarize işi ekle
    background.add_task(run_summarize, note.id)

    return note
