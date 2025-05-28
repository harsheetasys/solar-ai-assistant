import streamlit as st
import requests
import json
import base64
from PIL import Image
import io
import numpy as np
from typing import Dict, List, Tuple
import os

class SolarAnalysisAI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        
    def encode_image(self, image) -> str:
        """Convert PIL image to base64 string for API"""
        buffer = io.BytesIO()
        
        # Fix for RGBA to JPEG conversion issue
        if image.mode == 'RGBA':
            # Create white background and paste image on it
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])  # Use alpha channel as mask
            image = background
        elif image.mode not in ('RGB', 'L'):
            # Convert any other modes to RGB
            image = image.convert('RGB')
        
        image.save(buffer, format="JPEG")
        return base64.b64encode(buffer.getvalue()).decode()
    
    def analyze_rooftop(self, image, location: str, budget: float) -> Dict:
        """Analyze rooftop for solar potential using vision AI"""
        
        image_b64 = self.encode_image(image)
        
        prompt = f"""
        You are an expert solar energy consultant analyzing a rooftop for solar panel installation potential. 
        
        Location: {location}
        Budget: ${budget:,.2f}
        
        Analyze this satellite/aerial image and provide a comprehensive assessment in the following JSON format:
        
        {{
            "roof_analysis": {{
                "roof_type": "flat/pitched/hip/gable",
                "roof_area_sqft": estimated_total_area,
                "usable_area_sqft": area_suitable_for_panels,
                "orientation": "primary_roof_direction",
                "tilt_angle": estimated_degrees,
                "shading_assessment": "minimal/moderate/significant",
                "obstacles": ["list", "of", "obstacles"]
            }},
            "solar_potential": {{
                "recommended_system_size_kw": calculated_size,
                "estimated_panels_count": number_of_panels,
                "annual_energy_production_kwh": estimated_production,
                "capacity_factor": percentage,
                "optimal_panel_type": "monocrystalline/polycrystalline/thin_film"
            }},
            "financial_analysis": {{
                "estimated_system_cost": total_cost,
                "cost_per_watt": cost_per_watt,
                "annual_savings": estimated_annual_savings,
                "payback_period_years": calculated_payback,
                "roi_percentage": return_on_investment,
                "net_present_value": npv_calculation
            }},
            "installation_considerations": {{
                "structural_assessment": "suitable/needs_evaluation/not_suitable",
                "electrical_requirements": "description",
                "permit_complexity": "simple/moderate/complex",
                "installation_timeline": "estimated_weeks"
            }},
            "recommendations": {{
                "proceed_with_installation": true_or_false,
                "priority_improvements": ["list", "of", "suggestions"],
                "alternative_solutions": ["if", "applicable"],
                "next_steps": ["recommended", "actions"]
            }}
        }}
        
        Base your analysis on visible roof characteristics, estimated dimensions, shading from trees/buildings, 
        roof condition, and typical solar installation parameters for the given location and budget.
        """
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "anthropic/claude-3.5-sonnet",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_b64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.1
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data)
            
            # Check if request was successful
            response.raise_for_status()
            
            # Debug: Print response details
            st.write(f"**Response Status:** {response.status_code}")
            
            # Check if response has content
            if not response.text.strip():
                st.error("❌ Empty response from API")
                return None
            
            # Try to parse JSON
            try:
                result = response.json()
            except json.JSONDecodeError as json_err:
                st.error(f"❌ Invalid JSON response: {json_err}")
                st.write(f"**Raw Response:** {response.text[:500]}...")
                return None
            
            # Check if response has expected structure
            if 'choices' not in result or not result['choices']:
                st.error("❌ Unexpected API response structure")
                st.write(f"**Response:** {result}")
                return None
            
            content = result['choices'][0]['message']['content']
            
            # Extract JSON from response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                st.error("❌ No JSON found in AI response")
                st.write(f"**AI Response:** {content}")
                return None
            
            json_str = content[json_start:json_end]
            
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as parse_err:
                st.error(f"❌ Failed to parse AI response JSON: {parse_err}")
                st.write(f"**Extracted JSON:** {json_str}")
                return None
                
        except requests.exceptions.RequestException as req_err:
            st.error(f"❌ API request failed: {req_err}")
            return None
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            return None

