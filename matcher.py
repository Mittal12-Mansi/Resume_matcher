from ner_extractor import extract_skills_from_text
from similarity_engine import get_similarity_engine
from gap_analyzer import analyze_skill_gap

def preprocess(text):
    return text.strip()

def compute_final_score(resume, job_desc):
    res_skills = extract_skills_from_text(resume)["skills"]
    jd_skills = extract_skills_from_text(job_desc)["skills"]
    
    gap = analyze_skill_gap(res_skills, jd_skills, job_desc)
    sim_engine = get_similarity_engine()
    
    match_result = sim_engine.compute_match_score(resume, job_desc, gap["matched_skills"], jd_skills)
    return match_result["overall_match_score"]