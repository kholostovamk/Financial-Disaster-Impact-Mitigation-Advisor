import asyncio
import streamlit as st
import requests
import folium
import base64
from pathlib import Path
import random
import pandas as pd
from workflow import insurance_analysis_workflow
from PIL import Image
import io
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable


# Example Inputs
inputs = {
    "image": "spacejoy-vOa-PSimwg4-unsplash - Copy.jpg",
    "pdf": "Home_Insurance_Policy.pdf",
    "location": {"latitude": 37.7749, "longitude": -122.4194},
}

# # Execute Workflow
# result = insurance_analysis_workflow.invoke(inputs)


# Async Function to Process Workflow with Streaming Updates
async def run_workflow(inputs):
    st.session_state["workflow_results"] = {}  # Reset previous results
    placeholder = st.empty()  # Create a placeholder to update UI in real-time

    async for event in insurance_analysis_workflow.astream(inputs, stream_mode="values"):
        st.session_state["workflow_results"].update(event)
        with placeholder.container():  # Update dynamically
            # st.subheader("📌 Live Workflow Updates")
            for key, value in st.session_state["workflow_results"].items():
                if key in ['policy_images' , 'image_data' , 'image']:
                    continue
                
                
                if key == 'objects':
                    st.subheader("Objects Identified:")
                    objects_df = pd.DataFrame(value)
                    # Apply table styling
                    st.dataframe(
                        objects_df.style.set_properties(
                            **{"background-color": "#F8F9FA", "color": "#333", "border-radius": "10px"}
                        )
                        .set_table_styles(
                            [
                                {"selector": "thead th", "props": [("background-color", "#007BFF"), ("color", "white"), ("font-size", "16px")]}
                            ]
                        )
                    )
                    
                if key == 'price_data':
                    st.subheader("Price Data:")
                    price_df = pd.DataFrame(value)
                    # Apply table styling
                    st.dataframe(
                        price_df.style.set_properties(
                            **{"background-color": "#F8F9FA", "color": "#333", "border-radius": "10px"}
                        )
                        .set_table_styles(
                            [
                                {"selector": "thead th", "props": [("background-color", "#007BFF"), ("color", "white"), ("font-size", "16px")]}
                            ]
                        )
                    )
                    
                
                if key == 'loss_prob_wrt_disastor':
                    st.subheader("Loss Probability with respect to each Disaster:")
                    loss_df = pd.DataFrame([
                        {"Disaster": disaster, "Item": item["name"], "Probability": item["probability"]}
                        for disaster, items in value.items()
                        for item in items
                    ])
                    

                    # Pivot DataFrame to set Items on x-axis and Disasters on y-axis
                    loss_df = loss_df.pivot(index="Disaster", columns="Item", values="Probability")
                    # Apply table styling
                    st.dataframe(
                        loss_df.style.set_properties(
                            **{"background-color": "#F8F9FA", "color": "#333", "border-radius": "10px"}
                        )
                        .set_table_styles(
                            [
                                {"selector": "thead th", "props": [("background-color", "#007BFF"), ("color", "white"), ("font-size", "16px")]}
                            ]
                        )
                    )
                    
                if key == 'disaster_probability':
                    
                    st.subheader("Disaster Probability:")
                    
                    disaster_list = [{"Disaster": k, "Probability": v} for k, v in value.items()]
                    
                    disaster_df = pd.DataFrame(disaster_list)
                    # Apply table styling
                    st.dataframe(
                        disaster_df.style.set_properties(
                            **{"background-color": "#F8F9FA", "color": "#333", "border-radius": "10px"}
                        )
                        .set_table_styles(
                            [
                                {"selector": "thead th", "props": [("background-color", "#007BFF"), ("color", "white"), ("font-size", "16px")]}
                            ]
                        )
                    )
                    
                if key == 'estimated_damage':
                    st.subheader("Estimated Damage:")
                    estimated_damage : float = value
                    
                    # create a red box with the value
                    st.markdown(
                        f"""
                        <div class="hover-card
                        " style="background-color: #FF0000; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1); width: 250px; height: 100px; position: relative;">
                            <div class="card-title
                            " style="font-size: 20px; font-weight: bold; color: white; text-align: center; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);">
                                {estimated_damage}
                            </div>
                            <div class="card-content
                            " style="font-size: 20px; color: #FF0000; text-align: center;">
                                Estimated Damage
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                if key == 'evaluation':
                    evaluation = value  # Extract the evaluation dictionary
    
                    st.subheader("📊 Evaluation Summary")

                    # Helper function for formatted display
                    def display_list(title, items, color):
                        if items:
                            st.markdown(f"### <span style='color:{color};'>{title}</span>", unsafe_allow_html=True)
                            for item in items:
                                st.markdown(f"- {item}")

                    # Use columns for better alignment
                    col1, col2 = st.columns(2)

                    with col1:
                        display_list("✅ Coverage", evaluation.get("coverage", []), "#2E8B57")  # Green
                        display_list("🚨 Red Flags", evaluation.get("red flags", []), "#DC143C")  # Red

                    with col2:
                        display_list("⚠️ Gaps", evaluation.get("gap", []), "#FF8C00")  # Orange
                        display_list("💚 Green Flags", evaluation.get("green flags", []), "#32CD32")  # Light Green
                                    
                                 
                                 
                if key == 'report':
                    st.subheader("📝 Report")
                    st.write(value)   
                    
                
                    
                    
                    
                # st.write(f"**{key}:**")
                # st.json(value)




# Set page config first
st.set_page_config(layout="wide")
st.markdown(
    "<h1 style='text-align: center; padding: 20px;'>🦖 HomeOnTheEdge 🦖</h1>", 
    unsafe_allow_html=True
)
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    st.markdown(
        f"""
        <style>
        [data-testid="stSidebar"] {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    
    
# Add custom CSS for hover cards
st.markdown("""
    <style>
    .hover-card {
        position: relative;
        cursor: pointer;
    }
    .card-content {
        display: none;
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(176, 218, 228, 0.95);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .hover-card:hover .card-content {
        opacity: 1;
    }
    .card-title {
        opacity: 1;
    }
    .hover-card:hover .card-title {
        opacity: 0;
    }
    </style>
""", unsafe_allow_html=True)

def add_bg_from_url(url):
    st.markdown(
        f"""
        <style>
        [data-testid="stSidebar"] {{
            background-image: url("{url}");
            background-size: cover;
            background-position: center;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Function to get latitude & longitude based on IP (for current location)
def search_location(search_query):
    """
    Search for a location and return its details using Nominatim geocoding service
    """
    try:
        geolocator = Nominatim(user_agent="my_streamlit_app")
        location = geolocator.geocode(search_query, exactly_one=True)
        
        if location:
            return {
                'city': location.address.split(',')[0],
                'region': location.address.split(',')[-2].strip() if len(location.address.split(',')) > 2 else "Unknown",
                'country': location.address.split(',')[-1].strip(),
                'latitude': str(location.latitude),
                'longitude': str(location.longitude)
            }
        else:
            return None
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        st.error(f"Error searching location: {e}")
        return None

# Add background from local file
add_bg_from_local('bg2.png')

# Initialize session state for tracking button clicks
if 'analyse_loss_clicked' not in st.session_state:
    st.session_state.analyse_loss_clicked = False

# Sidebar for location input and file upload
with st.sidebar:
    st.markdown("### 📍 Location Search")
    
    search_query = st.text_input("Enter location (e.g., city, address)", "")
    
    if st.button("Search Location"):
        if search_query:
            location_data = search_location(search_query)
            if location_data:
                st.session_state.location_data = location_data
            else:
                st.error("Location not found. Please try a different search term.")
        else:
            st.warning("Please enter a location to search.")

    uploaded_images = st.file_uploader("🖼 Upload Images", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
    if uploaded_images:
        st.session_state.uploaded_images = uploaded_images

    uploaded_file = st.file_uploader("📄 Upload a PDF", type="pdf")
    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file

# Main Section
if "location_data" in st.session_state and st.session_state.location_data:
    loc = st.session_state.location_data
    
    col1, col2, col3 = st.columns(3)

    # Column 1: Location
    with col1:
        st.markdown(
            f"""
            <div class="hover-card" style="background-color: #337487; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1); width: 250px; height: 100px; position: relative;">
                <div class="card-title" style="font-size: 20px; font-weight: bold; color: white; text-align: center; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);">
                    {loc['city']}, {loc['region']}, {loc['country']}
                </div>
                <div class="card-content">
                    <div style="font-size: 20px; color:#337487; text-align: center;">
                        📍 Location
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    # Column 2: Longitude
    with col2:
        st.markdown(
            f"""
            <div class="hover-card" style="background-color: #337487; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1); width: 250px; height: 100px; position: relative;">
                <div class="card-title" style="font-size: 20px; font-weight: bold; color: white; text-align: center; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);">
                    {loc['longitude']}
                </div>
                <div class="card-content">
                    <div style="font-size: 20px; color: #337487; text-align: center;">
                        🌍 Longitude
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    # Column 3: Latitude
    with col3:
        st.markdown(
            f"""
            <div class="hover-card" style="background-color: #337487; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1); width: 250px; height: 100px; position: relative;">
                <div class="card-title" style="font-size: 20px; font-weight: bold; color: white; text-align: center; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);">
                    {loc['latitude']}
                </div>
                <div class="card-content">
                    <div style="font-size: 20px; color: #337487; text-align: center;">  
                        🌍 Latitude
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Add separator after location cards
    st.markdown("---")
    # Create two columns for images and PDF file
    col1, col2 = st.columns(2)

    # Display Uploaded Images in the Left Column
    with col1:
        if "uploaded_images" in st.session_state and st.session_state.uploaded_images:
            st.markdown("### 🖼️ Uploaded Images:")
            cols = st.columns(len(st.session_state.uploaded_images))  # Create sub-columns for multiple images
            for idx, img in enumerate(st.session_state.uploaded_images):
                with cols[idx]:
                    st.image(img, width=150)  # Adjust image width for better fit
        else:
            st.warning("Please upload images to analyze the loss.")

    # Display Uploaded PDF File in the Right Column
    with col2:
        if "uploaded_file" in st.session_state and st.session_state.uploaded_file:
            st.markdown("### 📄 Uploaded Insurance PDF:")
            st.write(f"File Name: **{st.session_state.uploaded_file.name}**")
        else:
            st.warning("Please upload a PDF insurance policy to continue.")
    # Display uploaded PDF
   
    if "uploaded_file" in st.session_state and st.session_state.uploaded_file and "uploaded_images" in st.session_state and st.session_state.uploaded_images:
        # with st.container():
            # Remove the column layout and align everything to the left
            st.markdown("<br>", unsafe_allow_html=True)

            # Button to trigger the content display with a unique id
            if st.button("Am I covered?", key="covered-button"):
                
                location_data = st.session_state.location_data
                
                latitude = location_data['latitude']
                longitude = location_data['longitude']
                
                image = st.session_state.uploaded_images[0]
                
                
                image = Image.open(image)

                # Convert image to bytes    
                bytes_io = io.BytesIO()
                image.save(bytes_io, format=image.format)

                # Convert to required dictionary format
                image_data = list(bytes_io.getvalue())
                
                
                pdf = st.session_state.uploaded_file
                
                pdf_bytes = pdf.read()
                
                inputs = {
                    "image": image_data,
                    "pdf": pdf_bytes,
                    "location": {"latitude": latitude, "longitude": longitude},
                    "image_bytes" : True,
                    "pdf_bytes" : True
                    }    
                
                for _input , data in inputs.items():
                    print(f"{_input} : {type(data)}")
                    
                    
                asyncio.run(run_workflow(inputs))

    