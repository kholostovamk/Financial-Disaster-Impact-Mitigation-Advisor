import asyncio
from time import sleep
import streamlit as st
from typing import Dict, Any
from langgraph.graph import StateGraph, START
from typing_extensions import TypedDict
import requests
import json

# Define the state
class State(TypedDict):
    image_data: Any
    pdf_data: Any
    location: Any
    fips: int
    objects: Dict
    price_data: Dict
    loss_prob_wrt_disastor: dict
    policy_text: str
    disaster_probability: dict
    estimated_damage: dict
    coverage: dict
    gap: float
    report: str
    suggestions: list

# Streamlit Page Configuration
st.set_page_config(page_title="Insurance Analysis Workflow", layout="wide")

st.title("📊 Interactive Insurance Analysis Workflow")

# Graph
workflow = StateGraph(State)

# Define Processing Functions
def image_input(state: State, image_path) -> Dict:
    with open(image_path, "rb") as f:
        return {"image_data": f.read()}

def pdf_input(state: State, pdf_path) -> Dict:
    with open(pdf_path, "rb") as f:
        return {"pdf_data": f.read()}

def location_input(state: State, latitude, longitude) -> Dict:
    url = f'https://geo.fcc.gov/api/census/block/find?latitude={latitude}&longitude={longitude}&format=json'
    response = requests.get(url)
    data = response.json()
    fips = data['County']['FIPS']
    return {"fips": fips}

def object_detection(state: State) -> Dict:
    
    return {"objects": ["TV", "Sofa", "Table"]}

def price_estimation(state: State) -> Dict:
    return {"price_data": {"TV": 500, "Sofa": 700, "Table": 300}}

def loss_estimation(state: State) -> Dict:
    return {"loss_prob_wrt_disastor": {
        "TV": {"earthquake": 0.2, "tornado": 0.3, "floods": 0.5, "fires": 0.7},
        "Sofa": {"earthquake": 0.2, "tornado": 0.3, "floods": 0.5, "fires": 0.7},
        "Table": {"earthquake": 0.2, "tornado": 0.3, "floods": 0.5, "fires": 0.7}
    }}

def pdf_parser(state: State) -> Dict:
    return {"policy_text": "Sample insurance policy covering floods and fires."}

def disaster_probability_model(state: State) -> Dict:
    return {"disaster_probability": {"earthquake": 0.2, "tornado": 0.3, "floods": 0.5, "fires": 0.7}}

def disaster_loss_estimation(state: State) -> Dict:
    loss_prob_wrt_disastor = state["loss_prob_wrt_disastor"]
    disaster_probability = state["disaster_probability"]
    combined_loss = {k: sum([loss_prob_wrt_disastor[obj][k] * disaster_probability[k] for obj in loss_prob_wrt_disastor])
                     for k in disaster_probability}
    return {"estimated_damage": combined_loss}

def compare_insurance(state: State) -> Dict:
    estimated_damage = state["estimated_damage"]
    policy_text = state["policy_text"]
    coverage = {disaster: 1 if disaster in policy_text else 0 for disaster in estimated_damage}
    total_estimated_loss = sum(estimated_damage.values())
    total_covered = sum(coverage.values())
    return {"coverage": coverage, "gap": total_estimated_loss - total_covered}

def report_generation(state: State) -> Dict:
    gap = state["gap"]
    suggestions = []
    if gap > 0:
        suggestions.append("Consider increasing insurance coverage for uncovered disasters.")
    return {"report": "Insurance Analysis Report", "suggestions": suggestions}

# Register Nodes
workflow.add_node("object_detection", object_detection)
workflow.add_node("price_estimation", price_estimation)
workflow.add_node("loss_estimation", loss_estimation)
workflow.add_node("pdf_parser", pdf_parser)
workflow.add_node("disaster_probability_model", disaster_probability_model)
workflow.add_node("disaster_loss_estimation", disaster_loss_estimation)
workflow.add_node("compare_insurance", compare_insurance)
workflow.add_node("report_generation", report_generation)

# Define Start Points
workflow.add_edge(START, "object_detection")
workflow.add_edge(START, "pdf_parser")
workflow.add_edge(START, "disaster_probability_model")

# Image Processing Path
workflow.add_edge("object_detection", "price_estimation")
workflow.add_edge("price_estimation", "loss_estimation")

# Combine Loss and Disaster Probability
workflow.add_edge(["loss_estimation", "disaster_probability_model"], "disaster_loss_estimation")

# Compare with Insurance Policy
workflow.add_edge(["disaster_loss_estimation", "pdf_parser"], "compare_insurance")

# Generate Final Report
workflow.add_edge("compare_insurance", "report_generation")

# Compile Graph
compiled_workflow = workflow.compile()

# Sidebar Inputs
st.sidebar.header("📥 Input Data")

image_file = st.sidebar.file_uploader("Upload Image", type=["jpg", "png"])
pdf_file = st.sidebar.file_uploader("Upload PDF", type=["pdf"])
latitude = st.sidebar.number_input("Latitude", value=37.7749)
longitude = st.sidebar.number_input("Longitude", value=-122.4194)

result = {}

# Async Function to Process Workflow
async def run_workflow(inputs):
    results = {}
    async for event in compiled_workflow.astream(inputs, stream_mode="values"):
        results.update(event)
    return results

if st.sidebar.button("Run Workflow"):
    with st.spinner("Processing..."):
        inputs = {}
        if image_file:
            inputs["image_data"] = image_file.read()
        if pdf_file:
            inputs["pdf_data"] = pdf_file.read()
        inputs["location"] = {"latitude": latitude, "longitude": longitude}

        result = asyncio.run(run_workflow(inputs))
        # Display Results
        # st.subheader("📌 Workflow Output")
        # st.json(result)

        # # Graph Visualization
        # st.subheader("📈 Workflow Graph")
        # mermaid_code = compiled_workflow.get_graph(xray=True).draw_mermaid()
        # st.markdown(f"```mermaid\n{mermaid_code}\n```")

# Node-wise Outputs
if "objects" in result:
    st.subheader("🎯 Object Detection")
    st.json(result["objects"])

if "price_data" in result:
    st.subheader("💰 Price Estimation")
    st.json(result["price_data"])

if "loss_prob_wrt_disastor" in result:
    st.subheader("🌪 Loss Estimation")
    st.json(result["loss_prob_wrt_disastor"])

if "policy_text" in result:
    st.subheader("📑 Extracted Insurance Policy")
    st.text(result["policy_text"])

if "disaster_probability" in result:
    st.subheader("🔥 Disaster Probability Model")
    st.json(result["disaster_probability"])

if "estimated_damage" in result:
    st.subheader("🏚 Estimated Damage")
    st.json(result["estimated_damage"])

if "coverage" in result:
    st.subheader("📜 Insurance Coverage Analysis")
    st.json(result["coverage"])

if "report" in result:
    st.subheader("📋 Final Report")
    st.text(result["report"])
    st.subheader("💡 Suggestions")
    for suggestion in result["suggestions"]:
        st.markdown(f"- {suggestion}")

