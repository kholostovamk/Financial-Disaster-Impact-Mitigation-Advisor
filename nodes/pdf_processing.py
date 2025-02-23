import io
import pypdfium2 as pdfium
import fitz
from io import BytesIO



def extract_text_from_pdf(pdf_bytes):
    """Extracts text from a given PDF file (provided as bytes)."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text("text")  # Extracts text from each page
    return text


def pdf_input(state: dict) -> dict:
    pdf_path = state["pdf"]
    pdf_bytes = state["pdf_bytes"]
    
    if pdf_bytes:
        return {"pdf_data": pdf_path}
    
    with open(pdf_path, "rb") as f:
        return {"pdf_data": f.read()}

def pdf_parser(state: dict) -> dict:
    # convert pdf to images
    policy_text = extract_text_from_pdf(state["pdf_data"])
    return {"policy_text": policy_text}
    
    
