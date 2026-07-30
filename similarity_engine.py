import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Environment flag to enable heavy PyTorch models (default: False for cloud low-RAM compatibility)
ENABLE_TRANSFORMERS = os.getenv("ENABLE_TRANSFORMERS", "false").lower() == "true"

_ST_MODEL = None

def get_sentence_transformer():
    global _ST_MODEL
    if not ENABLE_TRANSFORMERS:
        return None
    if _ST_MODEL is None:
        try:
            from sentence_transformers import SentenceTransformer
            _ST_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            print(f"[SimilarityEngine] SentenceTransformer skipped for low RAM: {e}")
            _ST_MODEL = False
    return _ST_MODEL if _ST_MODEL is not False else None

class SimilarityEngine:
    def __init__(self):
        pass

    def compute_tfidf_similarity(self, text1, text2):
        if not text1 or not text2:
            return 0.0
        try:
            vectorizer = TfidfVectorizer(ngram_range=(1, 3), stop_words='english', min_df=1)
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(sim)
        except Exception:
            return 0.0

    def compute_embedding_similarity(self, text1, text2):
        if not text1 or not text2:
            return 0.0
            
        model = get_sentence_transformer()
        if model is not None:
            try:
                embeddings = model.encode([text1, text2])
                sim = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
                return float(sim)
            except Exception as e:
                print(f"[SimilarityEngine] Embedding error: {e}")

        # High-performance lightweight TF-IDF n-gram vector similarity fallback
        return self.compute_tfidf_similarity(text1, text2)

    def compute_match_score(self, resume_text, job_desc, matched_skills, job_skills):
        lexical_sim = self.compute_tfidf_similarity(resume_text, job_desc)
        embedding_sim = self.compute_embedding_similarity(resume_text, job_desc)
        
        if job_skills and len(job_skills) > 0:
            skill_coverage = len(matched_skills) / len(job_skills)
        else:
            skill_coverage = 0.5

        # Weighted hybrid formula
        hybrid_raw = (0.50 * embedding_sim) + (0.30 * skill_coverage) + (0.20 * lexical_sim)
        
        # Scale to 0-100 percentage
        match_score = round(float(hybrid_raw) * 100, 2)
        match_score = max(0.0, min(100.0, match_score))

        return {
            "overall_match_score": match_score,
            "components": {
                "embedding_similarity": round(float(embedding_sim) * 100, 2),
                "skill_coverage_score": round(float(skill_coverage) * 100, 2),
                "lexical_tfidf_similarity": round(float(lexical_sim) * 100, 2)
            }
        }

# Global singleton
_similarity_engine_instance = None

def get_similarity_engine():
    global _similarity_engine_instance
    if _similarity_engine_instance is None:
        _similarity_engine_instance = SimilarityEngine()
    return _similarity_engine_instance
