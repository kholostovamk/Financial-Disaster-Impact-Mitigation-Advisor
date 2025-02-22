import logging
import re
from abc import ABC, abstractmethod
from word2number import w2n
import json
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path
import docx
from PyPDF2 import PdfReader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class Coverage:
    """Data class to store coverage information."""
    type: str                   # E.g., "Life Insurance", "Health Insurance"
    amount: Optional[float]     # Parsed numerical amount; None if parsing fails
    amount_text: str            # Original text that contains the amount
    details: str                # Additional details (if any)

@dataclass
class CustomerInfo:
    """Data class to store customer information."""
    name: str
    policy_number: str
    effective_date: str

class DocumentError(Exception):
    """Custom exception for document processing errors."""
    pass

class DocumentProcessor(ABC):
    """Abstract base class for document processing."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def extract_text(self, file_path: Path) -> str:
        """Extract text from document."""
        pass

    def validate_file(self, file_path: Path) -> None:
        """Validate that the file exists, is a file, and is not empty."""
        self.logger.debug(f"Validating file: {file_path}")
        if not file_path.exists() or not file_path.is_file():
            self.logger.error(f"Invalid file path: {file_path}")
            raise DocumentError(f"Invalid file path: {file_path}")
        if file_path.stat().st_size == 0:
            self.logger.error(f"File is empty: {file_path}")
            raise DocumentError(f"File is empty: {file_path}")
        self.logger.debug(f"File validation passed: {file_path}")

class PDFProcessor(DocumentProcessor):
    """PDF document processor."""
    
    def extract_text(self, file_path: Path) -> str:
        """Extract text from PDF document."""
        self.logger.info(f"Extracting text from PDF: {file_path}")
        self.validate_file(file_path)
        try:
            reader = PdfReader(file_path)
            if len(reader.pages) == 0:
                self.logger.error("PDF file contains no pages")
                raise DocumentError("PDF file contains no pages")
            
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            
            if not text.strip():
                self.logger.error("No text content found in PDF")
                raise DocumentError("No text content found in PDF")
            
            self.logger.debug(f"Successfully extracted text from {len(reader.pages)} pages")
            return text
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF: {e}", exc_info=True)
            raise DocumentError(f"Failed to extract text from PDF: {e}")

class DOCXProcessor(DocumentProcessor):
    """DOCX document processor."""
    
    def extract_text(self, file_path: Path) -> str:
        """Extract text from DOCX document."""
        self.logger.info(f"Extracting text from DOCX: {file_path}")
        self.validate_file(file_path)
        try:
            self.logger.debug("Opening DOCX document")
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                if paragraph.text:
                    text += paragraph.text + "\n"
            
            if not text.strip():
                self.logger.error("No text content found in DOCX")
                raise DocumentError("No text content found in DOCX")
            return text
        except Exception as e:
            self.logger.error(f"Error processing DOCX: {e}", exc_info=True)
            raise DocumentError(f"Error processing DOCX: {e}")

class CoverageAnalyzer:
    """Analyzes document text to extract coverage information."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def _parse_amount(self, amount_text: str) -> tuple[Optional[float], str]:
        """
        Parse an amount from text, handling both numeric and word-based formats.
        Returns a tuple: (numeric_amount, original_amount_text).
        """
        cleaned_text = amount_text.strip().lower()
        original_text = amount_text.strip()
        
        # Try numeric extraction: e.g., "$1,234.56"
        numeric_pattern = r"\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)"
        match = re.search(numeric_pattern, cleaned_text)
        if match:
            try:
                numeric_value = float(match.group(1).replace(",", ""))
                # Check for multipliers following the number (e.g., "thousand")
                multipliers = {"thousand": 1000, "million": 1000000, "billion": 1000000000}
                remaining_text = cleaned_text[match.end():].strip()
                for word, multiplier in multipliers.items():
                    if remaining_text.startswith(word):
                        numeric_value *= multiplier
                        break
                return numeric_value, original_text
            except ValueError:
                pass
        
        # Try word-to-number conversion for written amounts
        number_text = cleaned_text.replace("dollars", "").replace("$", "").strip()
        try:
            numeric_value = w2n.word_to_num(number_text)
            return float(numeric_value), original_text
        except ValueError as e:
            self.logger.warning(f"Failed to parse written number '{number_text}': {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error parsing '{number_text}': {e}", exc_info=True)
        
        return None, original_text
    
    def extract_coverage_details(self, text: str) -> List[Coverage]:
        self.logger.debug("Starting coverage pattern analysis")
        coverages = []
        
        # First, extract limits from the declarations section.
        declaration_limits = extract_declaration_limits(text)
        self.logger.debug(f"Extracted declaration limits: {declaration_limits}")
        
        # Revised pattern to capture headers like "COVERAGE C - Personal Property"
        general_pattern = r"(?i)coverage\s*([A-Z])\s*[-–]\s*([\w\s']+)"
        
        for match in re.finditer(general_pattern, text):
            coverage_letter = match.group(1).strip()
            coverage_description = match.group(2).strip()
            
            # Create a key to look up the limit
            key = f"Coverage {coverage_letter}"
            numeric_value = declaration_limits.get(key)
            amount_text = f"${numeric_value:,.2f}" if numeric_value is not None else ""
            
            # If no limit is found in the declarations mapping, fall back to searching in the nearby block.
            if numeric_value is None:
                start = match.end()
                block = text[start:start+2000]
                dollar_amounts = re.findall(r"\$([\d,]+(?:\.\d{2})?)", block)
                if dollar_amounts:
                    numeric_value = float(dollar_amounts[0].replace(",", ""))
                    amount_text = "$" + dollar_amounts[0]
            
            coverages.append(Coverage(
                type=f"Coverage {coverage_letter} - {coverage_description}",
                amount=numeric_value,
                amount_text=amount_text,
                details="Extracted using header and declarations mapping" if numeric_value is not None else "Extracted from contract header block"
            ))
        
        if not coverages:
            self.logger.warning("No coverage information found in document")
            raise DocumentError("No coverage information found in document")
        
        return coverages



    def analyze_text(self, text: str) -> tuple[CustomerInfo, List[Coverage]]:
        self.logger.info("Starting document text analysis")
        self.logger.debug(f"Analyzing text of length: {len(text)}")
        if not text.strip():
            raise DocumentError("Document contains no text to analyze")
        
        customer = self.extract_customer_info(text)
        coverages = self.extract_coverage_details(text)
        
        return customer, coverages


    def extract_customer_info(self, text: str) -> CustomerInfo:
        """ Wrapper for the improved customer info extraction. """
        return extract_customer_info(text)

