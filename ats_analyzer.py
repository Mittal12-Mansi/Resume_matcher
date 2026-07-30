import re

def compute_ats_score(resume_text, job_desc, matched_skills, missing_skills):
    score = 0.0
    suggestions = []
    
    resume_lower = resume_text.lower()
    job_lower = job_desc.lower()
    
    # 1. Essential Sections Check (20 pts)
    sections = {
        "skills": ["skills", "technical skills", "core competencies"],
        "experience": ["experience", "work experience", "employment", "professional experience"],
        "projects": ["projects", "personal projects", "key projects"],
        "education": ["education", "academic background", "qualifications"]
    }
    
    section_score = 0
    for sec_name, keywords in sections.items():
        found = any(kw in resume_lower for kw in keywords)
        if found:
            section_score += 5
        else:
            suggestions.append(f"Add an explicit '{sec_name.title()}' section header to boost ATS parser accuracy.")
    score += section_score
    
    # 2. Skill Alignment (40 pts)
    total_skills = len(matched_skills) + len(missing_skills)
    if total_skills > 0:
        skill_ratio = len(matched_skills) / total_skills
        score += skill_ratio * 40
        if len(missing_skills) > 0:
            top_missing = [s["skill"].title() if isinstance(s, dict) else s.title() for s in missing_skills[:3]]
            suggestions.append(f"Incorporate high-priority missing keywords: {', '.join(top_missing)}.")
    else:
        score += 20
        suggestions.append("Ensure your technical skills are listed clearly in a bulleted section.")

    # 3. Action Verbs Check (15 pts)
    action_verbs = [
        "developed", "built", "engineered", "designed", "architected", "implemented",
        "scaled", "optimized", "spearheaded", "managed", "deployed", "analyzed", "reduced", "increased"
    ]
    found_verbs = [v for v in action_verbs if v in resume_lower]
    if len(found_verbs) >= 4:
        score += 15
    elif len(found_verbs) >= 2:
        score += 10
        suggestions.append("Include more strong action verbs (e.g., engineered, scaled, optimized, architected).")
    else:
        score += 5
        suggestions.append("Start accomplishment bullets with powerful action verbs instead of passive phrases.")

    # 4. Quantifiable Impact & Metrics Check (15 pts)
    # Check for numbers, percentages, dollar amounts
    metrics_pattern = r'\b(\d+%\s*|\$\d+|\d+\+|\d+\s*k|\d+\s*ms)\b'
    matches = re.findall(metrics_pattern, resume_lower)
    if len(matches) >= 3:
        score += 15
    elif len(matches) >= 1:
        score += 10
        suggestions.append("Quantify your achievements with additional metric numbers (e.g., 'reduced latency by 40%', 'managed 50k users').")
    else:
        score += 5
        suggestions.append("Add measurable metrics and data points (%, $, time saved) to prove your impact.")

    # 5. Length & Formatting Check (10 pts)
    words = len(resume_text.split())
    if 300 <= words <= 900:
        score += 10
    elif words < 300:
        score += 5
        suggestions.append("Your resume appears too concise (under 300 words). Add details about relevant projects and experience.")
    else:
        score += 5
        suggestions.append("Your resume exceeds 900 words. Consider condensing content for better readability.")

    ats_final = round(score, 2)
    ats_final = min(100.0, max(0.0, ats_final))

    return {
        "ats_score": ats_final,
        "suggestions": suggestions,
        "word_count": words,
        "action_verbs_count": len(found_verbs)
    }
