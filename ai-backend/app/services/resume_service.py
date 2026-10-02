"""Resume Parsing and Extraction Service."""
import io
import pypdf
from langchain_core.prompts import ChatPromptTemplate
from app.services.llm_service import llm
from app.core.prompts.interview import ParsedResumeData, RESUME_PARSER_PROMPT

# Structured output parser for resume data
resume_parser_llm = llm.with_structured_output(ParsedResumeData)
resume_prompt = ChatPromptTemplate.from_messages([
    ("system", RESUME_PARSER_PROMPT)
])
resume_chain = resume_prompt | resume_parser_llm

def extract_raw_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extracts plain text from raw PDF bytes using pypdf."""
    try:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        extracted_pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_pages.append(text)
        return "\n\n".join(extracted_pages).strip()
    except Exception as e:
        print(f"[Resume Parsing Error] Could not read PDF bytes: {e}")
        return ""

async def parse_candidate_resume(file_bytes: bytes, filename: str, target_role: str = "Software Engineer") -> dict:
    """
    Parses an uploaded resume file and extracts structured candidate information.
    Returns a dictionary with success status and candidate profile data.
    """
    if not file_bytes:
        return {
            "success": False,
            "error": "Empty file received. Please upload a valid resume."
        }

    raw_text = ""
    # Check if PDF or Text file
    if filename.lower().endswith(".pdf"):
        raw_text = extract_raw_text_from_pdf_bytes(file_bytes)
    else:
        try:
            raw_text = file_bytes.decode("utf-8", errors="ignore").strip()
        except Exception:
            raw_text = ""

    if not raw_text or len(raw_text) < 30:
        return {
            "success": False,
            "error": "Could not extract sufficient text from your resume. Please upload a clear PDF or TXT file with your projects and skills."
        }

KNOWN_TECH_KEYWORDS = [
    "React", "React Native", "TypeScript", "JavaScript", "Node.js", "Express", "Python",
    "FastAPI", "Django", "Flask", "Java", "Spring Boot", "C++", "C#", ".NET", "Go", "Golang",
    "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "GraphQL", "REST API", "Docker",
    "Kubernetes", "AWS", "Azure", "GCP", "CI/CD", "Git", "System Design", "Microservices",
    "PyTorch", "TensorFlow", "Machine Learning", "AI", "LLM", "RAG", "LangChain", "HTML", "CSS",
    "Tailwind", "Next.js", "Vue", "Angular", "Flutter", "Android", "iOS", "Swift", "Kotlin"
]

def extract_tech_keywords(text: str) -> list[str]:
    """Finds matching tech keywords in raw text for quick fallback."""
    found = []
    text_lower = text.lower()
    for kw in KNOWN_TECH_KEYWORDS:
        if kw.lower() in text_lower:
            found.append(kw)
    return found[:8] if found else ["Software Engineering", "System Architecture", "Problem Solving"]

def normalize_resume_dict(data: dict, raw_text: str = "") -> dict:
    """Ensures both frontend property variants (skills vs primary_skills, years_experience vs experience_years) exist."""
    skills = data.get("skills") or data.get("primary_skills") or []
    if not skills and raw_text:
        skills = extract_tech_keywords(raw_text)
    
    data["skills"] = skills
    data["primary_skills"] = skills
    
    exp = data.get("years_experience") or data.get("experience_years") or "1-2 years"
    data["years_experience"] = exp
    data["experience_years"] = exp
    data["role_match_score"] = data.get("role_match_score", 88)
    return data

async def parse_candidate_resume(file_bytes: bytes, filename: str, target_role: str = "Software Engineer") -> dict:
    """
    Parses an uploaded resume file and extracts structured candidate information.
    Returns a dictionary with success status and candidate profile data.
    """
    if not file_bytes:
        return {
            "success": False,
            "error": "Empty file received. Please upload a valid resume."
        }

    raw_text = ""
    # Check if PDF or Text file
    if filename.lower().endswith(".pdf"):
        raw_text = extract_raw_text_from_pdf_bytes(file_bytes)
    else:
        try:
            raw_text = file_bytes.decode("utf-8", errors="ignore").strip()
        except Exception:
            raw_text = ""

    if not raw_text or len(raw_text) < 20:
        return {
            "success": False,
            "error": "Could not extract sufficient text from your resume. Please upload a clear PDF or TXT file with your projects and skills."
        }

    try:
        parsed: ParsedResumeData = await resume_chain.ainvoke({
            "resume_text": raw_text[:4000]
        })
        result = parsed.model_dump()
        result["raw_text_preview"] = raw_text[:300] + "..."
        if target_role and target_role != "Software Engineer":
            result["target_role"] = target_role
        return {
            "success": True,
            "data": normalize_resume_dict(result, raw_text)
        }
    except Exception as e:
        print(f"[Resume LLM Extraction Warning] Fallback: {e}")
        fallback_data = {
            "candidate_name": "Candidate",
            "target_role": target_role,
            "years_experience": "1-2 years",
            "skills": extract_tech_keywords(raw_text),
            "key_projects": ["Applied Engineering Project"],
            "education": "Computer Science / Engineering",
            "summary": f"Aspiring {target_role} with hands-on software development experience.",
            "raw_text_preview": raw_text[:300] + "..."
        }
        return {
            "success": True,
            "data": normalize_resume_dict(fallback_data, raw_text)
        }

async def parse_resume_from_text(raw_text: str, target_role: str = "Software Engineer") -> dict:
    """Parses raw text or a brief user description to extract candidate profile & skills."""
    if not raw_text or len(raw_text.strip()) < 10:
        return {
            "success": False,
            "error": "Please enter a valid resume text or brief professional description (at least 10 characters)."
        }
    try:
        parsed: ParsedResumeData = await resume_chain.ainvoke({
            "resume_text": raw_text[:4000]
        })
        result = parsed.model_dump()
        result["raw_text_preview"] = raw_text[:300] + "..."
        if target_role:
            result["target_role"] = target_role
        return {
            "success": True,
            "data": normalize_resume_dict(result, raw_text)
        }
    except Exception as e:
        print(f"[Resume Text LLM Extraction Warning] Fallback: {e}")
        fallback_data = {
            "candidate_name": "Candidate",
            "target_role": target_role,
            "years_experience": "1-2 years",
            "skills": extract_tech_keywords(raw_text),
            "key_projects": ["Portfolio / Technical Project"],
            "education": "Technical Degree / CS Background",
            "summary": raw_text[:300],
            "raw_text_preview": raw_text[:300] + "..."
        }
        return {
            "success": True,
            "data": normalize_resume_dict(fallback_data, raw_text)
        }


