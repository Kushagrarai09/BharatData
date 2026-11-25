import io
import pdfplumber

def extract_pdf(content: bytes):
    pages = []
    tables = []
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            pages.append({"page": page_number, "text": page.extract_text() or ""})
            for table in page.extract_tables() or []:
                tables.append({"page": page_number, "rows": table})
    return {"page_count": len(pages), "text": "\n\n".join(p["text"] for p in pages), "pages": pages, "tables": tables}
