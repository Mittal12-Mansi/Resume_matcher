import os
import json
import io
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import PyPDF2

from ner_extractor import extract_skills_from_text
from similarity_engine import get_similarity_engine
from gap_analyzer import analyze_skill_gap
from ats_analyzer import compute_ats_score
from eval_engine import ModelEvaluator

app = FastAPI(
    title="AI Resume ↔ Job Matcher & Skill Gap API",
    description="Production-grade AI system for Resume shortlisting, NER skill extraction, semantic matching, TF-IDF skill gap analysis, and ATS scoring.",
    version="2.0.0"
)

# Enable CORS for local testing & deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse PDF resume: {str(e)}")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Resume-Job-Matcher-API", "version": "2.0.0"}

@app.post("/api/match")
async def match_resume_and_jd(
    resume_file: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None),
    job_description: str = Form(...)
):
    # Determine resume text content
    final_resume_text = ""
    if resume_file and resume_file.filename:
        file_bytes = await resume_file.read()
        if resume_file.filename.lower().endswith(".pdf"):
            final_resume_text = extract_text_from_pdf_bytes(file_bytes)
        else:
            final_resume_text = file_bytes.decode("utf-8", errors="ignore")
    elif resume_text and resume_text.strip():
        final_resume_text = resume_text.strip()

    if not final_resume_text:
        raise HTTPException(status_code=400, detail="Please upload a valid PDF/TXT resume or provide resume text.")

    if not job_description or not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description text cannot be empty.")

    # 1. Skill Extraction (NER)
    resume_skills_info = extract_skills_from_text(final_resume_text)
    jd_skills_info = extract_skills_from_text(job_description)

    resume_skills = resume_skills_info["skills"]
    jd_skills = jd_skills_info["skills"]

    # 2. Skill Gap Analysis & TF-IDF Importance Ranking
    gap_result = analyze_skill_gap(resume_skills, jd_skills, job_description)

    # 3. Hybrid Semantic Similarity & Match Scoring
    sim_engine = get_similarity_engine()
    match_result = sim_engine.compute_match_score(
        final_resume_text,
        job_description,
        gap_result["matched_skills"],
        jd_skills
    )

    # 4. ATS Scoring & Section Feedback
    ats_result = compute_ats_score(
        final_resume_text,
        job_description,
        gap_result["matched_skills"],
        gap_result["missing_skills_ranked"]
    )

    # Match Status Label
    score = match_result["overall_match_score"]
    if score >= 75:
        match_status = "Strong Match"
        status_color = "success"
    elif score >= 50:
        match_status = "Moderate Match"
        status_color = "warning"
    else:
        match_status = "Low Match"
        status_color = "error"

    return {
        "overall_match_score": score,
        "match_status": match_status,
        "status_color": status_color,
        "score_breakdown": match_result["components"],
        "ats_analysis": ats_result,
        "skills_summary": {
            "resume_skills_count": len(resume_skills),
            "jd_skills_count": len(jd_skills),
            "matched_skills_count": len(gap_result["matched_skills"]),
            "missing_skills_count": len(gap_result["missing_skills_ranked"]),
            "matched_skills": gap_result["matched_skills"],
            "missing_skills_ranked": gap_result["missing_skills_ranked"],
            "critical_gaps": gap_result["critical_gaps"],
            "secondary_gaps": gap_result["secondary_gaps"],
            "resume_skills_by_category": resume_skills_info["by_category"],
            "jd_skills_by_category": jd_skills_info["by_category"]
        },
        "recommendations": gap_result["recommendations"] + ats_result["suggestions"]
    }

@app.post("/api/extract")
def extract_skills_endpoint(text: str = Form(...)):
    if not text:
        raise HTTPException(status_code=400, detail="Text parameter is required.")
    return extract_skills_from_text(text)

@app.post("/api/skill-gap")
def skill_gap_endpoint(resume_text: str = Form(...), job_description: str = Form(...)):
    res_skills = extract_skills_from_text(resume_text)["skills"]
    jd_skills = extract_skills_from_text(job_description)["skills"]
    return analyze_skill_gap(res_skills, jd_skills, job_description)

@app.get("/api/evaluate")
def run_evaluation_endpoint():
    evaluator = ModelEvaluator()
    return evaluator.run_evaluation()

# Mount Static Files for Modern Frontend
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
def read_root():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Resume Matcher API is Running.</h1><p>Frontend static/index.html initializing...</p>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_app:app", host="0.0.0.0", port=8000, reload=True)
