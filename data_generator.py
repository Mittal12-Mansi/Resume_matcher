import json
import os
import random

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# 1. Structured Skills Taxonomy
SKILLS_TAXONOMY = {
    "Languages": [
        "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust", 
        "ruby", "php", "swift", "kotlin", "scala", "r", "sql", "bash", "shell", "html", "css"
    ],
    "Frameworks & Libraries": [
        "react", "react.js", "next.js", "vue", "vue.js", "angular", "node.js", "express",
        "fastapi", "flask", "django", "spring boot", "dot net", ".net", "laravel",
        "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy", "opencv",
        "tailwind css", "bootstrap", "graphql", "rest api"
    ],
    "Cloud & DevOps": [
        "aws", "amazon web services", "azure", "gcp", "google cloud platform",
        "docker", "kubernetes", "k8s", "terraform", "ansible", "jenkins", "github actions",
        "gitlab ci", "ci/cd", "helm", "prometheus", "grafana", "linux", "nginx", "serverless"
    ],
    "Databases & Storage": [
        "postgresql", "postgres", "mysql", "mongodb", "redis", "elasticsearch",
        "dynamodb", "sqlite", "cassandra", "snowflake", "bigquery", "neo4j", "oracle"
    ],
    "AI & Data Science": [
        "machine learning", "deep learning", "nlp", "natural language processing",
        "computer vision", "generative ai", "llm", "large language models",
        "transformers", "rag", "retrieval augmented generation", "feature engineering",
        "data analysis", "data engineering", "time series", "reinforcement learning"
    ],
    "System & Software Engineering": [
        "system design", "distributed systems", "microservices", "object-oriented programming",
        "oop", "data structures", "algorithms", "design patterns", "event-driven architecture",
        "kafka", "rabbitmq", "grpc", "message queues", "caching", "scalability"
    ],
    "Tools & Platforms": [
        "git", "github", "gitlab", "jira", "confluence", "postman", "vscode",
        "figma", "tableau", "power bi", "spark", "hadoop", "airflow", "mlflow"
    ],
    "Soft Skills & Methodologies": [
        "agile", "scrum", "leadership", "problem solving", "communication",
        "project management", "teamwork", "critical thinking", "code review"
    ]
}

# Synonyms & Aliases for normalisation
SKILL_ALIASES = {
    "k8s": "kubernetes",
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "reactjs": "react",
    "vuejs": "vue",
    "nodejs": "node.js",
    "aws": "aws",
    "amazon web services": "aws",
    "gcp": "gcp",
    "google cloud": "gcp",
    "postgres": "postgresql",
    "nlp": "nlp",
    "natural language processing": "nlp",
    "ml": "machine learning",
    "dl": "deep learning",
    "ci/cd": "ci/cd",
    "continuous integration": "ci/cd"
}

# Roles for Synthetic Job Corpus (~500 postings)
ROLES_TEMPLATES = [
    {
        "role": "Senior Full Stack Software Engineer",
        "category": "Software Engineering",
        "skills": ["python", "javascript", "react", "fastapi", "postgresql", "docker", "aws", "system design", "git", "ci/cd", "microservices", "redis"]
    },
    {
        "role": "Backend Engineer (Go / Python)",
        "category": "Backend Development",
        "skills": ["go", "python", "postgresql", "docker", "kubernetes", "system design", "grpc", "kafka", "redis", "linux", "gcp"]
    },
    {
        "role": "Frontend Engineer (React / TypeScript)",
        "category": "Frontend Development",
        "skills": ["javascript", "typescript", "react", "next.js", "tailwind css", "html", "css", "graphql", "rest api", "figma", "jest"]
    },
    {
        "role": "Machine Learning Engineer",
        "category": "AI / ML",
        "skills": ["python", "pytorch", "tensorflow", "scikit-learn", "pandas", "numpy", "nlp", "deep learning", "docker", "fastapi", "mlflow", "aws"]
    },
    {
        "role": "DevOps / SRE Engineer",
        "category": "DevOps & Cloud",
        "skills": ["docker", "kubernetes", "terraform", "aws", "linux", "bash", "jenkins", "prometheus", "grafana", "python", "ansible", "ci/cd"]
    },
    {
        "role": "Data Scientist",
        "category": "Data Science",
        "skills": ["python", "r", "sql", "pandas", "numpy", "scikit-learn", "tableau", "machine learning", "data analysis", "bigquery", "statistics"]
    },
    {
        "role": "Data Engineer",
        "category": "Data Engineering",
        "skills": ["python", "sql", "spark", "hadoop", "airflow", "snowflake", "postgresql", "kafka", "aws", "data engineering", "docker"]
    },
    {
        "role": "AI / LLM Solutions Developer",
        "category": "AI / ML",
        "skills": ["python", "transformers", "generative ai", "llm", "rag", "fastapi", "langchain", "vector databases", "pytorch", "docker"]
    }
]

