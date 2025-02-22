import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from insurance_analyzer import (
    Coverage, CustomerInfo, DocumentError, DocumentProcessor,
    PDFProcessor, DOCXProcessor, CoverageAnalyzer,
    ReportGenerator, InsuranceDocumentAnalyzer
)

class TestCoverage(unittest.TestCase):
    def test_coverage_initialization(self):
        coverage = Coverage("Health", 1000.00, "USD")
        self.assertEqual(coverage.type, "Health")
        self.assertEqual(coverage.amount, 1000.00)
        self.assertEqual(coverage.currency, "USD")

class TestCustomerInfo(unittest.TestCase):
    def test_customer_info_initialization(self):
        customer = CustomerInfo("John Doe", "123 Main St")
        self.assertEqual(customer.name, "John Doe")
        self.assertEqual(customer.address, "123 Main St")

class TestPDFProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = PDFProcessor()

    @patch('insurance_analyzer.PyPDF2.PdfReader')
    def test_extract_text_from_pdf(self, mock_pdf_reader):
        # Mock PDF content
        mock_pdf_reader.return_value.pages = [Mock(extract_text=lambda: "Sample PDF content")]
        
        result = self.processor.extract_text(Path("test.pdf"))
        self.assertEqual(result, "Sample PDF content")

    def test_validate_file_valid_pdf(self):
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = True
            with patch('pathlib.Path.suffix', '.pdf'):
                self.processor.validate_file(Path("test.pdf"))

    def test_validate_file_invalid_extension(self):
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = True
            with patch('pathlib.Path.suffix', '.txt'):
                with self.assertRaises(DocumentError):
                    self.processor.validate_file(Path("test.txt"))

class TestDOCXProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = DOCXProcessor()

    @patch('docx.Document')
    def test_extract_text_from_docx(self, mock_document):
        # Mock DOCX content
        mock_doc_instance = Mock()
        mock_doc_instance.paragraphs = [Mock(text="Sample DOCX content")]
        mock_document.return_value = mock_doc_instance
        
        result = self.processor.extract_text(Path("test.docx"))
        self.assertEqual(result, "Sample DOCX content\n")

    def test_validate_file_valid_docx(self):
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = True
            with patch('pathlib.Path.suffix', '.docx'):
                self.processor.validate_file(Path("test.docx"))

    def test_validate_file_invalid_extension(self):
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = True
            with patch('pathlib.Path.suffix', '.txt'):
                with self.assertRaises(DocumentError):
                    self.processor.validate_file(Path("test.txt"))

class TestCoverageAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = CoverageAnalyzer()

    def test_parse_amount_valid(self):
        amount, currency = self.analyzer._parse_amount("$1,000.00 USD")
        self.assertEqual(amount, 1000.00)
        self.assertEqual(currency, "USD")

    def test_parse_amount_invalid(self):
        amount, currency = self.analyzer._parse_amount("invalid amount")
        self.assertIsNone(amount)
        self.assertEqual(currency, "")

    def test_analyze_text(self):
        sample_text = """
        Customer Name: John Doe
        Address: 123 Main St
        Coverage Details:
        Health Insurance: $1,000.00 USD
        Life Insurance: $500,000.00 USD
        """
        customer, coverages = self.analyzer.analyze_text(sample_text)
        
        self.assertEqual(customer.name, "John Doe")
        self.assertEqual(customer.address, "123 Main St")
        self.assertEqual(len(coverages), 2)
        self.assertEqual(coverages[0].type, "Health Insurance")
        self.assertEqual(coverages[0].amount, 1000.00)
        self.assertEqual(coverages[0].currency, "USD")

class TestReportGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = ReportGenerator()

    def test_generate_report(self):
        customer = CustomerInfo("John Doe", "123 Main St")
        coverages = [
            Coverage("Health", 1000.00, "USD"),
            Coverage("Life", 500000.00, "USD")
        ]
        
        report = self.generator.generate_report(customer, coverages)
        
        self.assertIn("John Doe", report)
        self.assertIn("123 Main St", report)
        self.assertIn("Health", report)
        self.assertIn("1,000.00", report)
        self.assertIn("500,000.00", report)

class TestInsuranceDocumentAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = InsuranceDocumentAnalyzer()

    @patch.object(PDFProcessor, 'extract_text')
    @patch.object(CoverageAnalyzer, 'analyze_text')
    @patch.object(ReportGenerator, 'generate_report')
    def test_process_document_pdf(self, mock_generate_report, mock_analyze_text, mock_extract_text):
        # Mock the chain of processing
        mock_extract_text.return_value = "Sample text"
        mock_analyze_text.return_value = (
            CustomerInfo("John Doe", "123 Main St"),
            [Coverage("Health", 1000.00, "USD")]
        )
        mock_generate_report.return_value = "Final report"

        result = self.analyzer.process_document(Path("test.pdf"))
        self.assertEqual(result, "Final report")

    def test_process_document_invalid_extension(self):
        with self.assertRaises(DocumentError):
            self.analyzer.process_document(Path("test.txt"))

if __name__ == '__main__':
    unittest.main()