from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models import Source, IngestionJob, DataRecord, QualityCheck
from app.services.normalize import normalize_record, record_fingerprint

def save_records(db: Session, provider: str, resource_id: str, records: list[dict]):
    source_name = f"{provider}:{resource_id}"
    source = db.query(Source).filter(Source.name == source_name).first()
    if not source:
        source = Source(name=source_name, source_type=provider, base_url="https://data.gov.in", resource_id=resource_id)
        db.add(source); db.flush()
    job = IngestionJob(source_id=source.id, provider=provider, status="running")
    db.add(job); db.flush(); saved = 0
    for item in records:
        normalized = normalize_record(item); fingerprint = record_fingerprint(item)
        existing = db.query(DataRecord).filter_by(source_id=source.id, fingerprint=fingerprint).first()
        if existing:
            existing.payload = item; existing.title = normalized["title"]; existing.category = normalized["category"]
            existing.record_date = normalized["record_date"]; existing.source_url = normalized["source_url"]
            existing.job_id = job.id; existing.updated_at = datetime.now(timezone.utc)
        else:
            db.add(DataRecord(source_id=source.id, job_id=job.id, fingerprint=fingerprint, **normalized)); saved += 1
    job.records_seen = len(records); job.records_saved = saved; job.status = "succeeded"
    job.finished_at = datetime.now(timezone.utc)
    db.add(QualityCheck(job_id=job.id, check_name="non_empty_batch", passed=len(records)>0, details={"records_seen":len(records),"new_records":saved}))
    db.commit()
    return {"job_id":job.id,"records_seen":len(records),"new_records":saved,"status":job.status}
