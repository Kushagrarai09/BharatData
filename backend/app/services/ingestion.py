"""Transactional ingestion with dataset-aware keys and idempotent updates."""
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models import Source,IngestionJob,DataRecord,QualityCheck
from app.services.normalize import normalize_record,record_fingerprint

MANDI_RESOURCE_ID="9ef84268-d588-465a-a308-a864a43d0070"

def save_records(db: Session,provider: str,resource_id: str,records: list[dict]):
    source_name=f"{provider}:{resource_id}"
    source=db.query(Source).filter(Source.name==source_name).first()
    if not source:
        source=Source(name=source_name,source_type=provider,base_url="https://data.gov.in",resource_id=resource_id)
        db.add(source); db.flush()
    job=IngestionJob(source_id=source.id,provider=provider,status="running")
    db.add(job); db.flush()
    new_records=0; updated_records=0
    try:
        for item in records:
            normalized=normalize_record(item,"mandi_prices" if resource_id==MANDI_RESOURCE_ID else None)
            metadata=normalized.get("payload",{}).get("_bharatdata",{})
            stable_identity=metadata.get("business_key") or record_fingerprint(item)
            existing=db.query(DataRecord).filter_by(source_id=source.id,fingerprint=stable_identity).first()
            if existing:
                existing.payload=normalized["payload"]; existing.title=normalized["title"]
                existing.category=normalized["category"]; existing.record_date=normalized["record_date"]
                existing.source_url=normalized["source_url"]; existing.job_id=job.id
                existing.updated_at=datetime.now(timezone.utc); updated_records+=1
            else:
                db.add(DataRecord(source_id=source.id,job_id=job.id,fingerprint=stable_identity,**normalized))
                new_records+=1
        job.records_seen=len(records); job.records_saved=new_records; job.status="succeeded"
        job.finished_at=datetime.now(timezone.utc)
        db.add(QualityCheck(job_id=job.id,check_name="batch_integrity",
          passed=len(records)==0 or new_records+updated_records==len(records),
          details={"records_seen":len(records),"new_records":new_records,"updated_records":updated_records}))
        db.commit()
        return {"job_id":job.id,"records_seen":len(records),"new_records":new_records,
          "updated_records":updated_records,"status":job.status}
    except Exception:
        db.rollback()
        raise
