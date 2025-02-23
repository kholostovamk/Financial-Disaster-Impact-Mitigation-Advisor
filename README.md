# 🏠 HouseOnTheEdge – AI-Powered Insurance Risk Assessment  

### **Bridging the gap between homeowners and insurance providers with AI-driven insights**  



## 🚀 Overview  

HouseOnTheEdge is an **AI-driven risk assessment tool** that helps homeowners and insurance companies evaluate insurance coverage based on property risk and natural disaster probabilities.  

This system leverages **natural language processing (NLP), computer vision, and machine learning** to analyze insurance policies, assess property conditions, and predict potential losses due to disasters like floods, earthquakes, and hurricanes.  

---

## 📌 Features  

✅ **AI-Powered Policy Analysis** – Extracts key details (coverage, exclusions, deductibles) from PDFs using NLP  
✅ **Property Risk Evaluation** – Analyzes uploaded house images to detect structural vulnerabilities  
✅ **Disaster Probability Modeling** – Uses machine learning to predict disaster risks based on historical weather data  
✅ **Coverage Comparison** – Highlights insurance gaps by comparing policy details with risk estimates  
✅ **Interactive Web UI** – Built with Streamlit for a seamless user experience  

---

## 🏗️ Architecture  

HouseOnTheEdge integrates multiple AI agents and machine learning models:  

### 🔹 **Pipeline Flow**  
1. **User Uploads Data**  
   - Insurance PDF & House Images  
2. **NLP Model Processes Policy Document**  
   - Extracts limits, deductibles, and exclusions  
3. **Computer Vision Model Analyzes House Images**  
   - Identifies property risks (e.g., poor roofing, weak structures)  
4. **Disaster Prediction Model Estimates Risks**  
   - Uses **NOAA & FEMA datasets** for disaster probability modeling  
5. **Coverage Analysis & Recommendations**  
   - Compares policy coverage with estimated risk  
6. **Interactive Report Generation**  
   - Provides a detailed breakdown of risks, losses & recommendations  

---

## 🛠️ Tech Stack  

| **Category**         | **Technology Used**                                      |
|----------------------|----------------------------------------------------------|
| **Languages**       | Python                                                   |
| **Frameworks**      | Streamlit (UI)                                           |
| **NLP Models**      | spaCy, transformers (LLMs)                               |
| **ML Models**       | XGBoost, MultiOutputClassifier                           |
| **Computer Vision** | OpenCV, Multimodal Models                                |
| **Data Sources**    | NOAA API, FEMA Disaster Summaries                        |
| **Cloud & APIs**    | Various external APIs for disaster data                  |
| **Data Processing** | pandas, NumPy                                            |

---

## 🖥️ Installation & Setup  

### **🔹 Prerequisites**  
Ensure you have **Python 3.8+** installed.  

### **🔹 Clone the Repository**  
```bash
git clone https://github.com/yourusername/HouseOnTheEdge.git
cd HouseOnTheEdge
```

### **🔹 Install Dependencies**  
```bash
pip install -r requirements.txt
```

### **🔹 Run the Application**  
```bash
streamlit run app.py
```

---

## 📊 Dataset Sources  

HouseOnTheEdge relies on publicly available datasets to train its risk prediction models:  

- **FEMA Disaster Summaries** – Historical disaster impact data  
- **NOAA API** – Climate and weather data for disaster modeling  
- **External property risk datasets** (for structural assessment)  

---

## 🔥 Challenges & Solutions  

### 🔹 **Challenges We Faced**  
- **Parsing Unstructured Policy PDFs** – Transitioned from regex-based extraction to NLP models for flexible policy analysis.  
- **Handling Various Document Formats** – Implemented preprocessing techniques for inconsistent layouts.  
- **Disaster Risk Prediction Accuracy** – Enhanced data preprocessing & feature engineering.  
- **Limited Real-World Property Risk Data** – Used multimodal AI to analyze property images.  

### 🔹 **Our Solutions**  
✅ Integrated **NLP for document parsing** instead of rule-based extraction  
✅ Used **multi-label classification for disaster risk modeling**  
✅ Leveraged **computer vision for object detection** in house images  
✅ Developed **interactive UI with real-time insights**  

---

## 🎯 Future Improvements  

🔹 **Expand Disaster Models** – Incorporate more granular climate & geological data  
🔹 **Enhance Policy Parsing** – Improve LLM fine-tuning for complex insurance terms  
🔹 **Improve UI & Mobile Support** – Build a responsive mobile-friendly interface  
🔹 **Integrate with Insurance Providers** – Offer APIs for seamless policy analysis  

---

## 🤝 Contributing  

We welcome contributions! To contribute:  

1. **Fork** the repository  
2. **Create a branch** (`feature-branch-name`)  
3. **Commit changes** and open a **pull request**  
4. **Ensure your code follows best practices**  

---

💡 *HouseOnTheEdge is a hackathon project built to revolutionize insurance evaluation using AI. If you find this useful, ⭐ star the repo and contribute to make it better!* 🚀  