RESPONSIBILITIES_POOL = [
    "Design, develop, and maintain high-performance scalable software applications.",
    "Collaborate with cross-functional product and design teams to deliver quality features.",
    "Implement CI/CD automated deployment pipelines and robust unit testing.",
    "Optimize database queries, data schemas, and backend caching layers.",
    "Troubleshoot production incidents, perform code reviews, and mentor junior developers.",
    "Deploy microservices to cloud infrastructure using containerization tools like Docker and Kubernetes.",
    "Build machine learning models and integrate NLP algorithms into business workflows.",
    "Ensure security best practices, system reliability, and high availability standard."
]

def generate_job_postings_corpus(target_count=500):
    job_postings = []
    for i in range(target_count):
        template = random.choice(ROLES_TEMPLATES)
        num_skills = random.randint(6, 12)
        selected_skills = list(set(random.sample(template["skills"], min(len(template["skills"]), num_skills))))
        
        # Add a couple random extra skills for variability
        all_flat_skills = [s for sub in SKILLS_TAXONOMY.values() for s in sub]
        extra_skills = random.sample(all_flat_skills, 2)
        combined_skills = list(set(selected_skills + extra_skills))
        
        responsibilities = random.sample(RESPONSIBILITIES_POOL, random.randint(3, 5))
        
        job_text = f"Job Title: {template['role']}\n"
        job_text += f"Category: {template['category']}\n"
        job_text += "Overview:\nWe are seeking a talented professional to join our team.\n\n"
        job_text += "Key Responsibilities:\n" + "\n".join([f"- {r}" for r in responsibilities]) + "\n\n"
        job_text += "Required Technical Skills & Qualifications:\n"
        job_text += ", ".join([s.title() for s in combined_skills]) + ".\n"
        job_text += "Experience in system architecture, agile teamwork, and problem solving is highly preferred."

        job_postings.append({
            "id": f"job_{i+1:04d}",
            "title": template["role"],
            "category": template["category"],
            "description": job_text,
            "skills": combined_skills
        })
    return job_postings

