document.addEventListener('DOMContentLoaded', () => {
    // Navigation Tabs
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            const target = btn.getAttribute('data-tab');
            document.getElementById(target).classList.add('active');
        });
    });

    // Drag and Drop File Upload
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('resume-file');
    const fileNameDisplay = document.getElementById('selected-file-name');

    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        if (e.dataTransfer.files.length > 0) {
            fileInput.files = e.dataTransfer.files;
            updateFileName();
        }
    });

    fileInput.addEventListener('change', updateFileName);

    function updateFileName() {
        if (fileInput.files.length > 0) {
            fileNameDisplay.textContent = `📄 Selected: ${fileInput.files[0].name}`;
        } else {
            fileNameDisplay.textContent = 'No file selected';
        }
    }

    // Match Analysis API Call
    const analyzeBtn = document.getElementById('analyze-btn');
    const resultsContainer = document.getElementById('results-container');

    analyzeBtn.addEventListener('click', async () => {
        const resumeText = document.getElementById('resume-text-input').value.trim();
        const jdText = document.getElementById('jd-text-input').value.trim();
        const file = fileInput.files[0];

        if (!file && !resumeText) {
            alert('Please upload a PDF/TXT resume or paste resume text.');
            return;
        }

        if (!jdText) {
            alert('Please paste the job description text.');
            return;
        }

        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '⏳ Analyzing Match & Extracting Skills...';

        const formData = new FormData();
        if (file) {
            formData.append('resume_file', file);
        }
        if (resumeText) {
            formData.append('resume_text', resumeText);
        }
        formData.append('job_description', jdText);

        try {
            const response = await fetch('/api/match', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'Failed to match resume.');
            }

            const data = await response.json();
            renderResults(data);
            resultsContainer.classList.remove('hidden');
            resultsContainer.scrollIntoView({ behavior: 'smooth' });

        } catch (error) {
            alert(`Error: ${error.message}`);
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = '<span class="btn-icon">⚡</span> Analyze Match & Extract Skill Gap';
        }
    });

    function renderResults(data) {
        // 1. Overall Match Score & Meter
        const score = data.overall_match_score;
        document.getElementById('match-score-value').textContent = `${score}%`;

        const meter = document.getElementById('score-meter');
        const circumference = 2 * Math.PI * 42; // ~263.89
        const offset = circumference - (score / 100) * circumference;
        meter.style.strokeDashoffset = offset;

        // Fit Badge
        const statusBadge = document.getElementById('fit-status-badge');
        statusBadge.textContent = data.match_status;
        statusBadge.className = `fit-status-badge ${data.status_color}`;

        // 2. Breakdown Bars
        const comp = data.score_breakdown;
        document.getElementById('embedding-sim-val').textContent = `${comp.embedding_similarity}%`;
        document.getElementById('embedding-sim-bar').style.width = `${comp.embedding_similarity}%`;

        document.getElementById('skill-cov-val').textContent = `${comp.skill_coverage_score}%`;
        document.getElementById('skill-cov-bar').style.width = `${comp.skill_coverage_score}%`;

        document.getElementById('lexical-sim-val').textContent = `${comp.lexical_tfidf_similarity}%`;
        document.getElementById('lexical-sim-bar').style.width = `${comp.lexical_tfidf_similarity}%`;

        // 3. ATS Score
        document.getElementById('ats-score-value').textContent = `${data.ats_analysis.ats_score}%`;
        document.getElementById('ats-word-count').textContent = `${data.ats_analysis.word_count} words parsed • ${data.ats_analysis.action_verbs_count} action verbs`;

        // 4. Missing Skills Ranked List
        const missingList = document.getElementById('missing-skills-list');
        missingList.innerHTML = '';

        if (data.skills_summary.missing_skills_ranked.length === 0) {
            missingList.innerHTML = '<p class="section-desc">🎉 No missing skills detected! Perfect skill overlap.</p>';
        } else {
            data.skills_summary.missing_skills_ranked.forEach(item => {
                const div = document.createElement('div');
                div.className = 'gap-item';
                div.innerHTML = `
                    <span class="gap-skill-name">${item.skill}</span>
                    <span class="gap-badge ${item.level}">${item.level} Importance (Score: ${item.importance_score})</span>
                `;
                missingList.appendChild(div);
            });
        }

        // 5. Matched Skills Tags
        const matchedContainer = document.getElementById('matched-skills-tags');
        matchedContainer.innerHTML = '';
        const matchedSkills = data.skills_summary.matched_skills;
        document.getElementById('matched-count-badge').textContent = `${matchedSkills.length} Found`;

        if (matchedSkills.length === 0) {
            matchedContainer.innerHTML = '<p class="section-desc">No direct skill matches detected.</p>';
        } else {
            matchedSkills.forEach(skill => {
                const tag = document.createElement('span');
                tag.className = 'skill-tag';
                tag.textContent = skill;
                matchedContainer.appendChild(tag);
            });
        }

        // 6. Recommendations
        const recList = document.getElementById('recommendations-list');
        recList.innerHTML = '';
        data.recommendations.forEach(rec => {
            const li = document.createElement('li');
            li.textContent = rec;
            recList.appendChild(li);
        });
    }

    // Evaluation Suite API Call
    const runEvalBtn = document.getElementById('run-eval-btn');
    const evalResultsContainer = document.getElementById('eval-results-container');

    runEvalBtn.addEventListener('click', async () => {
        runEvalBtn.disabled = true;
        runEvalBtn.innerHTML = '⏳ Running Evaluation Benchmark (50 Pairs)...';

        try {
            const response = await fetch('/api/evaluate');
            if (!response.ok) throw new Error('Evaluation failed.');
            const report = await response.json();
            renderEvalReport(report);
            evalResultsContainer.classList.remove('hidden');
        } catch (error) {
            alert(`Evaluation Error: ${error.message}`);
        } finally {
            runEvalBtn.disabled = false;
            runEvalBtn.innerHTML = '▶ Run Evaluation Suite';
        }
    });

    function renderEvalReport(report) {
        const m = report.metrics;
        document.getElementById('eval-precision').textContent = `${m.precision}%`;
        document.getElementById('eval-recall').textContent = `${m.recall}%`;
        document.getElementById('eval-f1').textContent = `${m.f1_score}%`;
        document.getElementById('eval-accuracy').textContent = `${m.accuracy}%`;
        document.getElementById('eval-mae').textContent = `${m.mean_absolute_error}`;

        const cm = report.confusion_matrix;
        document.getElementById('cm-tp').textContent = cm.true_positives;
        document.getElementById('cm-fp').textContent = cm.false_positives;
        document.getElementById('cm-fn').textContent = cm.false_negatives;
        document.getElementById('cm-tn').textContent = cm.true_negatives;

        const tableBody = document.getElementById('eval-table-body');
        tableBody.innerHTML = '';
        report.sample_results.forEach(row => {
            const tr = document.createElement('tr');
            const matchStatusText = row.predicted_match ? '✅ Match' : '❌ No Match';
            tr.innerHTML = `
                <td><strong>${row.candidate_role}</strong></td>
                <td>${row.jd_title}</td>
                <td><span class="gap-badge ${row.fit_label === 'HIGH' ? 'Critical' : (row.fit_label === 'MODERATE' ? 'High' : 'Medium')}">${row.fit_label}</span></td>
                <td><strong>${row.predicted_score}%</strong></td>
                <td>${matchStatusText}</td>
            `;
            tableBody.appendChild(tr);
        });
    }
});
