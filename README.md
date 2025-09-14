# AI-Powered Compliance Assistant for Healthtech Documentation  

## Problem Statement  
In the healthtech domain, organizations must maintain a large number of regulatory documents (SOPs, quality manuals, and process guidelines) to meet audit and compliance requirements. Traditionally, these documents are manually reviewed — a slow, inconsistent, and error-prone process.  

## Solution  
We built an **AI-powered compliance assistant** that automatically analyzes regulatory documents (PDF, DOCX, TXT), validates them against FDA/GxP rules, and generates a compliance score.  

The tool highlights missing sections, outdated references, placeholder text, and other compliance issues — helping organizations **reduce audit risks and improve regulatory readiness**.  

---

## High-Level Design  

### Architecture  

#### Frontend (React)  
- User-friendly interface to upload documents.  
- Option to analyze sample SOPs (compliant, missing sections, outdated references, placeholder).  
- Displays compliance score, issues, and suggestions with clear visual cues.  

#### Backend (Flask + Azure OpenAI)  
- Handles file uploads and parsing (DOCX, PDF, TXT).  
- Extracts text using `docx` and `pdfplumber`.  
- Runs compliance analysis via:  
  1. **Azure OpenAI** for intelligent checks.  
  2. **Mock Analyzer** fallback for rule-based local analysis.  
- Returns structured JSON (score, issues, suggestions).  

#### Compliance Rules Engine  
- Checks for mandatory sections (Title, Purpose, Scope, etc.).  
- Validates metadata (Document ID, Version, Effective Date).  
- Detects placeholders (e.g., *TBD*, *Lorem Ipsum*).  
- Flags outdated references (e.g., ISO 9001:1994 → ISO 9001:2015).  
- Ensures procedure clarity (≥ 3 steps).  

### Flow  
1. User uploads document from frontend.  
2. Backend extracts text and builds AI prompt.  
3. AI/Mock Analyzer validates compliance.  
4. JSON response returned with compliance score.  
5. Results visualized in React dashboard.  

---

## Installation & Setup  

### Clone Repository  
git clone https://github.com/Sraju2004/ai-compliance-assistant.git
cd ai-compliance-assistant

### Backend Setup (Flask)
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

### .env
AZURE_OPENAI_KEY="your-azure-openai-key"
AZURE_OPENAI_ENDPOINT="your-endpoint-url"
AZURE_OPENAI_DEPLOYMENT_NAME="your-deployment-name"
AZURE_OPENAI_API_VERSION="2024-02-01"

### Run the Flask server:
python app.py 
Backend runs on: http://127.0.0.1:8000

### Frontend Setup (React)
cd frontend
npm install
npm start 
Frontend runs on: http://localhost:3000

## Usage
- Start backend (Flask) and frontend (React).
- Open the app in your browser → http://localhost:3000
- Upload your SOP/Regulatory Document (PDF/DOCX/TXT).
- View compliance score, issues, and suggestions.
- Alternatively, test with provided sample SOPs (compliant, missing sections, outdated references, placeholder).

## Example Output
{
  "filename": "Synthetic_SOP_Missing_Sections.docx",
  "score": 60,
  "issues": [
    { "severity": "Major", "message": "Missing section: Definitions" },
    { "severity": "Major", "message": "Missing section: Revision History" },
    { "severity": "Major", "message": "Missing section: Approvals" }
  ],
  "suggestions": [
    "Add all missing required sections",
    "Review and address all identified issues"
  ],
  "notes": "Analysis performed using mock analyzer"
}

## Contributors
Shanmukha Ullinkala – Backend (Flask + AI integration), Frontend (React UI)
