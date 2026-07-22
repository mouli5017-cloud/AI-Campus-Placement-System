import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class DatabaseConfig:
    HOST: str = "localhost"
    PORT: int = 3306
    USER: str = "root"
    PASSWORD: str = ""
    DATABASE: str = "campus_placement_ai"

    @property
    def connection_string(self) -> str:
        return (
            f"mysql+pymysql://{self.USER}:{self.PASSWORD}"
            f"@{self.HOST}:{self.PORT}/{self.DATABASE}"
        )


@dataclass
class MLConfig:
    RANDOM_STATE: int = 42
    TEST_SIZE: float = 0.2
    CV_FOLDS: int = 5
    MODEL_PATH: str = "src/models/saved_models/"
    MAX_FEATURES_RESUME: int = 5000
    MIN_SKILL_CONFIDENCE: float = 0.6


@dataclass
class NLPConfig:
    SPACY_MODEL: str = "en_core_web_sm"
    NLTK_DATA_PATH: str = "data/nltk_data/"
    MAX_SKILLS_EXTRACT: int = 30
    RESUME_MIN_LENGTH: int = 50


@dataclass
class SkillCategories:
    TECHNICAL_SKILLS: List[str] = field(default_factory=lambda: [
        "Python", "Java", "C++", "JavaScript", "TypeScript", "SQL", "NoSQL",
        "React", "Angular", "Vue.js", "Node.js", "Django", "Flask", "FastAPI",
        "TensorFlow", "PyTorch", "Scikit-learn", "Keras", "OpenCV",
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Jenkins",
        "Git", "Linux", "REST API", "GraphQL", "Redis", "MongoDB",
        "MySQL", "PostgreSQL", "HTML", "CSS", "Bootstrap", "Tailwind",
        "Spring Boot", "Microservices", "CI/CD", "DevOps", "Terraform",
        "Spark", "Hadoop", "Kafka", "Elasticsearch", "RabbitMQ",
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
        "Data Analysis", "Power BI", "Tableau", "Excel", "Pandas", "NumPy",
        "R", "MATLAB", "Scala", "Go", "Rust", "PHP", "Ruby",
        "Next.js", "Svelte", "SASS", "Webpack", "Vite",
        "Firebase", "Supabase", "Prisma", "GraphQL", "gRPC",
        "Celery", "RabbitMQ", "Apache Airflow", "MLflow", "Databricks",
        "Postman", "Swagger", "OAuth", "JWT", "WebSockets",
        "Unity", "Unreal Engine", "Blender", "Three.js",
        "Selenium", "Cypress", "JUnit", "Pytest", "Jest",
        "Ansible", "Puppet", "Prometheus", "Grafana", "Datadog",
        "Neo4j", "Cassandra", "DynamoDB", "CouchDB", "Firebase",
        "OpenAI API", "Hugging Face", "LangChain", "LLM",
        "Blockchain", "Solidity", "Web3", "Smart Contracts",
        "AR/VR", "IoT", "Edge Computing", "5G",
        "Agile", "Scrum", "JIRA", "Confluence",
        "Figma", "Adobe XD", "Sketch", "InVision",
    ])

    SOFT_SKILLS: List[str] = field(default_factory=lambda: [
        "Communication", "Leadership", "Team Work", "Problem Solving",
        "Critical Thinking", "Time Management", "Adaptability",
        "Creativity", "Decision Making", "Conflict Resolution",
        "Emotional Intelligence", "Public Speaking", "Negotiation",
        "Project Management", "Analytical Thinking",
    ])

    DOMAIN_SKILLS: List[str] = field(default_factory=lambda: [
        "Data Science", "Web Development", "Mobile Development",
        "Cloud Computing", "Cybersecurity", "Blockchain",
        "Internet of Things", "Artificial Intelligence",
        "Software Testing", "Database Administration",
        "Network Administration", "System Design",
        "DevOps Engineering", "Site Reliability Engineering",
    ])


