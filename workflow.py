from langgraph.graph import StateGraph, START, END
from state import State
from nodes.image_processing import *
from nodes.pdf_processing import *
from nodes.location_processing import *
from nodes.insurance_analysis import *

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
workflow.add_edge("object_detection", "price_estimation" )
workflow.add_edge("object_detection", "loss_estimation")

# PDF Parsing Path (B)
workflow.add_edge("pdf_input", "pdf_parser")

# Location & House Details Path (C)
workflow.add_edge("location_input", "disaster_probability_model")

# Combine Loss and Disaster Probability
workflow.add_edge(["loss_estimation","price_estimation", "disaster_probability_model"],"disaster_loss_estimation")

# Compare with Insurance Policy
workflow.add_edge(["disaster_loss_estimation","pdf_parser"], "compare_insurance")

# Generate Final Report
workflow.add_edge("compare_insurance", "report_generation")

# End the Task
workflow.add_edge("report_generation", END)

# Compile
insurance_analysis_workflow = workflow.compile()

png_bytes = insurance_analysis_workflow.get_graph(xray=True).draw_mermaid_png()

with open(f"Agent Graph.png", "wb") as f:
    f.write(png_bytes)
    


