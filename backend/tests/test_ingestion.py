import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import DataRecord, IngestionJob
from app.services.ingestion import save_records, MANDI_RESOURCE_ID

@pytest.fixture
def db():
    engine=create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session=sessionmaker(bind=engine)()
    try: yield session
    finally:
        session.close()
        engine.dispose()

def test_mandi_repeat_import_updates_same_record(db):
    row={"state":"Maharashtra","district":"Nashik","market":"Nashik","commodity":"Onion","variety":"Red","grade":"FAQ","arrival_date":"25/11/2026","modal_price":"1500"}
    first=save_records(db,"data.gov.in",MANDI_RESOURCE_ID,[row])
    second=save_records(db,"data.gov.in",MANDI_RESOURCE_ID,[{**row,"modal_price":"1550"}])
    assert first["new_records"]==1
    assert second["new_records"]==0 and second["updated_records"]==1
    stored=db.query(DataRecord).all()
    assert len(stored)==1 and stored[0].payload["_bharatdata"]["modal_price"]=="1550.00"
    assert db.query(IngestionJob).count()==2
