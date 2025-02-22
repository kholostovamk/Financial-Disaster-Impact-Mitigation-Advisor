import langgraph.graph as lg
from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
import requests
from typing_extensions import TypedDict
import json

class State(TypedDict):
    image: Any
    pdf: Any
    location: Any
    image_data: Any
    pdf_data: Any
    fips: int
    house_type: str
    objects: Dict
    price_data: Dict
    loss_prob_wrt_disastor : dict
    policy_text: str
    disaster_probability: dict
    estimated_damage: dict
    coverage: dict
    gap: float
    report: str
    suggestions: list
    
    
def image_input(state: State) -> Dict:
    image_path = state["image"]
    print("image_input")
    with open(image_path, "rb") as f:
        return {"image_data": f.read()}

def pdf_input(state: State) -> Dict:
    pdf_path = state["pdf"]
    print("pdf_input")
    with open(pdf_path, "rb") as f:
        return {"pdf_data": f.read()}
    
def location_input(state: State) -> Dict:
    latitude , longitude = state["location"]["latitude"], state["location"]["longitude"]
    
    url = f'https://geo.fcc.gov/api/census/block/find?latitude={latitude}&longitude={longitude}&format=json'


    response = requests.get(url)


    data = response.json()

    fips = data['County']['FIPS']
    
 
    return {"fips": fips}

# Mock functions for processing
def object_detection(state: State) -> Dict:
    image_data = state["image_data"]
    """Detects objects in an image and returns estimated value."""
    return {"objects": ["TV", "Sofa", "Table"] }

def price_estimation(state: State) -> Dict:
    objects = state["objects"]
    print("price_estimation")
    """Estimates total house content value."""
    return {"price_data": {"TV": 500, "Sofa": 700, "Table": 300}}

def loss_estimation(state: State) -> Dict:
    price_data = state['price_data']
    print("loss_estimation")
    """Estimates fractional loss due to disasters."""
    # returns the n (bumber of object) * 5 (number of disastoe) martix
    return {"loss_prob_wrt_disastor" : {"TV" : {"earthquake": 0.2, "tornado": 0.3, "floods": 0.5, "fires": 0.7},
            "Sofa" : {"earthquake": 0.2, "tornado": 0.3, "floods": 0.5, "fires": 0.7},
            "Table" : {"earthquake": 0.2, "tornado": 0.3, "floods": 0.5, "fires": 0.7}}}
    
    
def pdf_parser(state: State) -> Dict:
    pdf_data = state["pdf_data"]
    print("pdf_parser")
    """Parses insurance PDF and extracts text."""
    return {"policy_text": "Sample insurance policy covering floods and fires."}

def disaster_probability_model(state: State) -> Dict:
    location_data = state["fips"]
    print("disaster_probability_model")
    """Predicts probability of disasters based on location and house details."""
    return {"disaster_probability": {"earthquake": 0.2, "tornado": 0.3, "floods": 0.5, "fires": 0.7}}
    

def disaster_loss_estimation(state: State) -> Dict:
    loss_prob_wrt_disastor = state["loss_prob_wrt_disastor"]
    disaster_probability = state["disaster_probability"]
    print("disaster_loss_estimation")
    """Combines loss and probability to estimate risk-weighted damage."""
    combined_loss = {k: sum([loss_prob_wrt_disastor[obj][k] * disaster_probability[k] for obj in loss_prob_wrt_disastor])
                     for k in disaster_probability}
    return {"estimated_damage": combined_loss}

def compare_insurance(state: State) -> Dict:
    estimated_damage = state["estimated_damage"]
    policy_text = state["policy_text"]
    print("compare_insurance")
    """Compares estimated loss with insurance coverage."""
    covered_disasters = ["floods", "fires"]
    coverage = {disaster: 1 if disaster in policy_text else 0 for disaster in estimated_damage}
    
    total_estimated_loss = sum(estimated_damage.values())
    total_covered = sum(coverage.values())
    
    return {"coverage": coverage, "gap": total_estimated_loss - total_covered}


def report_generation(state: State) -> Dict:
    gap = state["gap"]
    print("report_generation")
    """Generates final report with suggestions."""
    suggestions = []
    if gap > 0:
        suggestions.append("Consider increasing insurance coverage for uncovered disasters.")
    return {"report": "Insurance Analysis Report", "suggestions": suggestions}


# Create LangGraph
workflow = StateGraph(State)

# Register nodes
workflow.add_node("object_detection", object_detection)
workflow.add_node("price_estimation", price_estimation)
workflow.add_node("loss_estimation", loss_estimation)
workflow.add_node("pdf_parser", pdf_parser)
workflow.add_node("disaster_probability_model", disaster_probability_model)
workflow.add_node("disaster_loss_estimation", disaster_loss_estimation)
workflow.add_node("compare_insurance", compare_insurance)
workflow.add_node("report_generation", report_generation)
workflow.add_node("image_input", image_input)
workflow.add_node("pdf_input", pdf_input)
workflow.add_node("location_input", location_input)

# Define start points
workflow.add_edge(START, "image_input")
workflow.add_edge(START, "pdf_input")
workflow.add_edge(START, "location_input")

# Image Processing Path (A)
workflow.add_edge("image_input", "object_detection")
workflow.add_edge("object_detection", "price_estimation")
workflow.add_edge("price_estimation", "loss_estimation")

# PDF Parsing Path (B)
workflow.add_edge("pdf_input", "pdf_parser")

# Location & House Details Path (C)
workflow.add_edge("location_input", "disaster_probability_model")

# Combine Loss and Disaster Probability
workflow.add_edge(["loss_estimation", "disaster_probability_model"],"disaster_loss_estimation")
# workflow.add_edge( "disaster_loss_estimation")


# Compare with Insurance Policy
workflow.add_edge(["disaster_loss_estimation","pdf_parser"], "compare_insurance")
# workflow.add_edge( "compare_insurance")

# Generate Final Report
workflow.add_edge("compare_insurance", "report_generation")

# End the Task
# workflow.add_edge("report_generation", END)

# Compile
insurance_analysis_workflow = workflow.compile()

png_bytes = insurance_analysis_workflow.get_graph(xray=True).draw_mermaid_png()

with open(f"Agent Graph.png", "wb") as f:
    f.write(png_bytes)
    
    
# Example Usage
inputs = {
    "image": "spacejoy-vOa-PSimwg4-unsplash.jpg",
    "pdf": "pdf.pdf",
    "location": {"latitude": 37.7749, "longitude": -122.4194},
}


result = insurance_analysis_workflow.invoke(inputs)
