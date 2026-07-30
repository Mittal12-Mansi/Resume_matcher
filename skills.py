from ner_extractor import extract_skills_from_text
from gap_analyzer import analyze_skill_gap

def extract_skills(text):
    res = extract_skills_from_text(text)
    return res["skills"]

def skill_gap(resume, job_desc):
    res_skills = extract_skills(resume)
    jd_skills = extract_skills(job_desc)
    
    gap_analysis = analyze_skill_gap(res_skills, jd_skills, job_desc)
    
    matched = gap_analysis["matched_skills"]
    missing = [item["skill"] for item in gap_analysis["missing_skills_ranked"]]
    
    return matched, missing