import logging
from abc import ABC, abstractmethod
from word2number import w2n

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
import json
from dataclasses import dataclass
from typing import List, Dict, Union, Optional
from pathlib import Path
import docx
from PyPDF2 import PdfReader
import re

@dataclass
class Coverage:
    """Data class to store coverage information"""
    type: str  # Type of coverage (e.g., "Life", "Health", "Property")
    amount: Optional[float]  # Coverage amount, None if not specified numerically
    amount_text: str  # Original amount text as found in document
    details: str  # Additional coverage details

@dataclass
class CustomerInfo:
    """Data class to store customer information"""
    name: str
    policy_number: str
    effective_date: str

class DocumentError(Exception):
    """Custom exception for document processing errors"""
    pass

class DocumentProcessor(ABC):
    """Abstract base class for document processing"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def extract_text(self, file_path: Path) -> str:
        """Extract text from document"""
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
    """PDF document processor"""
    
    def extract_text(self, file_path: Path) -> str:
        """Extract text from PDF document"""
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
    """DOCX document processor"""
    
    def extract_text(self, file_path: Path) -> str:
        """Extract text from DOCX document"""
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
            raise DocumentError(f"Error processing DOCX: {str(e)}")

class CoverageAnalyzer:
    """Analyzes document text to extract coverage information"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def _parse_amount(self, amount_text: str) -> tuple[Optional[float], str]:
        """
        Parse amount from text, handling various formats
        Returns tuple of (numeric_amount, original_text)
        """
        # Remove any whitespace and convert to lowercase for consistent processing
        cleaned_text = amount_text.strip().lower()
        original_text = amount_text.strip()
        
        # Try to extract numeric value
        # Handle formats like "$1,234.56", "1234.56", "1,234", etc.
        numeric_pattern = r"\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)"
        match = re.search(numeric_pattern, cleaned_text)
        
        if match:
            try:
                # Remove commas and convert to float
                numeric_value = float(match.group(1).replace(",", ""))
                return numeric_value, original_text
            except ValueError:
                pass
        
        # Handle written amounts like "one million dollars" or "one hundred fifty thousand dollars"
        # Remove common words that might interfere with number parsing
        number_text = cleaned_text.replace("dollars", "").replace("$", "").strip()
        
        try:
            # Use word2number to parse written numbers
            numeric_value = w2n.word_to_num(number_text)
            return float(numeric_value), original_text
        except Exception:
            pass
        
        # Return None for numeric value if we could not parse it
        return None, original_text
    
    def analyze_text(self, text: str) -> tuple[CustomerInfo, List[Coverage]]:
        """
        Analyze document text to extract customer information and coverage details.
        Uses regex patterns to identify relevant information.
        """
        self.logger.info("Starting document text analysis")
        self.logger.debug(f"Analyzing text of length: {len(text)}")
        if not text.strip():
            raise DocumentError("Document contains no text to analyze")
        
        # Extract customer information
        name_pattern = r"Policy\s+Holder:\s*([^\n]+)"
        policy_pattern = r"Policy\s+Number:\s*([^\n]+)"
        date_pattern = r"Effective\s+Date:\s*([^\n]+)"
        
        name = re.search(name_pattern, text)
        policy_number = re.search(policy_pattern, text)
        effective_date = re.search(date_pattern, text)
        
        customer = CustomerInfo(
            name=name.group(1) if name else "Unknown",
            policy_number=policy_number.group(1) if policy_number else "Unknown",
            effective_date=effective_date.group(1) if effective_date else "Unknown"
        )
        
        # Extract coverage information
        self.logger.debug("Starting coverage pattern analysis")
        coverages = []
        
        # Common coverage types to look for
        coverage_types = [
            "Life Insurance",
            "Health Insurance",
            "Property Insurance",
            "Auto Insurance",
            "Liability Coverage",
            "Disability Insurance"
        ]
        
        for coverage_type in coverage_types:
            # Look for coverage type and associated amount
            coverage_pattern = fr"{coverage_type}.*?(?:Coverage|Amount|Limit):\s*(.*?)(?:\n|$)"
            coverage_matches = re.finditer(coverage_pattern, text, re.IGNORECASE | re.DOTALL)
            
            for match in coverage_matches:
                amount_text = match.group(1).strip()
                numeric_amount, original_amount_text = self._parse_amount(amount_text)
                
                # Look for additional details in the vicinity
                details_text = text[max(0, match.start() - 100):min(len(text), match.end() + 100)]
                details_pattern = r"Details?:|Description:|(Terms? and Conditions?:).*?(?=\n\n|\Z)"
                details_match = re.search(details_pattern, details_text, re.IGNORECASE | re.DOTALL)
                
                details = details_match.group(0) if details_match else "No additional details found"
                
                coverages.append(Coverage(
                    type=coverage_type,
                    amount=numeric_amount,
                    amount_text=original_amount_text,
                    details=details.strip()
                ))
        
        if not coverages:
            raise DocumentError("No coverage information found in document")
        
        return customer, coverages

class ReportGenerator:
    """Generates summary report of insurance coverage"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def generate_report(self, customer: CustomerInfo, coverages: List[Coverage]) -> str:
        """Generate a JSON report with customer and coverage information"""
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
                f"${coverage.amount:,.2f}" if coverage.amount is not None
                else coverage.amount_text
            )
            self.logger.debug(f"Formatting coverage amount: {amount_display}")
            
            coverage_data = {
                "type": coverage.type,
                "amount": amount_display,
                "details": coverage.details
            }
            report_data["coverage_details"].append(coverage_data)
        
        return json.dumps(report_data, indent=2)

class InsuranceDocumentAnalyzer:
    """Main class for analyzing insurance documents"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.pdf_processor = PDFProcessor()
        self.docx_processor = DOCXProcessor()
        self.analyzer = CoverageAnalyzer()
        self.report_generator = ReportGenerator()
    
    def process_document(self, file_path: Path) -> str:
        """
        Process an insurance document and generate a coverage report
        
        Args:
            file_path: Path to the insurance document (PDF or DOCX)
            
        Returns:
            str: Generated report summarizing the coverage
            
        Raises:
            DocumentError: If there are any issues processing the document
        """
        # Select appropriate processor based on file extension
        if not isinstance(file_path, Path):
            file_path = Path(file_path)
            
        if file_path.suffix.lower() == ".pdf":
            processor = self.pdf_processor
        elif file_path.suffix.lower() in [".docx", ".doc"]:
            processor = self.docx_processor
        else:
            raise DocumentError(f"Unsupported file type: {file_path.suffix}")
        
        # Extract text from document
        text = processor.extract_text(file_path)
        
        # Analyze text to extract customer info and coverages
        customer_info, coverages = self.analyzer.analyze_text(text)
        
        # Generate and return report
        return self.report_generator.generate_report(customer_info, coverages)