from app.services.normalize import clean_text, normalize_date, record_fingerprint, normalize_record

def test_clean_text(): assert clean_text("  hello   world ") == "hello world"
def test_normalize_date(): assert normalize_date("25-11-2026") == "2026-11-25"
def test_fingerprint_is_stable(): assert record_fingerprint({"a":1,"b":2}) == record_fingerprint({"b":2,"a":1})
def test_normalize_mandi_record():
    result = normalize_record({"Commodity":"Onion", "Arrival_Date":"25/11/2026"})
    assert result["title"] == "Onion"
    assert result["record_date"] == "2026-11-25"
