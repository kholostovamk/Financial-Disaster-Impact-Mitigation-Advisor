from workflow import insurance_analysis_workflow

# Example Inputs
inputs = {
    "image": "spacejoy-vOa-PSimwg4-unsplash - Copy.jpg",
    "pdf": "pdf.pdf",
    "location": {"latitude": 37.7749, "longitude": -122.4194},
}

# Execute Workflow
result = insurance_analysis_workflow.invoke(inputs)

# # Print Results
# print(result)
