import json
import os
import re
import spacy
from spacy.pipeline import EntityRuler

# Path to skills database
TAXONOMY_PATH = os.path.join(os.path.dirname(__file__), "data", "skills_taxonomy.json")

class SkillNERExtractor:
    def __init__(self, taxonomy_file=TAXONOMY_PATH):
        self.taxonomy = {}
        self.aliases = {}
        self.all_skills = set()
        self.load_taxonomy(taxonomy_file)
        
        # Load spacy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except Exception:
            # Fallback if spacy model not downloaded
            self.nlp = spacy.blank("en")

        self.setup_spacy_ruler()

    def load_taxonomy(self, filepath):
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.taxonomy = data.get("taxonomy", {})
                self.aliases = data.get("aliases", {})
        
        for category, skills in self.taxonomy.items():
            for skill in skills:
                self.all_skills.add(skill.lower())
        
        for alias in self.aliases.keys():
            self.all_skills.add(alias.lower())

    def setup_spacy_ruler(self):
        if "entity_ruler" in self.nlp.pipe_names:
            ruler = self.nlp.get_pipe("entity_ruler")
        else:
            ruler = self.nlp.add_pipe("entity_ruler", before="ner" if "ner" in self.nlp.pipe_names else None)
        
        patterns = []
        for skill in self.all_skills:
            # Create tokenized patterns
            tokens = skill.split()
            pattern = [{"LOWER": t} for t in tokens]
            patterns.append({"label": "SKILL", "pattern": pattern})
        
        ruler.add_patterns(patterns)

    def normalize_skill(self, skill):
        s_clean = skill.strip().lower()
        if s_clean in self.aliases:
            return self.aliases[s_clean]
        return s_clean

    def extract_skills(self, text):
        if not text:
            return {"skills": [], "by_category": {}, "normalized": []}
        
        extracted = set()
        text_lower = text.lower()
        
        # 1. spaCy Entity Extractor
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == "SKILL":
                norm = self.normalize_skill(ent.text)
                extracted.add(norm)

        # 2. Regex / String Boundary Matcher for multi-word and boundary exact matches
        for skill in self.all_skills:
            # Use word boundary for single token, or phrase match
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                norm = self.normalize_skill(skill)
                extracted.add(norm)

        # Categorize extracted skills
        skills_list = sorted(list(extracted))
        by_category = {}
        
        for category, skills_in_cat in self.taxonomy.items():
            cat_matched = [s for s in skills_list if s in skills_in_cat]
            if cat_matched:
                by_category[category] = cat_matched
        
        # Uncategorized check
        categorized_set = set(s for cat_list in by_category.values() for s in cat_list)
        uncategorized = [s for s in skills_list if s not in categorized_set]
        if uncategorized:
            by_category["Other"] = uncategorized

        return {
            "skills": skills_list,
            "count": len(skills_list),
            "by_category": by_category
        }

# Global singleton extractor
_extractor_instance = None

def get_skill_extractor():
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = SkillNERExtractor()
    return _extractor_instance

def extract_skills_from_text(text):
    extractor = get_skill_extractor()
    return extractor.extract_skills(text)

if __name__ == "__main__":
    sample_text = "Looking for a Senior Full Stack Dev with Python, Docker, ReactJS, K8s, AWS, and System Design experience."
    res = extract_skills_from_text(sample_text)
    print("Extracted Skills:", res["skills"])
    print("By Category:", json.dumps(res["by_category"], indent=2))