@dataclass
class CompanyData:
    COMPANIES: List[Dict] = field(default_factory=lambda: [
        {"name": "TCS", "min_cgpa": 6.0, "min_salary": 3.36, "max_salary": 7.0,
         "skills": ["Java", "Python", "SQL", "Communication"]},
        {"name": "Infosys", "min_cgpa": 6.0, "min_salary": 3.6, "max_salary": 6.5,
         "skills": ["Java", "Python", "React", "SQL"]},
        {"name": "Wipro", "min_cgpa": 6.0, "min_salary": 3.5, "max_salary": 6.0,
         "skills": ["Java", "Python", "Angular", "SQL"]},
        {"name": "Accenture", "min_cgpa": 6.5, "min_salary": 4.5, "max_salary": 8.0,
         "skills": ["Python", "AWS", "Java", "Communication"]},
        {"name": "Cognizant", "min_cgpa": 6.0, "min_salary": 4.0, "max_salary": 7.5,
         "skills": ["Java", "Python", "SQL", "Spring Boot"]},
        {"name": "Capgemini", "min_cgpa": 6.0, "min_salary": 3.8, "max_salary": 7.0,
         "skills": ["Java", "Python", "React", "Docker"]},
        {"name": "Amazon", "min_cgpa": 7.0, "min_salary": 12.0, "max_salary": 30.0,
         "skills": ["Python", "Java", "AWS", "System Design", "DSA"]},
        {"name": "Google", "min_cgpa": 7.5, "min_salary": 18.0, "max_salary": 45.0,
         "skills": ["Python", "Java", "C++", "DSA", "System Design"]},
        {"name": "Microsoft", "min_cgpa": 7.0, "min_salary": 15.0, "max_salary": 40.0,
         "skills": ["C++", "Java", "Python", "DSA", "System Design"]},
        {"name": "Infosys BPM", "min_cgpa": 5.5, "min_salary": 2.5, "max_salary": 4.5,
         "skills": ["Communication", "Excel", "Data Analysis"]},
        {"name": "IBM", "min_cgpa": 6.5, "min_salary": 4.0, "max_salary": 12.0,
         "skills": ["Python", "Java", "Cloud Computing", "AI"]},
        {"name": "HCL Technologies", "min_cgpa": 6.0, "min_salary": 3.5, "max_salary": 7.0,
         "skills": ["Java", "Python", "Networking", "SQL"]},
        {"name": "Freshworks", "min_cgpa": 6.5, "min_salary": 5.0, "max_salary": 10.0,
         "skills": ["Ruby", "Python", "React", "SQL"]},
        {"name": "Zoho", "min_cgpa": 6.0, "min_salary": 4.5, "max_salary": 9.0,
         "skills": ["Java", "Python", "JavaScript", "SQL"]},
        {"name": "SAP Labs", "min_cgpa": 7.0, "min_salary": 8.0, "max_salary": 18.0,
         "skills": ["Java", "Python", "ABAP", "Cloud Computing"]},
        {"name": "Atlassian", "min_cgpa": 7.0, "min_salary": 12.0, "max_salary": 35.0,
         "skills": ["Java", "Python", "React", "System Design"]},
        {"name": "Flipkart", "min_cgpa": 7.0, "min_salary": 12.0, "max_salary": 30.0,
         "skills": ["Java", "Python", "React", "Microservices"]},
        {"name": "Swiggy", "min_cgpa": 6.5, "min_salary": 8.0, "max_salary": 20.0,
         "skills": ["Python", "Go", "React", "Kubernetes"]},
        {"name": "Razorpay", "min_cgpa": 6.5, "min_salary": 8.0, "max_salary": 22.0,
         "skills": ["Python", "Java", "React", "Microservices"]},
        {"name": "PhonePe", "min_cgpa": 7.0, "min_salary": 10.0, "max_salary": 28.0,
         "skills": ["Java", "Python", "React", "AWS"]},
        {"name": "Uber", "min_cgpa": 7.5, "min_salary": 18.0, "max_salary": 45.0,
         "skills": ["Python", "Java", "Go", "System Design", "DSA"]},
        {"name": "Adobe", "min_cgpa": 7.0, "min_salary": 12.0, "max_salary": 30.0,
         "skills": ["Java", "C++", "JavaScript", "React"]},
        {"name": "Nvidia", "min_cgpa": 7.5, "min_salary": 15.0, "max_salary": 40.0,
         "skills": ["C++", "Python", "CUDA", "Machine Learning"]},
        {"name": "Goldman Sachs", "min_cgpa": 7.0, "min_salary": 15.0, "max_salary": 35.0,
         "skills": ["Java", "Python", "DSA", "System Design"]},
    ])


@dataclass
class AppConfig:
    APP_NAME: str = "AI Campus Placement Prediction & Resume Screening"
    APP_VERSION: str = "1.0.0"
    APP_ICON: str = "🎓"
    PAGE_LAYOUT: str = "wide"
    PRIMARY_COLOR: str = "#1E88E5"
    BACKGROUND_COLOR: str = "#FFFFFF"
    MAX_UPLOAD_SIZE_MB: int = 10
    SESSION_TIMEOUT_MIN: int = 30
    ITEMS_PER_PAGE: int = 20

    db: DatabaseConfig = field(default_factory=DatabaseConfig)
    ml: MLConfig = field(default_factory=MLConfig)
    nlp: NLPConfig = field(default_factory=NLPConfig)
    skills: SkillCategories = field(default_factory=SkillCategories)
    companies: CompanyData = field(default_factory=CompanyData)


config = AppConfig()
