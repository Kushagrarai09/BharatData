from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models import Source, DataRecord, IngestionJob, Document
from app.schemas import DataGovIngestRequest, ApifyIngestRequest
from app.services.datagov import fetch_datagov
from app.services.apify import fetch_apify_dataset
from app.services.ingestion import save_records
from app.services.pdf_extract import extract_pdf
from app.core.config import settings

router = APIRouter(prefix="/api")

@router.get("/metrics")
def metrics(db: Session = Depends(get_db)):
    return {
        "sources": db.query(Source).count(),
        "records": db.query(DataRecord).count(),
        "jobs": db.query(IngestionJob).count(),
        "successful_jobs": db.query(IngestionJob).filter_by(status="succeeded").count(),
        "failed_jobs": db.query(IngestionJob).filter_by(status="failed").count(),
        "documents": db.query(Document).count(),
    }

@router.get("/sources")
def sources(db: Session = Depends(get_db)):
    return [{"id": s.id, "name": s.name, "type": s.source_type, "resource_id": s.resource_id}
            for s in db.query(Source).order_by(Source.id.desc()).all()]

@router.get("/jobs")
def jobs(db: Session = Depends(get_db), limit: int = Query(50, ge=1, le=200)):
    rows = db.query(IngestionJob).order_by(desc(IngestionJob.started_at)).limit(limit).all()
    return [{"id": j.id, "provider": j.provider, "status": j.status, "records_seen": j.records_seen,
             "records_saved": j.records_saved, "error": j.error_message, "started_at": j.started_at,
             "finished_at": j.finished_at} for j in rows]

@router.get("/records")
def records(db: Session = Depends(get_db), q: str | None = None, category: str | None = None,
            limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0)):
    query = db.query(DataRecord)
    if q:
        query = query.filter(DataRecord.title.ilike(f"%{q}%"))
    if category:
        query = query.filter(DataRecord.category.ilike(f"%{category}%"))
    rows = query.order_by(desc(DataRecord.updated_at)).offset(offset).limit(limit).all()
    return [{"id": r.id, "title": r.title, "category": r.category, "record_date": r.record_date,
             "payload": r.payload, "source_url": r.source_url} for r in rows]

@router.post("/ingestion/datagov")
async def ingest_datagov(body: DataGovIngestRequest, db: Session = Depends(get_db)):
    try:
        rows = await fetch_datagov(body.resource_id, body.limit, body.filters)
        return save_records(db, "data.gov.in", body.resource_id, rows)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))

@router.post("/ingestion/apify")
async def ingest_apify(body: ApifyIngestRequest, db: Session = Depends(get_db)):
    try:
        rows = await fetch_apify_dataset(body.resource_id, body.max_results, body.filters)
        return save_records(db, "apify", body.resource_id, rows)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))

@router.post("/documents/extract")
async def extract_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type != "application/pdf" and not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=415, detail="Only PDF files are supported in this version.")
    content = await file.read()
    if len(content) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.max_upload_mb} MB limit.")
    try:
        result = extract_pdf(content)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not parse PDF: {exc}")
    doc = Document(filename=file.filename or "uploaded.pdf", extracted_text=result["text"], page_count=result["page_count"])
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return {"document_id": doc.id, "filename": doc.filename, "page_count": result["page_count"],
            "text": result["text"], "tables": result["tables"]}
