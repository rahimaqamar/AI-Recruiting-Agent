# ==========================================
# utils.py
# Utility Functions
# ==========================================
#  contains reusable functions that extract useful information from resumes and job descriptions.
import re
from pypdf import PdfReader     
from docx import Document        # python-docx

# ==========================================
# Skills List
# ==========================================

SKILLS = [
    "Python",
    "Java",
    "C++",
    "JavaScript",
    "TypeScript",
    "React",
    "Angular",
    "Vue",
    "Node.js",
    "Express",
    "FastAPI",
    "Flask",
    "Django",
    "SQL",
    "MySQL",
    "PostgreSQL",
    "MongoDB",
    "Oracle",
    "Docker",
    "Kubernetes",
    "AWS",
    "Azure",
    "GCP",
    "Git",
    "Linux",
    "REST API",
    "GraphQL",
    "Machine Learning",
    "Deep Learning",
    "TensorFlow",
    "PyTorch",
    "NLP",
    "LangChain",
    "ChromaDB"
]

# ==========================================
# Education List
# ==========================================
EDUCATION = [

    "BS Computer Science",
    "BS Software Engineering",
    "BS Information Technology",

    "BSc Computer Science",
    "B.Sc Computer Science",

    "MS Computer Science",
    "MS Software Engineering",

    "Bachelor",
    "Master",

    "MBA",
    "B.Tech",
    "M.Tech",

    "PhD",

    "Computer Science",
    "Software Engineering",
    "Information Technology"

]

# ==========================================
# Extract Text From PDF
# ==========================================

def extract_text_from_pdf(file_path):

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text

# ==========================================
# # Extract Text From DOCX
# # ==========================================

# def extract_text_from_pdf(file_path):
#     reader = PdfReader(file_path)

#     text = ""

#     for page in reader.pages:
#         page_text = page.extract_text()
#         if page_text:
#             text += page_text + "\n"

#     return text


# ==========================================
# Clean Text
# ==========================================

def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ==========================================
# Extract Experience
# ==========================================

def extract_experience(text):

    text = text.lower()

    patterns = [

        r'(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)',

        r'experience[:\s]*(\d+(?:\.\d+)?)',

        r'(\d+)\s*year',

    ]

    years = []

    for pattern in patterns:

        matches = re.findall(pattern, text)

        for m in matches:
            years.append(float(m))

    if years:
        return max(years)

    return 0.0


# ==========================================
# Extract Skills
# ==========================================



def extract_skills(text):
    """
    Extract skills using predefined skill list.
    """

    found_skills = []

    lower_text = text.lower()

    for skill in SKILLS:

        if skill.lower() in lower_text:
            found_skills.append(skill)

    return list(dict.fromkeys(found_skills))


# ==========================================
# Extract Education
# ==========================================



def extract_education(text):

    patterns = [
        r"BSCS",
        r"BSSE",
        r"BSIT",
        r"BS Computer Science",
        r"BS Software Engineering",
        r"BS Information Technology",
        r"Bachelor(?:'s)?(?:\s+of\s+[A-Za-z &]+)?",
        r"Master(?:'s)?(?:\s+of\s+[A-Za-z &]+)?",
        r"MSCS",
        r"MSSE",
        r"MBA",
        r"PhD",
        r"Diploma"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group()

    return "Unknown"

# ==========================================
# Extract Job Title
# ==========================================

def extract_job_title(text):

    lines = text.split("\n")

    for line in lines:

        line = line.strip()

        if len(line) > 5:

            return line

    return "Unknown Job"


# ==========================================
# Extract Job Location
# ==========================================

def extract_location(text):

    cities = [
        "Lahore",
        "Karachi",
        "Islamabad",
        "Rawalpindi",
        "Faisalabad",
        "Multan",
        "Peshawar",
        "Hyderabad",
        "Remote"
    ]

    text = text.lower()

    for city in cities:

        if city.lower() in text:

            return city

    return "Unknown"


# ==========================================
# Extract Job Category
# ==========================================

def extract_category(text):

    text = text.lower()

    categories = {

        "Python": [
            "python",
            "django",
            "fastapi",
            "flask"
        ],

        "Java": [
            "java",
            "spring"
        ],

        "Frontend": [
            "react",
            "angular",
            "vue"
        ],

        "Data Science": [
            "machine learning",
            "deep learning",
            "tensorflow",
            "pytorch"
        ],

        "DevOps": [
            "docker",
            "kubernetes",
            "aws",
            "azure"
        ]
    }

    for category, keywords in categories.items():

        for keyword in keywords:

            if keyword in text:

                return category

    return "General"


# ==========================================
# Extract Complete Job Information
# ==========================================

def extract_job_information(job_text):

    job_text = clean_text(job_text)

    return {

        "title": extract_job_title(job_text),
        "required_skills": extract_skills(job_text),
        "experience": extract_experience(job_text),
        "education": extract_education(job_text),
        "location": extract_location(job_text),
        "category": extract_category(job_text),
        "description": job_text
    }
def extract_pdf_text(file_path):
    return extract_text_from_pdf(file_path)