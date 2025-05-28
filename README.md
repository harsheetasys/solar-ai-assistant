**☀️ Solar AI Assistant**
An AI-powered rooftop analysis tool that uses satellite imagery to assess solar installation potential, providing comprehensive assessments for homeowners and solar professionals.

🚀 Features
🏠 Rooftop Image Analysis - Upload satellite/aerial imagery for AI-powered analysis
⚡ Solar Potential Assessment - Get detailed solar installation recommendations
💰 Financial ROI Calculations - Comprehensive cost and savings analysis
🔧 Installation Planning - Technical specifications and timeline estimates
📊 Interactive Dashboard - Visual metrics and detailed reporting
🌍 Location-Based Analysis - Customized assessments based on geographic location

🛠️ Installation
Prerequisites
Python 3.8 or higher
pip package manager
OpenRouter API key

**Quick Setup**

Clone the repository
git clone https://github.com/yourusername/solar-ai-assistant.git
cd solar-ai-assistant

Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies
pip install -r requirements.txt

Run the application
streamlit run app.py

📦 Requirements
streamlit>=1.28.0
requests>=2.31.0
Pillow>=10.0.0
numpy>=1.24.0

**🎯 Usage**

Start the application
streamlit run app.py

Configure settings in sidebar
Enter your OpenRouter API key

Specify property location (e.g., "San Francisco, CA")
Set your budget ($1,000 - $100,000)
Upload rooftop image
Supported formats: PNG, JPG, JPEG
Satellite or aerial imagery works best

Analyze solar potential
Click "🚀 Analyze Solar Potential"
Wait for AI analysis to complete
Review comprehensive results

**🔑 API Key Setup**
Getting Your OpenRouter API Key
Visit OpenRouter
Sign up for a free account
Navigate to API Keys section
Generate a new API key
Copy the key (starts with sk-or-v1-)
