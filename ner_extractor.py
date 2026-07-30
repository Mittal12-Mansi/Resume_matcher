import json
import os
import re

try:
    import spacy
    from spacy.pipeline import EntityRuler
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

# Path to skills database
TAXONOMY_PATH = os.path.join(os.path.dirname(__file__), "data", "skills_taxonomy.json")

class SkillNERExtractor:
    def __init__(self, taxonomy_file=TAXONOMY_PATH):
        self.taxonomy = {}
        self.aliases = {}
        self.all_skills = set()
        self.load_taxonomy(taxonomy_file)
        
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except Exception:
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
        if not self.nlp:
            return
        if "entity_ruler" in self.nlp.pipe_names:
            ruler = self.nlp.get_pipe("entity_ruler")
        else:
            ruler = self.nlp.add_pipe("entity_ruler", before="ner" if "ner" in self.nlp.pipe_names else None)
        
        patterns = []
        for skill in self.all_skills:
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
        
        # 1. spaCy Entity Extractor (if available)
        if self.nlp:
            try:
                doc = self.nlp(text)
                for ent in doc.ents:
                    if ent.label_ == "SKILL":
                        norm = self.normalize_skill(ent.text)
                        extracted.add(norm)
            except Exception:
                pass

        # 2. Regex / String Phrase Boundary Matcher
        for skill in self.all_skills:
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
