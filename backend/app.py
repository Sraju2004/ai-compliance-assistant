# app.py (FDA Compliance Analyzer)
import os
import json
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from docx import Document
import pdfplumber
from openai import AzureOpenAI
from datetime import datetime, timezone

# -----------------------------
# 🔑 Azure OpenAI Configuration
# -----------------------------
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

azure_client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

# -----------------------------
# Flask Setup
# -----------------------------
app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DOCUMENTS_DIR = os.path.join(BASE_DIR, "documents")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

ALLOWED_EXT = {"pdf", "docx", "txt"}

SAMPLE_FILES = {
    "compliant": "Synthetic_SOP_Compliant.docx",
    "missing_sections": "Synthetic_SOP_Missing_Sections.docx",
    "outdated_refs": "Synthetic_SOP_Outdated_References.docx",
    "placeholder": "Synthetic_SOP_Placeholder.docx"
}

REFERENCE_PATHS = [
    os.path.join(DOCUMENTS_DIR, "21 CFR Part 11 (up to date as of 2-01-2024).pdf"),
    os.path.join(DOCUMENTS_DIR, "General-Principles-of-Software-Validation---Final-Guidance-for-Industry-and-FDA-Staff.pdf")
]

# -----------------------------
# File Readers
# -----------------------------
def read_pdf_text(path):
    text = ""
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text += (page.extract_text() or "") + "\n"
    except Exception as e:
        print(f"⚠️ Failed to read PDF {path}: {e}")
    return text

def read_docx_text(path):
    try:
        doc = Document(path)
        return "\n".join([p.text for p in doc.paragraphs if p.text])
    except Exception as e:
        print(f"⚠️ Failed to read DOCX {path}: {e}")
        return ""

def extract_text_from_file(path):
    if path.lower().endswith(".docx"):
        return read_docx_text(path)
    elif path.lower().endswith(".pdf"):
        return read_pdf_text(path)
    else:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            print(f"⚠️ Failed to read TXT {path}: {e}")
            return ""

REFERENCE_TEXT = ""
for p in REFERENCE_PATHS:
    if os.path.exists(p):
        REFERENCE_TEXT += "\n\n" + read_pdf_text(p)
    else:
        print(f"⚠️ Missing reference doc: {p}")

# -----------------------------
# Compliance Analysis (Mock Analyzer)
# -----------------------------
# Updated mock_analysis function
def mock_analysis(sop_text, filename):
    """Mock analysis function that analyzes SOPs based on reference documents"""
    
    # Initialize analysis result
    analysis = {
        "filename": filename,
        "score": 100,  # Start with perfect score, deduct for issues
        "issues": [],
        "suggestions": [],
        "notes": "Analysis performed using mock analyzer"
    }
    
    # Convert to lowercase for easier matching
    sop_lower = sop_text.lower()
    
    # Check for specific document types based on content
    is_placeholder = "SOP-003" in sop_text or "placeholder" in filename.lower()
    is_missing_sections = "SOP-002" in sop_text or "missing_sections" in filename.lower()
    is_outdated_refs = "SOP-004" in sop_text or "outdated_refs" in filename.lower()
    is_compliant = "SOP-001" in sop_text or "compliant" in filename.lower()
    
    # Simple section detection (looking for section headers)
    def has_section(section_name):
        # Look for common section header patterns
        patterns = [
            f"# {section_name}",
            f"## {section_name}", 
            f"#{section_name}",
            f"{section_name}:",
            f"{section_name.upper()}",
            f"{section_name.title()}"
        ]
        return any(pattern.lower() in sop_lower for pattern in patterns)
    
    # Check sections for each document type
    if is_compliant:
        # SOP-001: Should have all sections
        analysis["score"] = 90
        
        # Check for blank approvals
        if "_____" in sop_text or "___" in sop_text:
            analysis["issues"].append({
                "severity": "Minor", 
                "message": "Approval signatures are blank (using underscores)"
            })
            analysis["score"] -= 5
            
        analysis["suggestions"].append("Consider adding more detailed procedure steps")
        analysis["suggestions"].append("Include version control information in header")
    
    elif is_missing_sections:
        # SOP-002: Missing several sections
        analysis["score"] = 60
        
        # Check what's actually missing (this document should be missing Definitions, Revision History, Approvals)
        missing_sections = []
        if not has_section("definitions"):
            missing_sections.append("Definitions")
        if not has_section("revision history"):
            missing_sections.append("Revision History") 
        if not has_section("approvals"):
            missing_sections.append("Approvals")
        
        for section in missing_sections:
            analysis["issues"].append({
                "severity": "Major",
                "message": f"Missing section: {section}"
            })
            analysis["score"] -= 10
    
    elif is_outdated_refs:
        # SOP-004: Outdated references
        analysis["score"] = 30
        
        # Check for outdated references
        outdated_refs = {
            "ISO 9001:1994": "ISO 9001:2015",
            "ICH Q7 (2001)": "ICH Q7 (2015)", 
            "21 CFR Part 11 (1997)": "21 CFR Part 11 (2024)"
        }
        
        for old_ref, new_ref in outdated_refs.items():
            if old_ref in sop_text:
                analysis["issues"].append({
                    "severity": "Critical",
                    "message": f"Outdated reference: {old_ref}. Should be updated to {new_ref}"
                })
                analysis["score"] -= 20
        
        # Check old effective date
        if "2010-05-10" in sop_text:
            analysis["issues"].append({
                "severity": "Major", 
                "message": "Effective date is from 2010 - document needs comprehensive review"
            })
            analysis["score"] -= 10
    
    elif is_placeholder:
        # SOP-003: Placeholder text
        analysis["score"] = 20
        
        # Check for placeholder text
        placeholders = []
        if "tbd" in sop_lower:
            placeholders.append("TBD")
        if "to be decided" in sop_lower:
            placeholders.append("to be decided") 
        if "to be updated" in sop_lower:
            placeholders.append("to be updated")
        if "lorem ipsum" in sop_lower:
            placeholders.append("lorem ipsum")
        
        for placeholder in placeholders:
            analysis["issues"].append({
                "severity": "Major",
                "message": f"Contains placeholder text: {placeholder}"
            })
            analysis["score"] -= 15
        
        # Check if procedure has placeholders
        if "procedure" in sop_lower and any(p in sop_lower for p in ["tbd", "to be", "lorem"]):
            analysis["issues"].append({
                "severity": "Critical",
                "message": "Procedure section contains placeholder text instead of actual steps"
            })
            analysis["score"] -= 20
    
    else:
        # Generic document analysis
        required_sections = ["purpose", "scope", "procedure", "references"]
        for section in required_sections:
            if not has_section(section):
                analysis["issues"].append({
                    "severity": "Major",
                    "message": f"Missing required section: {section.title()}"
                })
                analysis["score"] -= 15
        
        # Check for placeholders
        if any(p in sop_lower for p in ["tbd", "to be decided", "to be updated", "lorem ipsum"]):
            analysis["issues"].append({
                "severity": "Major", 
                "message": "Contains placeholder text"
            })
            analysis["score"] -= 10
    
    # Ensure score is reasonable
    analysis["score"] = max(0, min(100, analysis["score"]))
    
    # Add general suggestions
    if not analysis["issues"]:
        analysis["suggestions"].append("SOP appears compliant with FDA regulations")
    else:
        analysis["suggestions"].append("Review and address all identified issues")
        
        if any("placeholder" in issue["message"].lower() for issue in analysis["issues"]):
            analysis["suggestions"].append("Replace all placeholder text with actual content")
            
        if any("outdated" in issue["message"].lower() for issue in analysis["issues"]):
            analysis["suggestions"].append("Update all references to current versions")
            
        if any("missing" in issue["message"].lower() for issue in analysis["issues"]):
            analysis["suggestions"].append("Add all missing required sections")
    
    return analysis

