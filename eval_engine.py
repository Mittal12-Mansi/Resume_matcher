import json
import os
import numpy as np

from ner_extractor import extract_skills_from_text
from similarity_engine import get_similarity_engine
from gap_analyzer import analyze_skill_gap
from ats_analyzer import compute_ats_score

EVAL_PATH = os.path.join(os.path.dirname(__file__), "data", "eval_dataset.json")

class ModelEvaluator:
    def __init__(self, eval_path=EVAL_PATH):
        self.eval_path = eval_path

    def run_evaluation(self, match_threshold=60.0):
        if not os.path.exists(self.eval_path):
            return {"error": "Evaluation dataset not found. Run data_generator.py first."}

        with open(self.eval_path, "r", encoding="utf-8") as f:
            eval_pairs = json.load(f)

        sim_engine = get_similarity_engine()

        true_positives = 0
        false_positives = 0
        true_negatives = 0
        false_negatives = 0

        absolute_errors = []
        detailed_results = []

        for pair in eval_pairs:
            res_text = pair["resume_text"]
            jd_text = pair["jd_text"]
            ground_truth_match = pair["should_match"]
            expected_min = pair["expected_score_min"]
            expected_max = pair["expected_score_max"]
            expected_mid = (expected_min + expected_max) / 2.0

            # 1. Extract Skills
            res_skills = extract_skills_from_text(res_text)["skills"]
            jd_skills = extract_skills_from_text(jd_text)["skills"]

            # 2. Skill Gap
            gap_info = analyze_skill_gap(res_skills, jd_skills, jd_text)
            matched_skills = gap_info["matched_skills"]

            # 3. Match Score
            match_res = sim_engine.compute_match_score(res_text, jd_text, matched_skills, jd_skills)
            predicted_score = match_res["overall_match_score"]

            # 4. Classification Decision
            predicted_match = predicted_score >= match_threshold

            # Confusion Matrix
            if ground_truth_match and predicted_match:
                true_positives += 1
            elif not ground_truth_match and predicted_match:
                false_positives += 1
            elif not ground_truth_match and not predicted_match:
                true_negatives += 1
            elif ground_truth_match and not predicted_match:
                false_negatives += 1

            abs_err = abs(predicted_score - expected_mid)
            absolute_errors.append(abs_err)

            detailed_results.append({
                "id": pair["id"],
                "candidate_role": pair["candidate_role"],
                "jd_title": pair["jd_title"],
                "fit_label": pair["fit_label"],
                "ground_truth_should_match": ground_truth_match,
                "predicted_score": predicted_score,
                "predicted_match": predicted_match,
                "error": round(abs_err, 2)
            })

        total = len(eval_pairs)
        accuracy = (true_positives + true_negatives) / total if total > 0 else 0
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        mae = float(np.mean(absolute_errors)) if absolute_errors else 0

        report = {
            "dataset_size": total,
            "match_threshold_used": match_threshold,
            "metrics": {
                "accuracy": round(accuracy * 100, 2),
                "precision": round(precision * 100, 2),
                "recall": round(recall * 100, 2),
                "f1_score": round(f1_score * 100, 2),
                "mean_absolute_error": round(mae, 2)
            },
            "confusion_matrix": {
                "true_positives": true_positives,
                "false_positives": false_positives,
                "true_negatives": true_negatives,
                "false_negatives": false_negatives
            },
            "sample_results": detailed_results[:10]
        }

        return report

def main():
    evaluator = ModelEvaluator()
    print("Running evaluation on 50 benchmark Resume-JD test pairs...")
    report = evaluator.run_evaluation()

    print("\n" + "=" * 60)
    print("          MODEL EVALUATION BENCHMARK REPORT          ")
    print("=" * 60)
    print(f"Dataset Size       : {report['dataset_size']} Resume-JD Pairs")
    print(f"Match Threshold    : {report['match_threshold_used']}%")
    print("-" * 60)
    metrics = report["metrics"]
    print(f"Precision          : {metrics['precision']}%")
    print(f"Recall             : {metrics['recall']}%")
    print(f"F1 Score           : {metrics['f1_score']}%")
    print(f"Accuracy           : {metrics['accuracy']}%")
    print(f"Mean Abs Error     : {metrics['mean_absolute_error']} points")
    print("-" * 60)
    cm = report["confusion_matrix"]
    print(f"Confusion Matrix   : TP={cm['true_positives']} | FP={cm['false_positives']} | TN={cm['true_negatives']} | FN={cm['false_negatives']}")
    print("=" * 60 + "\n")

    with open("data/eval_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print("Saved evaluation report to data/eval_report.json")

if __name__ == "__main__":
    main()
