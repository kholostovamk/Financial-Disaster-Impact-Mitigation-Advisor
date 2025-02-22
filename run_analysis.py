from pathlib import Path
from insurance_analyzer import InsuranceDocumentAnalyzer, DocumentError

def main():
    analyzer = InsuranceDocumentAnalyzer()
    file_path = Path("ExamplePolicy2.pdf")
    
    try:
        extracted_text = analyzer.process_document(file_path)
        print("\nExtracted Text:\n")
        print(extracted_text)  # Debugging Step
        
    except DocumentError as e:
        print(f"Error processing document: {e}")

if __name__ == "__main__":
    main()