# -----------------------------
# Azure OpenAI Helpers
# -----------------------------
def build_prompt(sop_text, filename):
    trimmed_sop = sop_text[:5000]
    trimmed_refs = REFERENCE_TEXT[:3000]
    return f"""
You are an FDA compliance expert. Analyze the SOP for compliance.

Return ONLY JSON with schema:
{{
  "filename": "<filename>",
  "score": <0-100>,
  "issues": [{{"severity":"Critical|Major|Minor", "message":"..."}}],
  "suggestions": ["..."],
  "notes": "...",
  "scoring_explanation": "..."
}}

Check for:
- Missing sections: Title, Purpose, Scope, Responsibilities, Definitions, Procedure, References, Revision History, Approvals
- Metadata: Document ID, Version/Revision, Effective Date
- Revision History completeness
- References freshness
- Placeholders (TBD, lorem ipsum, etc.)
- Procedure steps clarity (≥3)
- Approvals/signatures

SOP Content:
{trimmed_sop}
"""

def call_azure_openai(prompt, max_tokens=800):
    try:
        print(f"➡️ Sending request to Azure OpenAI with deployment: {AZURE_OPENAI_DEPLOYMENT_NAME}")
        response = azure_client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are a strict FDA compliance assistant. Always return ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=max_tokens,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        if not content or not content.strip():
            return None
        print(f"✅ Received response: {content[:200]}...")
        return content
    except Exception as e:
        print(f"❌ Azure OpenAI error: {e}")
        return None

# -----------------------------
# API Routes
# -----------------------------
@app.route("/analyze", methods=["POST"])
def analyze_upload():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    filename = secure_filename(file.filename)
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXT:
        return jsonify({"error": "Unsupported file type"}), 400

    saved_path = os.path.join(UPLOADS_DIR, f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{filename}")
    file.save(saved_path)

    sop_text = extract_text_from_file(saved_path)
    if not sop_text.strip():
        return jsonify({"error": "File unreadable"}), 400

    prompt = build_prompt(sop_text, filename)
    model_out = call_azure_openai(prompt)

    if model_out:
        try:
            return jsonify({"filename": filename, "analysis": json.loads(model_out)})
        except Exception as e:
            print(f"⚠️ JSON parse failed: {e}")

    return jsonify({"filename": filename, "analysis": mock_analysis(sop_text, filename)})

@app.route("/analyze-sample", methods=["POST"])
def analyze_sample():
    data = request.get_json() or {}
    key = data.get("sample_key")
    if not key or key not in SAMPLE_FILES:
        return jsonify({"error": f"Provide sample_key ({', '.join(SAMPLE_FILES)})"}), 400

    path = os.path.join(DOCUMENTS_DIR, SAMPLE_FILES[key])
    if not os.path.exists(path):
        return jsonify({"error": "Sample file not found"}), 404

    sop_text = extract_text_from_file(path)
    if not sop_text.strip():
        return jsonify({"error": "Sample unreadable"}), 400

    prompt = build_prompt(sop_text, SAMPLE_FILES[key])
    model_out = call_azure_openai(prompt)

    if model_out:
        try:
            return jsonify({"filename": SAMPLE_FILES[key], "analysis": json.loads(model_out)})
        except Exception as e:
            print(f"⚠️ JSON parse failed: {e}")

    return jsonify({"filename": SAMPLE_FILES[key], "analysis": mock_analysis(sop_text, SAMPLE_FILES[key])})

@app.route("/")
def root():
    return jsonify({"message": "✅ Flask AI Compliance backend running"})

# -----------------------------
# Run Server
# -----------------------------
if __name__ == "__main__":
    app.run(port=8000, debug=True)
