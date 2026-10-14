
import os
import re
import time

from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError

from schemas import (
    CalculateMatchInput,
    CalculateMatchOutput,
    LearningPlanInput,
    LearningPlanOutput,
    RoleAnalysisInput,
    RoleAnalysisOutput,
    CandidateSkillAnalysisInput,
    CandidateSkillAnalysisOutput,
)

from vector_store import VectorStore


# =========================================================
# CONFIGURATION
# =========================================================

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

RESUME_INDEX_PATH = "data/resume_index.json"


# =========================================================
# ANALYZE ROLE
# =========================================================

def analyze_role(role):
    """
    Analyze a target role independently of the candidate's resume.
    """

    validated_input = RoleAnalysisInput(role=role)

    prompt = f"""
You are a career role analysis assistant.

Analyze this target job role:
{validated_input.role}

Return:
1. Technical skills commonly required.
2. Soft skills commonly expected.
3. Typical responsibilities.

Rules:
- Analyze only the target role.
- Do not assume the candidate has any skills.
- Do not invent candidate experience.
- Keep skills relevant to the role.
"""

    models = [
        "gemini-3.5-flash-lite",
        "gemini-3.5-flash",
    ]

    last_error = None

    for model in models:
        for attempt in range(3):
            try:
                print(
                    f"🤖 Role analysis using {model} "
                    f"(attempt {attempt + 1}/3)"
                )

                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": RoleAnalysisOutput,
                    },
                )

                result = RoleAnalysisOutput.model_validate_json(
                    response.text
                )

                return result.model_dump()

            except ServerError as error:
                last_error = error

                print(f"⚠️ {model} temporarily unavailable.")

                if attempt < 2:
                    time.sleep(2 ** attempt)

    raise RuntimeError(
        "Role analysis model is temporarily unavailable. "
        "Please try again shortly."
    ) from last_error


# =========================================================
# SKILL NORMALIZATION
# =========================================================


def normalize_skill(skill):
    """Normalize common technology aliases."""

    normalized = skill.lower().strip()

    aliases = {
        "react.js": "react",
        "react js": "react",
        "reactjs": "react",
        "rest api": "rest apis",
        "restful api": "rest apis",
        "restful apis": "rest apis",
        "node.js": "node.js",
        "node js": "node.js",
        "nodejs": "node.js",
        "sql database": "sql databases",
        "relational databases": "sql databases",
        "nosql database": "nosql databases",
    }

    normalized = re.sub(r"\s+", " ", normalized).strip()

    return aliases.get(normalized, normalized)



# =========================================================
# SKILL MATCHING
# =========================================================

def skills_match(required_skill, candidate_skill):
    """
    Match equivalent skill names and supported skill categories.

    Category matching is directional: knowing a specific
    technology can support a broad category, but knowing
    a broad category does not prove a specific technology.
    """

    required = normalize_skill(required_skill)
    candidate = normalize_skill(candidate_skill)

    # 1. Exact match after normalization.
    if required == candidate:
        return True

    # 2. Broader database categories.
    sql_technologies = {
        "sql",
        "postgresql",
        "mysql",
        "sqlite",
        "mariadb",
        "microsoft sql server",
        "oracle database",
    }

    nosql_technologies = {
        "mongodb",
        "cassandra",
        "couchdb",
        "dynamodb",
        "redis",
        "firebase",
    }

    if required == "sql databases":
        return candidate in sql_technologies

    if required == "nosql databases":
        return candidate in nosql_technologies

    # 3. Version-control category.
    if required == "version control":
        return candidate in {
            "git",
            "github",
            "gitlab",
            "bitbucket",
        }

    # 4. Programming-language requirements that explicitly
    # list examples, e.g. "Programming Languages (Python, Java)".
    if "(" in required_skill and ")" in required_skill:
        pattern = (
            r"(?<![a-z0-9])"
            + re.escape(candidate)
            + r"(?![a-z0-9])"
        )

        if re.search(pattern, required):
            return True

    return False


# =========================================================
# CALCULATE MATCH
# =========================================================

def calculate_match(required_skills, candidate_skills):
    """
    Calculate the match percentage using normalized,
    evidence-supported candidate skills.
    """

    validated_input = CalculateMatchInput(
        required_skills=required_skills,
        candidate_skills=candidate_skills,
    )

    # Deduplicate requirements without losing their labels.
    required = list(
        dict.fromkeys(validated_input.required_skills)
    )

    candidate = validated_input.candidate_skills

    matched = []
    missing = []

    for required_skill in required:
        is_matched = any(
            skills_match(required_skill, candidate_skill)
            for candidate_skill in candidate
        )

        if is_matched:
            matched.append(required_skill)
        else:
            missing.append(required_skill)

    match_percentage = (
        len(matched) / len(required) * 100
        if required
        else 0
    )

    result = {
        "matched_skills": matched,
        "missing_skills": missing,
        "match_percentage": round(match_percentage, 2),
    }

    validated_output = CalculateMatchOutput(**result)

    return validated_output.model_dump()


