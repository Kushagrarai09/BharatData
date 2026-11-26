from app.services.normalize import clean_text, normalize_date, normalize_amount, record_fingerprint, normalize_record, normalize_mandi_record, mandi_business_key

def test_clean_text(): assert clean_text("  hello   world ") == "hello world"
def test_normalize_date(): assert normalize_date("25-11-2026") == "2026-11-25"
def test_normalize_amount(): assert normalize_amount("₹1,250.50") == "1250.50"
def test_fingerprint_is_stable(): assert record_fingerprint({"a":1,"b":2}) == record_fingerprint({"b":2,"a":1})
def test_generic_record(): assert normalize_record({"title":"Notice","published_date":"25/11/2026"})["record_date"] == "2026-11-25"
def test_mandi_normalization():
    item={"state":"Maharashtra","district":"Nashik","market":"Nashik","commodity":"Onion","variety":"Red","grade":"FAQ","arrival_date":"25/11/2026","min_price":"1,000","max_price":"2,000","modal_price":"1,500"}
    row=normalize_mandi_record(item)
    assert row["category"] == "Agriculture / Mandi Prices"
    assert row["record_date"] == "2026-11-25"
    assert row["payload"]["_bharatdata"]["modal_price"] == "1500.00"
def test_mandi_business_key_ignores_mutable_price():
    item={"state":"Maharashtra","district":"Nashik","market":"Nashik","commodity":"Onion","variety":"Red","grade":"FAQ","arrival_date":"25/11/2026","modal_price":"1500"}
    assert mandi_business_key(item) == mandi_business_key({**item,"modal_price":"1550"})
