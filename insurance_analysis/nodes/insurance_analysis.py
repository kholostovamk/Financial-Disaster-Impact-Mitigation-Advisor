import json
import requests
from PIL import Image
import io

# import markdown
# from weasyprint import HTML

# def markdown_to_pdf(markdown_string, output_pdf):
#     html_content = markdown.markdown(markdown_string)

#     HTML(string=html_content).write_pdf(output_pdf)

# Cloudflare API credentials
ACCOUNT_ID = "70ce45de58b391cf496b21b7f4d82be0"
AUTH_TOKEN = "JWJ_5F6UAaMsD-sjF9blkYw2YHZmRjRFypilIBd5"
API_URL = (
    f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/"
)


def disaster_loss_estimation(state: dict) -> dict:
    loss_prob_wrt_disastor = state["loss_prob_wrt_disastor"]
    disaster_probability = state["disaster_probability"]
    objects = state["objects"]
    price_data = state["price_data"]
    
    objects = [object['name'] for object in objects]

    combined_loss = 0
    
    for disaster , item_prob in loss_prob_wrt_disastor.items():
        dis_prob = disaster_probability[disaster]
        for item in item_prob:
            item_name = item['name']
            
            for data in price_data:
                if data['name'] == item_name:
                    item_cost = data['cost']
                    break
            
            item_prob = item['probability']
            
            item_loss = item_cost * item_prob * dis_prob
            combined_loss += item_loss
    
    return {"estimated_damage": combined_loss}

def compare_insurance(state: dict) -> dict:
    estimated_damage = state["estimated_damage"]
    policy_images = state["policy_images"]
    disaster_probability = state["disaster_probability"]
    objects = state["objects"]
    
    
    model = "@cf/meta/llama-3.1-70b-instruct"
    
    system_prompt = '''
        You are an insurance policy evaluation system.
        You have insurance policy images, information about common disaster in area , and list of items in the house.
        You need to check that insurance policy covers everything in the house and if the damages are covered or not.
        Provide a list of coverage and gap, green flages and red flags about the policy in the following JSON format:
        {
            "coverage": [list of coverages],
            "gap": [list of gaps],
            "red flags": [list of red flags],
            "green flags": [list of green flags]
        }
    '''
    
    
    cost_of_object = 0
    for object in objects:
        cost_of_object += object['cost']
    
    
    prompt = f'''
    Information :
    Estimated Damage if disaster happens: {estimated_damage},
    Disaster Probability: {disaster_probability},
    Cost of things in house: {cost_of_object}
    '''
    
    response = requests.post(
        API_URL + model,
        headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
        json={
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "image": policy_images,
            "max_tokens": 10000,
            "response_format":{"type": "json"}
        }
    )
    
    print(response.json())
    
    
    # Process response
    result = response.json()
    response_text = result.get("result", {}).get("response", "")
    
    print(response_text)
    
    json_data_start = response_text.find("{")
    json_data_end = response_text.rfind("}") + 1
    
    print(response_text[json_data_start:json_data_end])

    evaluation = json.loads(response_text[json_data_start:json_data_end])
    
    print(evaluation)
    

    return {"evaluation": evaluation}

def report_generation(state: dict) -> dict:
    
    evaluation = state["evaluation"]
    
    model = "@cf/meta/llama-3.3-70b-instruct-fp8-fast"
    
    system_prompt = '''
        You are a Professional Report generator.
        You have insurance policy evaluation and you need to generate a report based on the evaluation.
        user markdown to generate the report.
        Provide a markdown string for the report.
        User proper formatting for the report.
    '''
    
    response = requests.post(
        API_URL + model,
        headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
        json={
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": str(evaluation)}
            ],
            "max_tokens": 10000,
            "response_format":{"type": "json"}
        }
    )
    
    result = response.json()
    
    print(result)
    
    response_text = result.get("result", {}).get("response", "")
    
    print(response_text)
    
    # markdown_to_pdf(response_text, "report.pdf")
    
    return {"report": response_text}

    