# =========================================================
# CREATE LEARNING PLAN
# =========================================================

def create_learning_plan(missing_skills):
    """
    Generate learning topics for missing skills.
    """

    validated_input = LearningPlanInput(
        missing_skills=missing_skills
    )

    plan = []

    for skill in validated_input.missing_skills:
        skill_lower = normalize_skill(skill)

        if skill_lower == "javascript":
            topics = [
                "ES6+ fundamentals",
                "Promises",
                "Async/Await",
                "DOM manipulation",
                "Closures",
            ]

        elif skill_lower == "rest apis":
            topics = [
                "HTTP methods",
                "HTTP status codes",
                "Building REST APIs with Express.js",
                "Request and response handling",
                "API authentication",
            ]

        elif skill_lower == "jwt":
            topics = [
                "Authentication fundamentals",
                "Access tokens",
                "Refresh tokens",
                "JWT verification",
                "Authorization",
            ]

        elif skill_lower == "data structures and algorithms":
            topics = [
                "Arrays and strings",
                "Hash maps and sets",
                "Stacks and queues",
                "Trees and graph fundamentals",
                "Time and space complexity",
            ]

        elif skill_lower == "testing and debugging frameworks":
            topics = [
                "Unit testing fundamentals",
                "Python testing with pytest",
                "JavaScript testing fundamentals",
                "Integration testing",
                "Debugging and edge cases",
            ]

        elif skill_lower == "ci/cd pipelines":
            topics = [
                "CI/CD fundamentals",
                "GitHub Actions workflows",
                "Automated test execution",
                "Build and deployment pipelines",
                "Environment variables and secrets",
            ]

        elif skill_lower == "cloud computing":
            topics = [
                "Cloud computing fundamentals",
                "Compute, storage, and networking",
                "Deploying a web application",
                "Cloud security basics",
                "Monitoring a deployed application",
            ]

        else:
            topics = [
                f"Learn {skill} fundamentals",
                f"Practice {skill} with hands-on exercises",
                f"Build a small project using {skill}",
            ]

        plan.append({
            "skill": skill,
            "topics": topics,
        })

    result = {
        "learning_plan": plan,
    }

    validated_output = LearningPlanOutput(**result)

    return validated_output.model_dump()


# =========================================================
# SEARCH RESUME
# =========================================================


def search_resume(query, top_k=3, store_path=None):
    selected_store_path = store_path or RESUME_INDEX_PATH

    vector_store = VectorStore(
        store_path=selected_store_path
    )
    vector_store.load()

    return vector_store.search(
        query=query,
        top_k=top_k
    )



# =========================================================
# TEST ERROR TOOL
# =========================================================

def test_error_tool(message):
    """Intentionally raise an error for error-handling tests."""

    raise ValueError(
        f"Tool failed intentionally: {message}"
    )


# =========================================================
# ANALYZE CANDIDATE SKILLS
# =========================================================

def analyze_candidate_skills(
    role,
    role_skills,
    resume_evidence,
):
    """
    Identify candidate skills supported by retrieved resume evidence.
    """

    validated_input = CandidateSkillAnalysisInput(
        role=role,
        role_skills=role_skills,
        resume_evidence=resume_evidence,
    )

    prompt = f"""
You are an evidence-based career analysis assistant.

Target role:
{validated_input.role}

Required role skills:
{validated_input.role_skills}

Resume evidence:
{validated_input.resume_evidence}

Identify skills supported by the supplied resume evidence.

Return:
1. candidate_skills: skills reasonably supported by the evidence.
2. skill_evidence: evidence supporting each candidate skill.

Rules:
- Use only the supplied resume evidence.
- Do not invent technologies or experience.
- Explicitly mentioned skills are strong evidence.
- Broader skills may be inferred only when the evidence
  strongly supports that inference.
- CNN combined with relevant computer-vision work may
  support computer vision or deep learning.
- React.js can support React experience.
- Node.js can support Node.js experience.
- PostgreSQL can support SQL database experience.
- Do not infer PyTorch from TensorFlow.
- Do not infer AWS from unrelated deployment work.
- Do not infer MLOps merely because an application was deployed.
- Do not list a required skill as a candidate skill merely
  because the role requires it.
- Include specific evidence for every claimed skill.
- Be conservative and evidence-based.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": CandidateSkillAnalysisOutput,
        },
    )

    result = CandidateSkillAnalysisOutput.model_validate_json(
        response.text
    )

    return result.model_dump()