# Standalone function for customer info extraction (used in CoverageAnalyzer)
def extract_customer_info(text: str) -> CustomerInfo:
    """Extracts customer info using multiple patterns."""
    name_patterns = [
        r"(?i)Policy\s+Holder[:\s]+([A-Za-z\s]+)",
        r"(?i)Insured[:\s]+([A-Za-z\s]+)",
        r"(?i)Policyholder[:\s]+([A-Za-z\s]+)"
    ]
    policy_patterns = [
        r"(?i)Policy\s*(?:Number|#)[:\s]+([\w\d-]+)"
    ]
    date_patterns = [
        r"(?i)Effective\s*Date[:\s]+([\d]{4}-[\d]{2}-[\d]{2})",
        r"(?i)Effective\s*Date[:\s]+([A-Za-z]+\s+\d{1,2},\s+\d{4})"
    ]
    customer_name = "Unknown"
    policy_number = "Unknown"
    effective_date = "Unknown"
    for pat in name_patterns:
        m = re.search(pat, text)
        if m:
            customer_name = m.group(1).strip()
            break
    for pat in policy_patterns:
        m = re.search(pat, text)
        if m:
            policy_number = m.group(1).strip()
            break
    for pat in date_patterns:
        m = re.search(pat, text)
        if m:
            effective_date = m.group(1).strip()
            break
    return CustomerInfo(name=customer_name, policy_number=policy_number, effective_date=effective_date)


def extract_declaration_limits(text: str) -> dict:
    """
    Attempts to extract a mapping of coverage headers to monetary limits from the declarations section.
    For example, for HO-4 policies, it might map:
      "Coverage C" -> 1000, "Coverage D" -> 0 (if not found),
      "Coverage E" -> 100000, "Coverage F" -> 0, "Coverage G" -> 1000.
    This is a heuristic based on ordering within a specific block.
    """
    limits = {}
    # Look for the declarations block that mentions "Limit of Insurance Personal Property Group"
    declaration_pattern = r"(?i)Limit of\s+Insurance\s+Personal\s+Property\s+Group(.+?)(?=COVERAGE|$)"
    match = re.search(declaration_pattern, text, re.DOTALL)
    if match:
        block = match.group(1)
        # Find all dollar amounts in the block
        amounts = re.findall(r"\$[\s]*([\d,]+(?:\.\d{2})?)", block)
        # Define an ordered list of coverage keys based on typical HO-4 ordering
        keys = ["Coverage C", "Coverage D", "Coverage E", "Coverage F", "Coverage G"]
        for i, amt in enumerate(amounts):
            if i < len(keys):
                try:
                    limits[keys[i]] = float(amt.replace(",", ""))
                except ValueError:
                    limits[keys[i]] = None
    return limits




class ReportGenerator:
    """Generates a JSON report of insurance coverage."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def generate_report(self, customer: CustomerInfo, coverages: List[Coverage]) -> str:
        """Generate a JSON report with customer and coverage information."""
        self.logger.info("Generating insurance coverage report")
        self.logger.debug(f"Customer: {customer.name}, Policy: {customer.policy_number}")
        report_data = {
            "customer_information": {
                "name": customer.name,
                "policy_number": customer.policy_number,
                "effective_date": customer.effective_date
            },
            "coverage_details": []
        }
        
        for coverage in coverages:
            amount_display = (
                f"${coverage.amount:,.2f}" if coverage.amount is not None else "0.0"
            )
            self.logger.debug(f"Formatting coverage amount: {amount_display}")
            report_data["coverage_details"].append({
                "type": coverage.type,
                "amount": amount_display,
                "details": coverage.details
            })
        
        return json.dumps(report_data, indent=2)

class InsuranceDocumentAnalyzer:
    """Main class for analyzing insurance documents."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.pdf_processor = PDFProcessor()
        self.docx_processor = DOCXProcessor()
        self.analyzer = CoverageAnalyzer()
        self.report_generator = ReportGenerator()
    
    def process_document(self, file_path: Path) -> str:
        """
        Process an insurance document and generate a coverage report.
        
        Args:
            file_path: Path to the insurance document (PDF or DOCX).
        
        Returns:
            A JSON-formatted report summarizing the coverage.
        
        Raises:
            DocumentError: If there are issues processing the document.
        """
        if not isinstance(file_path, Path):
            file_path = Path(file_path)
        
        if file_path.suffix.lower() == ".pdf":
            processor = self.pdf_processor
        elif file_path.suffix.lower() in [".docx", ".doc"]:
            processor = self.docx_processor
        else:
            raise DocumentError(f"Unsupported file type: {file_path.suffix}")
        
        text = processor.extract_text(file_path)
        customer, coverages = self.analyzer.analyze_text(text)
        return self.report_generator.generate_report(customer, coverages)
