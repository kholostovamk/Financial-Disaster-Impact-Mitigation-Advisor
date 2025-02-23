import io
import pypdfium2 as pdfium


def pdf_input(state: dict) -> dict:
    pdf_path = state["pdf"]
    with open(pdf_path, "rb") as f:
        return {"pdf_data": f.read()}

def pdf_parser(state: dict) -> dict:
    # convert pdf to images
    pdf_data = state["pdf_data"]
    pdf_path = state["pdf"]
    pdf = pdfium.PdfDocument(pdf_path)
    
    images = []
    for i in range(len(pdf)):
        page = pdf[i]
        image = page.render().to_pil()
        
        # Convert PIL image to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')  # You can use JPEG or other formats
        images.append(img_byte_arr.getvalue())
    
    return {"policy_images": images}
    
    
