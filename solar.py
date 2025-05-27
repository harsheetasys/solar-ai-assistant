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
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Extract JSON from response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            json_str = content[json_start:json_end]
            
            return json.loads(json_str)
            
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")
            return None

def main():
    st.set_page_config(
        page_title="Solar Rooftop Analysis AI",
        page_icon="☀️",
        layout="wide"
    )
    
    st.title("☀️ AI-Powered Solar Rooftop Analysis")
    st.markdown("Upload satellite imagery to get comprehensive solar installation assessments")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input("OpenRouter API Key", type="password")
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
    
    if not api_key:
        st.warning("Please enter your OpenRouter API key in the sidebar")
        return
    
    # Initialize AI analyzer
    analyzer = SolarAnalysisAI(api_key)
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload Rooftop Image",
        type=['png', 'jpg', 'jpeg'],
        help="Upload satellite or aerial imagery of the rooftop"
    )
    
    if uploaded_file:
        # Display uploaded image
        image = Image.open(uploaded_file)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Uploaded Image")
            st.image(image, caption="Rooftop Analysis Target", use_column_width=True)
        
        with col2:
            if st.button("🔍 Analyze Solar Potential", type="primary"):
                if not location:
                    st.error("Please enter the property location")
                    return
                
                with st.spinner("Analyzing rooftop with AI..."):
                    analysis = analyzer.analyze_rooftop(image, location, budget)
                
                if analysis:
                    display_analysis_results(analysis)

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

if __name__ == "__main__":
    main()
