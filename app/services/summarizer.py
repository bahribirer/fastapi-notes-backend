from time import sleep
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.note import Note, NoteStatus

MAX_ATTEMPTS = 3


def _simple_summarize(text: str) -> str:
    text = (text or "").strip()
    if len(text) <= 120:
        return text
    return text[:117] + "..."


def run_summarize(note_id: int) -> None:
    db: Session = SessionLocal()
    try:
        note = db.query(Note).filter(Note.id == note_id).first()
        if not note:
            return

        if note.status not in (NoteStatus.queued, NoteStatus.processing):
            return

        # processing'e çek
        note.status = NoteStatus.processing
        db.commit()

        # "AI çağrısı" simülasyonu (2 saniye bekle)
        sleep(2)

        # Basit özet çıkarma
        summary = _simple_summarize(note.raw_text)

        # Başarılı sonuç
        note.summary = summary
        note.status = NoteStatus.done
        note.attempts += 1
        note.last_error = None
        db.commit()

    except Exception as e:
        # Hata durumunu yakala ve retry mekanizması uygula
        note = db.query(Note).filter(Note.id == note_id).first()
        if note:
            note.attempts += 1
            note.last_error = str(e)[:500]

            if note.attempts < MAX_ATTEMPTS:
                # yeniden queued yap → tekrar denenecek
                note.status = NoteStatus.queued
            else:
                # çok denendi → failed
                note.status = NoteStatus.failed

            db.commit()
    finally:
        db.close()
