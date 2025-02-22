import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from insurance_analyzer import (
    Coverage, CustomerInfo, DocumentError, PDFProcessor, DOCXProcessor,
    CoverageAnalyzer, ReportGenerator, InsuranceDocumentAnalyzer
)

# -------------------------------
# Test for Coverage dataclass
# -------------------------------
class TestCoverage(unittest.TestCase):
    def test_coverage_initialization(self):
        # Create a Coverage instance using the correct fields.
        coverage = Coverage(
            type="Health Insurance",
            amount=1000.00,
            amount_text="$1,000.00 USD",
            details="Basic coverage"
        )
        self.assertEqual(coverage.type, "Health Insurance")
        self.assertEqual(coverage.amount, 1000.00)
        self.assertEqual(coverage.amount_text, "$1,000.00 USD")
        self.assertEqual(coverage.details, "Basic coverage")

# -------------------------------
# Test for CustomerInfo dataclass
# -------------------------------
class TestCustomerInfo(unittest.TestCase):
    def test_customer_info_initialization(self):
        # CustomerInfo has fields: name, policy_number, effective_date.
        customer = CustomerInfo("John Doe", "123456", "2023-01-01")
        self.assertEqual(customer.name, "John Doe")
        self.assertEqual(customer.policy_number, "123456")
        self.assertEqual(customer.effective_date, "2023-01-01")

# -------------------------------
# Helper to create temporary files
# -------------------------------
def create_temp_file(suffix: str, content: bytes = b"dummy data"):
    tmp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    tmp_file.write(content)
    tmp_file.flush()
    tmp_file.close()
    return Path(tmp_file.name)

# -------------------------------
# Test PDFProcessor
# -------------------------------
class TestPDFProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = PDFProcessor()

    @patch('insurance_analyzer.PdfReader')
    def test_extract_text_from_pdf(self, mock_pdf_reader):
        # Mock PDFReader to simulate a PDF with one page returning sample text.
        mock_pdf_reader.return_value.pages = [Mock(extract_text=lambda: "Sample PDF content")]
        dummy_path = create_temp_file(".pdf")
        try:
            result = self.processor.extract_text(dummy_path)
            self.assertEqual(result, "Sample PDF content\n")
        finally:
            dummy_path.unlink()

    def test_validate_file_valid_pdf(self):
        dummy_path = create_temp_file(".pdf")
        try:
            self.processor.validate_file(dummy_path)
        finally:
            dummy_path.unlink()

# -------------------------------
# Test DOCXProcessor
# -------------------------------
class TestDOCXProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = DOCXProcessor()

    @patch('docx.Document')
    def test_extract_text_from_docx(self, mock_document):
        # Mock DOCX document content.
        mock_doc_instance = Mock()
        mock_doc_instance.paragraphs = [Mock(text="Sample DOCX content")]
        mock_document.return_value = mock_doc_instance
        dummy_path = create_temp_file(".docx")
        try:
            result = self.processor.extract_text(dummy_path)
            self.assertEqual(result, "Sample DOCX content\n")
        finally:
            dummy_path.unlink()

    def test_validate_file_valid_docx(self):
        dummy_path = create_temp_file(".docx")
        try:
            self.processor.validate_file(dummy_path)
        finally:
            dummy_path.unlink()

# -------------------------------
# Test CoverageAnalyzer
# -------------------------------
class TestCoverageAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = CoverageAnalyzer()

    def test_parse_amount_valid(self):
        amount, original_text = self.analyzer._parse_amount("$1,000.00 USD")
        self.assertEqual(amount, 1000.00)
        self.assertEqual(original_text, "$1,000.00 USD")

    def test_parse_amount_invalid(self):
        amount, original_text = self.analyzer._parse_amount("invalid amount")
        self.assertIsNone(amount)
        self.assertEqual(original_text, "invalid amount")

    def test_analyze_text(self):
        # Update sample text to include "Coverage" after each coverage type.
        sample_text = """
        Policy Holder: John Doe
        Policy Number: 123456
        Effective Date: 2023-01-01
        Coverage Details:
        Health Insurance Coverage: $1,000.00 USD
        Life Insurance Coverage: $500,000.00 USD
        """
        customer, coverages = self.analyzer.analyze_text(sample_text)
        self.assertEqual(customer.name, "John Doe")
        self.assertEqual(customer.policy_number, "123456")
        self.assertEqual(customer.effective_date, "2023-01-01")
        self.assertEqual(len(coverages), 2)
        # Instead of relying on order, check that both expected types are present
        types = {cov.type for cov in coverages}
        self.assertEqual(types, {"Health Insurance", "Life Insurance"})

# -------------------------------
# Test ReportGenerator
# -------------------------------
class TestReportGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = ReportGenerator()

    def test_generate_report(self):
        customer = CustomerInfo("John Doe", "123456", "2023-01-01")
        coverages = [
            Coverage(type="Health Insurance", amount=1000.00, amount_text="$1,000.00 USD", details="Basic health coverage"),
            Coverage(type="Life Insurance", amount=500000.00, amount_text="$500,000.00 USD", details="Standard life coverage")
        ]
        report = self.generator.generate_report(customer, coverages)
        report_data = json.loads(report)
        
        # Validate customer information
        self.assertEqual(report_data["customer_information"]["name"], "John Doe")
        self.assertEqual(report_data["customer_information"]["policy_number"], "123456")
        self.assertEqual(report_data["customer_information"]["effective_date"], "2023-01-01")
        
        # Validate coverage details
        self.assertEqual(len(report_data["coverage_details"]), 2)
        # Check that both coverage types are present
        types = {cov["type"] for cov in report_data["coverage_details"]}
        self.assertEqual(types, {"Health Insurance", "Life Insurance"})
        # Check specific amounts (as formatted strings)
        for cov in report_data["coverage_details"]:
            if cov["type"] == "Health Insurance":
                self.assertEqual(cov["amount"], "$1,000.00")
            elif cov["type"] == "Life Insurance":
                self.assertEqual(cov["amount"], "$500,000.00")
        
        # Additional text-based checks
        self.assertIn("John Doe", report)
        self.assertIn("Health Insurance", report)
        self.assertIn("1,000.00", report)
        self.assertIn("500,000.00", report)

# -------------------------------
# Test InsuranceDocumentAnalyzer
# -------------------------------
class TestInsuranceDocumentAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = InsuranceDocumentAnalyzer()

    @patch.object(PDFProcessor, 'extract_text')
    @patch.object(CoverageAnalyzer, 'analyze_text')
    @patch.object(ReportGenerator, 'generate_report')
    def test_process_document_pdf(self, mock_generate_report, mock_analyze_text, mock_extract_text):
        # Mock the chain of processing.
        mock_extract_text.return_value = "Sample text"
        mock_analyze_text.return_value = (
            CustomerInfo("John Doe", "123456", "2023-01-01"),
            [Coverage(type="Health Insurance", amount=1000.00, amount_text="$1,000.00 USD", details="Basic coverage")]
        )
        mock_generate_report.return_value = "Final report"
        
        result = self.analyzer.process_document(Path("test.pdf"))
        self.assertEqual(result, "Final report")

    def test_process_document_invalid_extension(self):
        with self.assertRaises(DocumentError):
            self.analyzer.process_document(Path("test.txt"))

if __name__ == '__main__':
    unittest.main()
