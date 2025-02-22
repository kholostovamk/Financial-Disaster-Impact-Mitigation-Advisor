# from pdf2image import convert_from_bytes
import io

def pdf_input(state: dict) -> dict:
    pdf_path = state["pdf"]
    with open(pdf_path, "rb") as f:
        return {"pdf_data": f.read()}

def pdf_parser(state: dict) -> dict:
    # pdf_bytes = state["pdf_data"]
    # images = convert_from_bytes(pdf_bytes, dpi=300)
    
    # image_data_list = []
    # for i, image in enumerate(images):
    #     img_byte_arr = io.BytesIO()
    #     image.save(img_byte_arr, format="PNG")
    #     image_data_list.append(list(img_byte_arr.getvalue()))  

    return {"policy_images": "Test"}
    
    
