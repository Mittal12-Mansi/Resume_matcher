import json
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

POSTINGS_PATH = os.path.join(os.path.dirname(__file__), "data", "job_postings.json")

class SkillGapAnalyzer:
    def __init__(self, postings_path=POSTINGS_PATH):
        self.corpus_texts = []
        self.vectorizer = None
        self.feature_names = []
        self.tfidf_weights = {}
        self.load_corpus(postings_path)

    def load_corpus(self, filepath):
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                postings = json.load(f)
                self.corpus_texts = [p.get("description", "") for p in postings]
        
        if self.corpus_texts:
            try:
                self.vectorizer = TfidfVectorizer(ngram_range=(1, 3), stop_words="english")
                tfidf_matrix = self.vectorizer.fit_transform(self.corpus_texts)
                self.feature_names = self.vectorizer.get_feature_names_out()
                
                # Compute average TF-IDF weight across corpus
                mean_weights = np.asarray(tfidf_matrix.mean(axis=0)).ravel()
                for idx, word in enumerate(self.feature_names):
                    self.tfidf_weights[word.lower()] = mean_weights[idx]
            except Exception as e:
                print(f"[GapAnalyzer] TF-IDF corpus vectorizer init error: {e}")

    def get_skill_importance(self, skill, jd_text=""):
        skill_lower = skill.lower().strip()
        base_weight = self.tfidf_weights.get(skill_lower, 0.05)
        
        # Boost weight if skill explicitly appears multiple times in the JD
        if jd_text:
            occurrences = jd_text.lower().count(skill_lower)
            if occurrences > 1:
                base_weight *= (1 + 0.25 * (occurrences - 1))
        
        return round(float(base_weight * 100), 2)

    def analyze_gap(self, resume_skills, jd_skills, jd_text=""):
        resume_set = set(s.lower() for s in resume_skills)
        jd_set = set(s.lower() for s in jd_skills)
        
        matched_skills = sorted(list(jd_set & resume_set))
        missing_skills_raw = list(jd_set - resume_set)
        
        # Rank missing skills by TF-IDF Importance Score
        ranked_missing = []
        for skill in missing_skills_raw:
            importance = self.get_skill_importance(skill, jd_text)
            ranked_missing.append({
                "skill": skill,
                "importance_score": importance,
                "level": "Critical" if importance >= 1.2 else ("High" if importance >= 0.6 else "Medium")
            })
            
        ranked_missing.sort(key=lambda x: x["importance_score"], reverse=True)
        
        critical_gaps = [item for item in ranked_missing if item["level"] in ["Critical", "High"]]
        secondary_gaps = [item for item in ranked_missing if item["level"] == "Medium"]

        # Recommendations
        recommendations = []
        if ranked_missing:
            top_3 = [item["skill"].title() for item in ranked_missing[:3]]
            recommendations.append(f"Priority focus: Gain hands-on project experience with top missing skills: {', '.join(top_3)}.")
            recommendations.append("Update your resume project descriptions to highlight any exposure to these skills.")
        else:
            recommendations.append("Excellent match! Your resume covers all key technical skills requested in the job posting.")

        return {
            "matched_skills": [s.title() for s in matched_skills],
            "missing_skills_ranked": ranked_missing,
            "critical_gaps": critical_gaps,
            "secondary_gaps": secondary_gaps,
            "recommendations": recommendations
        }

# Global singleton
_gap_analyzer_instance = None

def get_gap_analyzer():
    global _gap_analyzer_instance
    if _gap_analyzer_instance is None:
        _gap_analyzer_instance = SkillGapAnalyzer()
    return _gap_analyzer_instance

def analyze_skill_gap(resume_skills, jd_skills, jd_text=""):
    analyzer = get_gap_analyzer()
    return analyzer.analyze_gap(resume_skills, jd_skills, jd_text)
