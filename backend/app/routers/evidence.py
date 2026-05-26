import uuid
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.database import get_db
from app.models.evidence import Evidence
from app.schemas.evidence import EvidenceRead, EvidenceUpdate

router = APIRouter()

UPLOAD_DIR = Path(settings.upload_dir)


def _ensure_upload_dir():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/", response_model=EvidenceRead, status_code=status.HTTP_201_CREATED)
async def upload_evidence(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    control_id: Optional[uuid.UUID] = Form(None),
    expiry_date: Optional[str] = Form(None),
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

    # Store file with UUID prefix to prevent collisions
    safe_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = UPLOAD_DIR / safe_filename

    with file_path.open("wb") as buf:
        shutil.copyfileobj(file.file, buf)

    file_size = file_path.stat().st_size

    evidence = Evidence(
        title=title,
        description=description,
        control_id=control_id,
        file_name=file.filename,
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
    db: AsyncSession = Depends(get_db),
):
    query = select(Evidence).order_by(Evidence.uploaded_at.desc())
    if control_id:
        query = query.where(Evidence.control_id == control_id)
    result = await db.execute(query)
    items = result.scalars().all()
    if status_filter:
        items = [e for e in items if e.status == status_filter]
    return items


@router.get("/{evidence_id}", response_model=EvidenceRead)
async def get_evidence(evidence_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Evidence).where(Evidence.id == evidence_id))
    evidence = result.scalar_one_or_none()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return evidence


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
