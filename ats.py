from ner_extractor import extract_skills_from_text
from gap_analyzer import analyze_skill_gap
from ats_analyzer import compute_ats_score

def ats_score(resume_text, job_desc):
    res_skills = extract_skills_from_text(resume_text)["skills"]
    jd_skills = extract_skills_from_text(job_desc)["skills"]
    
    gap = analyze_skill_gap(res_skills, jd_skills, job_desc)
    
    ats_res = compute_ats_score(
        resume_text,
        job_desc,
        gap["matched_skills"],
        gap["missing_skills_ranked"]
    )
    
    return ats_res["ats_score"], ats_res["suggestions"]