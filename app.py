import streamlit as st
import PyPDF2

from ner_extractor import extract_skills_from_text
from similarity_engine import get_similarity_engine
from gap_analyzer import analyze_skill_gap
from ats_analyzer import compute_ats_score
from eval_engine import ModelEvaluator

st.set_page_config(page_title="AI Resume Matcher & Skill Gap", layout="wide", page_icon="⚡")

st.title("⚡ AI Resume ↔ Job Description Matcher (NER + Sentence Embeddings)")
st.caption("Advanced Resume Shortlisting, Skill Gap Analysis with TF-IDF Importance Weighting, and ATS Scoring")

tab1, tab2 = st.tabs(["🔍 Matcher & Skill Gap", "📊 Model Evaluation Benchmark"])

with tab1:
    col_input1, col_input2 = st.columns(2)

    with col_input1:
        st.subheader("📤 Candidate Resume")
        resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
        resume_text_manual = st.text_area("Or Paste Resume Text", height=180)

    with col_input2:
        st.subheader("💼 Job Description")
        job_desc = st.text_area("Paste Job Description", height=280)

    def extract_pdf_text(file):
        text = ""
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            t = page.extract_text()
            if t: text += t + "\n"
        return text

    if st.button("🔍 Analyze Match & Extract Skill Gap", type="primary"):
        resume_text = ""
        if resume_file:
            resume_text = extract_pdf_text(resume_file)
        elif resume_text_manual.strip():
            resume_text = resume_text_manual.strip()

        if resume_text and job_desc:
            # 1. Skill Extraction
            res_skills = extract_skills_from_text(resume_text)["skills"]
            jd_skills = extract_skills_from_text(job_desc)["skills"]

            # 2. Skill Gap
            gap_info = analyze_skill_gap(res_skills, jd_skills, job_desc)

            # 3. Match Score
            sim_engine = get_similarity_engine()
            match_res = sim_engine.compute_match_score(
                resume_text, job_desc, gap_info["matched_skills"], jd_skills
            )
            score = match_res["overall_match_score"]

            # 4. ATS Score
            ats_info = compute_ats_score(
                resume_text, job_desc, gap_info["matched_skills"], gap_info["missing_skills_ranked"]
            )

            # ---- UI DISPLAY ----
            m_col1, m_col2, m_col3 = st.columns(3)

            with m_col1:
                st.metric("📊 Overall Match Fit", f"{score}%")
                if score >= 75:
                    st.success("Strong Match")
                elif score >= 50:
                    st.warning("Moderate Match")
                else:
                    st.error("Low Match")

            with m_col2:
                st.metric("📄 ATS Readability Score", f"{ats_info['ats_score']}%")

            with m_col3:
                st.metric("🎯 Skill Coverage", f"{round(len(gap_info['matched_skills'])/max(1, len(jd_skills))*100, 1)}%")

            st.divider()

            # Breakdown
            st.subheader("📈 Score Components")
            b_col1, b_col2, b_col3 = st.columns(3)
            b_col1.metric("Semantic Embeddings", f"{match_res['components']['embedding_similarity']}%")
            b_col2.metric("Skill Coverage", f"{match_res['components']['skill_coverage_score']}%")
            b_col3.metric("Lexical Density (TF-IDF)", f"{match_res['components']['lexical_tfidf_similarity']}%")

            st.divider()

            s_col1, s_col2 = st.columns(2)

            with s_col1:
                st.subheader("❌ Missing Skills (Ranked by TF-IDF Importance)")
                if gap_info["missing_skills_ranked"]:
                    for item in gap_info["missing_skills_ranked"]:
                        lvl = item["level"]
                        st.markdown(f"- **{item['skill'].title()}** — *{lvl} Importance* (Score: `{item['importance_score']}`)")
                else:
                    st.success("No missing skills! Perfect coverage.")

            with s_col2:
                st.subheader("✅ Matched Skills")
                if gap_info["matched_skills"]:
                    st.write(", ".join([f"`{s}`" for s in gap_info["matched_skills"]]))
                else:
                    st.write("No matching skills detected.")

            st.divider()
            st.subheader("📌 Actionable Recommendations & ATS Tips")
            all_recs = gap_info["recommendations"] + ats_info["suggestions"]
            for r in all_recs:
                st.markdown(f"• {r}")

        else:
            st.warning("Please provide both candidate resume and job description text.")

with tab2:
    st.subheader("📊 Model Evaluation Benchmark Report")
    st.write("Evaluates precision, recall, F1-score, accuracy, and MAE on 50 benchmark Resume-JD test pairs.")

    if st.button("▶ Run Model Evaluation Suite"):
        evaluator = ModelEvaluator()
        report = evaluator.run_evaluation()

        e_col1, e_col2, e_col3, e_col4, e_col5 = st.columns(5)
        e_col1.metric("Precision", f"{report['metrics']['precision']}%")
        e_col2.metric("Recall", f"{report['metrics']['recall']}%")
        e_col3.metric("F1 Score", f"{report['metrics']['f1_score']}%")
        e_col4.metric("Accuracy", f"{report['metrics']['accuracy']}%")
        e_col5.metric("MAE Error", f"{report['metrics']['mean_absolute_error']}")

        st.subheader("Confusion Matrix")
        cm = report["confusion_matrix"]
        st.write(f"**True Positives**: {cm['true_positives']} | **False Positives**: {cm['false_positives']} | **True Negatives**: {cm['true_negatives']} | **False Negatives**: {cm['false_negatives']}")

        st.subheader("Sample Predictions Table")
        st.dataframe(report["sample_results"])