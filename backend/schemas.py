from pydantic import BaseModel, Field


# =========================================================
# JOB ANALYSIS
# =========================================================

class JobAnalysis(BaseModel):
    technical_skills: list[str]
    soft_skills: list[str]
    candidate_profile: str


# =========================================================
# CALCULATE MATCH - INPUT
# =========================================================

class CalculateMatchInput(BaseModel):
    required_skills: list[str] = Field(
        min_length=1,
        description="Skills required by the job."
    )

    candidate_skills: list[str] = Field(
        min_length=1,
        description="Skills possessed by the candidate."
    )


# =========================================================
# CALCULATE MATCH - OUTPUT
# =========================================================

class CalculateMatchOutput(BaseModel):
    matched_skills: list[str]

    missing_skills: list[str]

    match_percentage: float = Field(
        ge=0,
        le=100
    )


# =========================================================
# LEARNING PLAN - INPUT
# =========================================================

class LearningPlanInput(BaseModel):
    missing_skills: list[str] = Field(
        min_length=1,
        description="Skills the candidate needs to learn."
    )


# =========================================================
# LEARNING PLAN - OUTPUT
# =========================================================

class LearningPlanItem(BaseModel):
    skill: str
    topics: list[str]


class LearningPlanOutput(BaseModel):
    learning_plan: list[LearningPlanItem]
    
class RoleAnalysisInput(BaseModel):
    role: str = Field(
        min_length=2,
        description="The job role the candidate wants to apply for."
    )


class RoleAnalysisOutput(BaseModel):
    role: str
    technical_skills: list[str]
    soft_skills: list[str]
    responsibilities: list[str]
    
class CandidateSkillAnalysisInput(BaseModel):
    role: str
    role_skills: list[str]
    resume_evidence: str


class CandidateSkillEvidence(BaseModel):
    skill: str
    evidence: str


class CandidateSkillAnalysisOutput(BaseModel):
    candidate_skills: list[str]
    skill_evidence: list[CandidateSkillEvidence]
    
class PlanStep(BaseModel):
    step_number: int
    action: str
    tool: str
    reason: str


class AgentPlan(BaseModel):
    goal: str
    steps: list[PlanStep]
    
class AgentState(BaseModel):
    goal: str = ""

    phase: str = "resume_ready"

    target_role: str | None = None

    suggested_roles: list[dict] = []

    role_analysis: dict | None = None

    resume_evidence: str | None = None

    candidate_analysis: dict | None = None

    match_result: dict | None = None

    learning_plan: dict | None = None

    career_plan: dict | None = None

class TargetRoleOutput(BaseModel):
    role: str = Field(
        min_length=2,
        description="The job role the user wants to apply for."
    )
class SuggestedRole(BaseModel):
    role: str
    reason: str


class RoleSuggestionsOutput(BaseModel):
    suggested_roles: list[SuggestedRole]