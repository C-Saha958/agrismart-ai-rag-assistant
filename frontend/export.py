# export.py
import base64
from io import BytesIO
from fpdf import FPDF
from storage import load_db

def export_chat_pdf(cid):
    db = load_db()
    chat = db["chats"][cid]
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    safe_title = chat["title"].encode('latin-1', 'ignore').decode('latin-1')
    pdf.cell(200, 10, safe_title, ln=True)
    pdf.ln(5)
    for m in chat["messages"]:
        role = "User" if m["role"] == "user" else "Assistant"
        text = m['content'].replace("[Live]", "").replace("[Cached]", "").replace("Source:", "")
        safe_text = text.encode('latin-1', 'ignore').decode('latin-1')
        pdf.multi_cell(0, 8, f"{role}: {safe_text}")
        pdf.ln(2)
    pdf_bytes = pdf.output(dest="S").encode("latin-1", 'replace')
    return BytesIO(pdf_bytes)

def export_single_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    clean_text = text.replace("[Live]", "").replace("[Cached]", "")
    safe_text = clean_text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 8, safe_text)
    return BytesIO(pdf.output(dest="S").encode("latin-1", 'replace'))

def get_pdf_href(text, filename="response.pdf"):
    pdf_bytes = export_single_pdf(text)
    b64 = base64.b64encode(pdf_bytes.getvalue()).decode()
    return f'data:application/pdf;base64,{b64}'