def display_analysis_results(analysis: Dict):
    """Display comprehensive analysis results"""
    
    st.success("✅ Analysis Complete!")
    
    # Key Metrics Dashboard
    st.subheader("📊 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "System Size",
            f"{analysis['solar_potential']['recommended_system_size_kw']:.1f} kW"
        )
    
    with col2:
        st.metric(
            "Annual Production",
            f"{analysis['solar_potential']['annual_energy_production_kwh']:,.0f} kWh"
        )
    
    with col3:
        st.metric(
            "Payback Period",
            f"{analysis['financial_analysis']['payback_period_years']:.1f} years"
        )
    
    with col4:
        st.metric(
            "ROI",
            f"{analysis['financial_analysis']['roi_percentage']:.1f}%"
        )
    
    # Detailed Analysis Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏠 Roof Analysis", 
        "⚡ Solar Potential", 
        "💰 Financial Analysis", 
        "🔧 Installation"
    ])
    
    with tab1:
        st.subheader("Roof Characteristics")
        roof = analysis['roof_analysis']
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Roof Type:** {roof['roof_type'].title()}")
            st.write(f"**Total Area:** {roof['roof_area_sqft']:,.0f} sq ft")
            st.write(f"**Usable Area:** {roof['usable_area_sqft']:,.0f} sq ft")
        
        with col2:
            st.write(f"**Orientation:** {roof['orientation']}")
            st.write(f"**Tilt Angle:** {roof['tilt_angle']}°")
            st.write(f"**Shading:** {roof['shading_assessment'].title()}")
        
        if roof['obstacles']:
            st.write("**Obstacles Identified:**")
            for obstacle in roof['obstacles']:
                st.write(f"• {obstacle}")
    
    with tab2:
        st.subheader("Solar System Specifications")
        solar = analysis['solar_potential']
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Recommended System Size:** {solar['recommended_system_size_kw']:.1f} kW")
            st.write(f"**Number of Panels:** {solar['estimated_panels_count']}")
            st.write(f"**Panel Type:** {solar['optimal_panel_type'].replace('_', ' ').title()}")
        
        with col2:
            st.write(f"**Annual Production:** {solar['annual_energy_production_kwh']:,.0f} kWh")
            st.write(f"**Capacity Factor:** {solar['capacity_factor']:.1f}%")
    
    with tab3:
        st.subheader("Financial Projections")
        financial = analysis['financial_analysis']
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**System Cost:** ${financial['estimated_system_cost']:,.0f}")
            st.write(f"**Cost per Watt:** ${financial['cost_per_watt']:.2f}")
            st.write(f"**Annual Savings:** ${financial['annual_savings']:,.0f}")
        
        with col2:
            st.write(f"**Payback Period:** {financial['payback_period_years']:.1f} years")
            st.write(f"**ROI:** {financial['roi_percentage']:.1f}%")
            st.write(f"**Net Present Value:** ${financial['net_present_value']:,.0f}")
    
    with tab4:
        st.subheader("Installation Assessment")
        installation = analysis['installation_considerations']
        
        st.write(f"**Structural Assessment:** {installation['structural_assessment'].replace('_', ' ').title()}")
        st.write(f"**Electrical Requirements:** {installation['electrical_requirements']}")
        st.write(f"**Permit Complexity:** {installation['permit_complexity'].title()}")
        st.write(f"**Installation Timeline:** {installation['installation_timeline']}")
    
    # Recommendations
    st.subheader("🎯 Recommendations")
    recommendations = analysis['recommendations']
    
    if recommendations['proceed_with_installation']:
        st.success("✅ **Recommended:** This property is suitable for solar installation")
    else:
        st.warning("⚠️ **Caution:** Additional evaluation recommended before proceeding")
    
    if recommendations['priority_improvements']:
        st.write("**Priority Improvements:**")
        for improvement in recommendations['priority_improvements']:
            st.write(f"• {improvement}")
    
    if recommendations['next_steps']:
        st.write("**Next Steps:**")
        for step in recommendations['next_steps']:
            st.write(f"• {step}")

def main():
    # Set page config for Hugging Face Spaces
    st.set_page_config(
        page_title="Solar AI Assistant",
        page_icon="☀️",
        layout="wide"
    )
    
    st.title("☀️ AI-Powered Solar Rooftop Analysis")
    st.markdown("Upload satellite imagery to get comprehensive solar installation assessments")
    
    # Get API key from Hugging Face Secrets or user input
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # If no environment variable, allow manual input
        if not api_key:
            api_key = st.text_input("OpenRouter API Key", type="password", 
                                   help="Enter your OpenRouter API key")
        else:
            st.success("✅ API Key loaded from environment")
        
        location = st.text_input("Property Location", placeholder="e.g., San Francisco, CA")
        budget = st.number_input("Budget ($)", min_value=1000, max_value=100000, value=25000)
        
        st.markdown("---")
        st.markdown("### About This Tool")
        st.markdown("""
        This AI assistant analyzes rooftop imagery to provide:
        - Solar installation potential assessment
        - Financial ROI calculations
        - Installation recommendations
        - Technical specifications
        """)
        
        st.markdown("---")
        st.markdown("### How to Use")
        st.markdown("""
        1. Enter your OpenRouter API key (if not set in environment)
        2. Specify the property location
        3. Set your budget
        4. Upload a rooftop image
        5. Click 'Analyze Solar Potential'
        """)
    
    if not api_key:
        st.warning("⚠️ Please enter your OpenRouter API key in the sidebar to continue")
        st.info("💡 Get your API key from [OpenRouter](https://openrouter.ai/keys)")
        return
    
    # Initialize AI analyzer
    analyzer = SolarAnalysisAI(api_key)
    
    # File upload section
    st.subheader("📸 Upload Rooftop Image")
    uploaded_file = st.file_uploader(
        "Choose a rooftop image file",
        type=['png', 'jpg', 'jpeg'],
        help="Upload satellite or aerial imagery of the rooftop for analysis"
    )
    
    if uploaded_file:
        # Display uploaded image
        image = Image.open(uploaded_file)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📷 Uploaded Image")
            # Fixed: Changed use_column_width to use_container_width
            st.image(image, caption="Rooftop Analysis Target", use_container_width=True)
            
            # Image info
            st.write(f"**Image Size:** {image.size[0]} x {image.size[1]} pixels")
            st.write(f"**File Size:** {len(uploaded_file.getvalue()) / 1024:.1f} KB")
        
        with col2:
            st.subheader("🔍 Analysis Controls")
            
            if not location:
                st.error("⚠️ Please enter the property location in the sidebar")
            else:
                st.success(f"📍 Location: {location}")
                st.info(f"💰 Budget: ${budget:,.2f}")
                
                if st.button("🚀 Analyze Solar Potential", type="primary", use_container_width=True):
                    with st.spinner("🤖 Analyzing rooftop with AI... This may take a few moments."):
                        analysis = analyzer.analyze_rooftop(image, location, budget)
                    
                    if analysis:
                        display_analysis_results(analysis)
                    else:
                        st.error("❌ Analysis failed. Please check your API key and try again.")

if __name__ == "__main__":
    main()