# 2. Benchmark Evaluation Dataset (50 pairs)
def generate_eval_dataset():
    eval_pairs = []
    
    # Define test profiles
    profiles = [
        {
            "name": "Senior Full Stack Dev",
            "resume": """
John Doe - Senior Full Stack Developer
Email: john@example.com | Phone: (555) 123-4567 | GitHub: github.com/johndoe

SUMMARY:
Results-driven Full Stack Engineer with 5+ years of experience building modern web applications using Python, JavaScript, React, FastAPI, and PostgreSQL. Experienced with Docker containerization and AWS cloud deployments.

TECHNICAL SKILLS:
- Languages: Python, JavaScript, TypeScript, SQL, HTML/CSS
- Frameworks: React, FastAPI, Node.js, Express, Tailwind CSS
- Databases: PostgreSQL, MongoDB, Redis
- Cloud & DevOps: Docker, AWS (S3, EC2), Git, GitHub Actions, CI/CD
- Concepts: REST API, System Design, Microservices, Agile, OOP

EXPERIENCE:
Software Engineer | TechCorp Inc. (2021 - Present)
- Developed and scaled microservices architecture using Python and FastAPI, increasing request throughput by 40%.
- Designed responsive front-end dashboards in React with TypeScript, serving over 100k active monthly users.
- Automated deployment workflows with GitHub Actions and Docker containers on AWS EC2.
- Optimized PostgreSQL database queries and integrated Redis caching layer to reduce latency by 50ms.

EDUCATION:
B.S. in Computer Science | State University (2017 - 2021)
""",
            "res_skills": ["python", "javascript", "typescript", "sql", "html", "css", "react", "fastapi", "node.js", "express", "tailwind css", "postgresql", "mongodb", "redis", "docker", "aws", "git", "ci/cd", "rest api", "system design", "microservices", "agile", "oop"]
        },
        {
            "name": "Junior Data Scientist",
            "resume": """
Jane Smith - Data Scientist & ML Developer
Email: jane.smith@example.com | Portfolio: janesmith.ai

SUMMARY:
Passionate Data Scientist with strong background in Python, Machine Learning, Data Analysis, Pandas, NumPy, and Scikit-Learn. Passionate about natural language processing (NLP) and data visualization.

TECHNICAL SKILLS:
- Languages: Python, R, SQL
- Data Science & ML: Pandas, NumPy, Scikit-Learn, TensorFlow, Matplotlib, Seaborn, NLP
- Databases: MySQL, SQLite
- Tools: Jupyter Notebooks, Git, Tableau

PROJECTS:
Customer Churn Prediction Engine (2023)
- Built predictive Machine Learning model using Scikit-Learn and Random Forest classifier, achieving 88% accuracy.
- Conducted exploratory data analysis and feature engineering on dataset of 50,000 customer records.

NLP Text Classifier (2023)
- Tokenized and preprocessed text corpora using spaCy and NLTK for sentiment classification.

EDUCATION:
M.S. in Data Analytics | Tech Institute (2022 - 2024)
""",
            "res_skills": ["python", "r", "sql", "pandas", "numpy", "scikit-learn", "tensorflow", "nlp", "mysql", "sqlite", "git", "tableau", "machine learning", "data analysis"]
        },
        {
            "name": "DevOps & Infrastructure Engineer",
            "resume": """
Alex Rivera - DevOps Engineer
Email: alex.rivera@example.com | LinkedIn: linkedin.com/in/arivera

SUMMARY:
DevOps Engineer with 4 years of experience specializing in Cloud Infrastructure, Automation, Kubernetes, Docker, Terraform, and CI/CD pipelines on AWS.

SKILLS:
- Cloud & Infrastructure: AWS, Terraform, Ansible, Linux, CloudFormation
- Containerization & Orchestration: Docker, Kubernetes, Helm
- CI/CD & Automation: Jenkins, GitLab CI, Bash, Python
- Monitoring & Security: Prometheus, Grafana, Nginx, IAM

WORK EXPERIENCE:
Cloud DevOps Engineer | CloudScale Systems (2022 - Present)
- Managed production Kubernetes clusters (EKS) across multi-region AWS infrastructure.
- Authored infrastructure as code scripts using Terraform to provision VPCs, EKS, and RDS instances.
- Built automated CI/CD pipelines in GitLab CI to reduce build times by 35%.

EDUCATION:
B.S. in Information Technology (2018 - 2022)
""",
            "res_skills": ["aws", "terraform", "ansible", "linux", "docker", "kubernetes", "helm", "jenkins", "gitlab ci", "bash", "python", "prometheus", "grafana", "nginx", "ci/cd"]
        }
    ]

    # Generate 50 evaluated test pairs by combining resumes with target JDs
    pair_id = 1
    for i in range(50):
        profile = random.choice(profiles)
        
        # Pick fit type
        rand_val = random.random()
        if rand_val < 0.4:
            fit_label = "HIGH"
            # Matching JD
            if profile["name"] == "Senior Full Stack Dev":
                jd_title = "Senior Full Stack Engineer"
                jd_skills = ["python", "javascript", "react", "fastapi", "postgresql", "docker", "aws", "system design"]
            elif profile["name"] == "Junior Data Scientist":
                jd_title = "Data Scientist / ML Analyst"
                jd_skills = ["python", "sql", "pandas", "numpy", "scikit-learn", "machine learning", "data analysis", "tableau"]
            else:
                jd_title = "DevOps Engineer"
                jd_skills = ["aws", "terraform", "docker", "kubernetes", "linux", "ci/cd", "prometheus", "bash"]
            expected_score_range = (75, 100)
            should_match = True

        elif rand_val < 0.7:
            fit_label = "MODERATE"
            # Partial match JD (requires additional skills profile doesn't fully have)
            if profile["name"] == "Senior Full Stack Dev":
                jd_title = "Lead Backend & Cloud Engineer"
                jd_skills = ["python", "postgresql", "docker", "aws", "system design", "kubernetes", "go", "kafka", "grpc"]
            elif profile["name"] == "Junior Data Scientist":
                jd_title = "AI Research & Generative AI Specialist"
                jd_skills = ["python", "pytorch", "transformers", "generative ai", "llm", "rag", "deep learning", "fastapi", "docker"]
            else:
                jd_title = "Cloud Systems Architect"
                jd_skills = ["aws", "gcp", "azure", "terraform", "system design", "security", "python", "go"]
            expected_score_range = (50, 74)
            should_match = True

        else:
            fit_label = "LOW"
            # Mismatched JD
            if profile["name"] == "Senior Full Stack Dev":
                jd_title = "Senior Bio-Data Scientist"
                jd_skills = ["r", "bioinformatics", "genomics", "statistics", "matlab", "spark"]
            elif profile["name"] == "Junior Data Scientist":
                jd_title = "Principal Mobile Developer (iOS/Swift)"
                jd_skills = ["swift", "ios", "xcode", "objective-c", "mobile design", "uikit"]
            else:
                jd_title = "Senior Frontend Specialist (Vue/Angular)"
                jd_skills = ["angular", "vue.js", "bootstrap", "css3", "ui/ux", "figma", "storybook"]
            expected_score_range = (0, 49)
            should_match = False

        jd_text = f"Job Title: {jd_title}\n"
        jd_text += "Overview: Seeking a highly qualified engineer to join our fast-paced tech environment.\n"
        jd_text += "Required Skills: " + ", ".join([s.title() for s in jd_skills]) + ".\n"
        jd_text += "Key Tasks: Develop scalable solutions, write clean code, and drive system improvements."

        eval_pairs.append({
            "id": f"eval_{pair_id:03d}",
            "candidate_role": profile["name"],
            "jd_title": jd_title,
            "fit_label": fit_label,
            "should_match": should_match,
            "expected_score_min": expected_score_range[0],
            "expected_score_max": expected_score_range[1],
            "resume_text": profile["resume"].strip(),
            "resume_skills": profile["res_skills"],
            "jd_text": jd_text,
            "jd_skills": jd_skills
        })
        pair_id += 1

    return eval_pairs

def main():
    print("Generating skills taxonomy...")
    with open("data/skills_taxonomy.json", "w", encoding="utf-8") as f:
        json.dump({"taxonomy": SKILLS_TAXONOMY, "aliases": SKILL_ALIASES}, f, indent=2)
    print("Saved data/skills_taxonomy.json")

    print("Generating job postings corpus (~500 postings)...")
    postings = generate_job_postings_corpus(500)
    with open("data/job_postings.json", "w", encoding="utf-8") as f:
        json.dump(postings, f, indent=2)
    print("Saved data/job_postings.json with 500 job postings.")

    print("Generating evaluation benchmark dataset (50 Resume-JD pairs)...")
    eval_data = generate_eval_dataset()
    with open("data/eval_dataset.json", "w", encoding="utf-8") as f:
        json.dump(eval_data, f, indent=2)
    print("Saved data/eval_dataset.json with 50 benchmark pairs.")

if __name__ == "__main__":
    main()
