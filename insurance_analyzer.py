import sys
import re
import json
from pathlib import Path
import spacy
import docx
from PyPDF2 import PdfReader
from dataclasses import dataclass

# Data classes for holding extracted data.
@dataclass
class CustomerInfo:
    name: str
    policy_number: str
    effective_date: str

@dataclass
class Coverage:
    type: str    # e.g., "Coverage C - Personal Property"
    amount: str  # e.g., "$1,000.00"

def extract_declaration_limits(text: str) -> dict:
    """
    Attempts to extract coverage limits from the declarations section.
    Looks for a block starting with "Limit of Insurance Personal Property Group"
    and then extracts dollar amounts in the assumed order (Coverage C, D, E, F, G).
    """
    limits = {}
    declaration_pattern = r"(?i)Limit of\s+Insurance\s+Personal\s+Property\s+Group(.+?)(?=COVERAGE|$)"
    match = re.search(declaration_pattern, text, re.DOTALL)
    if match:
        block = match.group(1)
        # Find all dollar amounts in the block
        amounts = re.findall(r"\$[\s]*([\d,]+(?:\.\d{2})?)", block)
        keys = ["Coverage C", "Coverage D", "Coverage E", "Coverage F", "Coverage G"]
        for i, amt in enumerate(amounts):
            if i < len(keys):
                limits[keys[i]] = "$" + amt
    return limits

class InsuranceDocumentAnalyzer:
    """
    Analyzes insurance documents to extract customer information and coverage details.
    Combines line-based regex extraction with spaCy-based NLP where beneficial.
    """
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
    
    def clean_customer_name(self, raw_name: str) -> str:
        # Remove any newline characters and trailing tokens.
        cleaned = raw_name.splitlines()[0].strip()
        # Remove trailing tokens like "HO" (common in some headers)
        cleaned = re.sub(r'\s+HO\b.*$', '', cleaned)
        return cleaned
    
    def extract_customer_info(self, text: str) -> CustomerInfo:
        # Look for a line starting with "Insured:"; ignore lines containing "Shelter" (often part of company info)
        insured_matches = re.findall(r"(?i)^Insured[:\s]+(.+)$", text, re.MULTILINE)
        customer_name = "Unknown"
        for match in insured_matches:
            if "shelter" not in match.lower():
                customer_name = match.strip()
                break
        if customer_name == "Unknown" and insured_matches:
            customer_name = insured_matches[0].strip()
        customer_name = self.clean_customer_name(customer_name)
        
        # Extract policy number from a line like "Policy # A2345-01"
        policy_match = re.search(r"(?i)Policy\s*(?:Number|#)[:\s]+([\w\d-]+)", text)
        policy_number = policy_match.group(1).strip() if policy_match else "Unknown"
        
        # Extract effective date from a line beginning with "Effective:"
        effective_match = re.search(r"(?i)^Effective[:\s]+(.+)$", text, re.MULTILINE)
        effective_date = effective_match.group(1).strip() if effective_match else "Unknown"
        # Look for a proper date pattern within the effective date line (e.g., "February 12, 2024")
        date_in_effective = re.search(r"([A-Za-z]+\s+\d{1,2},\s+\d{4})", effective_date)
        if date_in_effective:
            effective_date = date_in_effective.group(1).strip()
        
        return CustomerInfo(name=customer_name, policy_number=policy_number, effective_date=effective_date)
    
    def extract_coverage_info(self, text: str) -> list:
        # First, extract declared limits from the declarations section.
        limits = extract_declaration_limits(text)
        coverages = []
        # Regex to capture coverage headers. This pattern may need adjustment depending on document formatting.
        pattern = re.compile(r"(?i)\bCoverage\s+([A-Z])\s*-\s*([A-Z][A-Za-z\s]+)")
        seen = set()
        for match in pattern.finditer(text):
            letter = match.group(1).strip()
            description = match.group(2).strip()
            key = f"Coverage {letter}"
            if key in seen:
                continue  # avoid duplicate entries
            seen.add(key)
            amount = limits.get(key, "Unknown")
            coverages.append(Coverage(type=f"Coverage {letter} - {description}", amount=amount))
        return coverages

def extract_text_from_pdf(file_path: Path) -> str:
    """Extract text from a PDF file using PyPDF2."""
    reader = PdfReader(str(file_path))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def extract_text_from_docx(file_path: Path) -> str:
    """Extract text from a DOCX file using python-docx."""
    doc = docx.Document(file_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_file>")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: File '{file_path}' does not exist.")
        sys.exit(1)
    
    ext = file_path.suffix.lower()
    if ext == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        text = extract_text_from_docx(file_path)
    else:
        print("Unsupported file type. Only PDF and DOCX are supported.")
        sys.exit(1)
    
    if not text.strip():
        print("No text could be extracted from the file.")
        sys.exit(1)
    
    analyzer = InsuranceDocumentAnalyzer()
    customer_info = analyzer.extract_customer_info(text)
    coverage_info = analyzer.extract_coverage_info(text)
    
    # Build the final JSON structure.
    data = {
        "customer_information": {
            "name": customer_info.name,
            "policy_number": customer_info.policy_number,
            "effective_date": customer_info.effective_date
        },
        "coverage_information": [
            {"type": cov.type, "amount": cov.amount} for cov in coverage_info
        ]
    }
    
    output_file = "extracted_data.json"
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Extracted data saved to '{output_file}'.")

if __name__ == "__main__":
    main()
