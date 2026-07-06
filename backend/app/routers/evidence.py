import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.database import get_db
from app.models.evidence import Evidence
from app.schemas.evidence import EvidenceRead, EvidenceUpdate

router = APIRouter()

UPLOAD_DIR = Path(settings.upload_dir)

# Accepted evidence file types. Keep this conservative — evidence is documents
# and images, not executables/archives that could carry payloads.
ALLOWED_EXTENSIONS = {
    ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp",
    ".txt", ".csv", ".log", ".json",
    ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
}
MAX_UPLOAD_BYTES = settings.max_upload_mb * 1024 * 1024
_CHUNK_SIZE = 1024 * 1024  # 1 MiB


def _ensure_upload_dir():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _sanitize_filename(filename: Optional[str]) -> str:
    """Strip any directory components and null bytes, returning a safe base name."""
    base = Path(filename or "").name.replace("\x00", "").strip()
    return base or "upload"


@router.post("/", response_model=EvidenceRead, status_code=status.HTTP_201_CREATED)
async def upload_evidence(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    control_id: Optional[uuid.UUID] = Form(None),
    expiry_date: Optional[str] = Form(None),
    client_id: Optional[uuid.UUID] = Form(None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    _ensure_upload_dir()
    # Parse expiry_date string
    from datetime import date as date_type
    parsed_expiry = None
    if expiry_date:
        try:
            parsed_expiry = date_type.fromisoformat(expiry_date)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid expiry_date format, expected YYYY-MM-DD")

    # Sanitize the client-supplied name and validate the extension allowlist.
    original_name = _sanitize_filename(file.filename)
    extension = Path(original_name).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type '{extension or 'unknown'}' is not allowed",
        )

    # Store file with UUID prefix to prevent collisions and path traversal.
    stored_filename = f"{uuid.uuid4()}_{original_name}"
    file_path = UPLOAD_DIR / stored_filename

    # Stream to disk in chunks, enforcing the size limit as we go so a huge
    # upload can't fill the disk before we notice.
    file_size = 0
    try:
        with file_path.open("wb") as buf:
            while chunk := await file.read(_CHUNK_SIZE):
                file_size += len(chunk)
                if file_size > MAX_UPLOAD_BYTES:
                    buf.close()
                    file_path.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=413,
                        detail=f"File exceeds the {settings.max_upload_mb} MB limit",
                    )
                buf.write(chunk)
    except HTTPException:
        raise
    except Exception:
        file_path.unlink(missing_ok=True)
        raise

    evidence = Evidence(
        title=title,
        description=description,
        control_id=control_id,
        client_id=client_id,
        file_name=original_name,
        file_path=str(file_path),
        file_size=file_size,
        mime_type=file.content_type or "application/octet-stream",
        expiry_date=parsed_expiry,
    )
    db.add(evidence)
    await db.commit()
    await db.refresh(evidence)
    return evidence


@router.get("/", response_model=List[EvidenceRead])
async def list_evidence(
    control_id: Optional[uuid.UUID] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    client_id: Optional[uuid.UUID] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    query = select(Evidence).order_by(Evidence.uploaded_at.desc())
    if control_id:
        query = query.where(Evidence.control_id == control_id)
    if client_id:
        query = query.where(Evidence.client_id == client_id)
    # status is a computed property (not a column), so apply limit/offset in SQL
    # only when not filtering by status; otherwise page after the Python filter.
    if status_filter:
        result = await db.execute(query)
        items = [e for e in result.scalars().all() if e.status == status_filter]
        return items[offset:offset + limit]
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{evidence_id}", response_model=EvidenceRead)
async def get_evidence(evidence_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Evidence).where(Evidence.id == evidence_id))
    evidence = result.scalar_one_or_none()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return evidence


@router.get("/{evidence_id}/download")
async def download_evidence(evidence_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Evidence).where(Evidence.id == evidence_id))
    evidence = result.scalar_one_or_none()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    file_path = Path(evidence.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Evidence file is missing from storage")
    return FileResponse(
        path=file_path,
        filename=evidence.file_name,
        media_type=evidence.mime_type or "application/octet-stream",
    )


@router.patch("/{evidence_id}", response_model=EvidenceRead)
async def update_evidence(evidence_id: uuid.UUID, body: EvidenceUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Evidence).where(Evidence.id == evidence_id))
    evidence = result.scalar_one_or_none()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(evidence, field, value)
    await db.commit()
    await db.refresh(evidence)
    return evidence


@router.delete("/{evidence_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_evidence(evidence_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Evidence).where(Evidence.id == evidence_id))
    evidence = result.scalar_one_or_none()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    # Delete file from disk
    file_path = Path(evidence.file_path)
    if file_path.exists():
        file_path.unlink()
    await db.delete(evidence)
    await db.commit()
