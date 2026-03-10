from typing import List, Dict, Any, Literal, Optional
from pydantic import BaseModel, Field
from .config import TOTAL_QUESTIONS_PLANNED

InterviewStatus = Literal['not_started', 'in_progress', 'completed', 'terminated']
VerificationStatus = Literal['not_verified', 'verified', 'partially_verified', 'unverified', 'inconsistent']

class JobInformation(BaseModel):
    industry: Optional[str] = None
    job_level: Optional[str] = None
    employment_type: Optional[str] = None
    salary_range: Optional[str] = None
    job_description: Optional[str] = None

class CVInformation(BaseModel):
    """Extracted information from candidate's CV"""
    candidate_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    work_experience: List[Dict[str, Any]] = Field(default_factory=list)  # [{title, company, duration, description}]
    education: List[Dict[str, Any]] = Field(default_factory=list)  # [{degree, institution, year}]
    certifications: List[str] = Field(default_factory=list)
    projects: List[Dict[str, Any]] = Field(default_factory=list)  # [{name, description, technologies}]
    summary: Optional[str] = None  # Professional summary/objective
    years_of_experience: Optional[int] = None
    raw_text: Optional[str] = None  # Full CV text for reference


# ============================================================================
# CV VERIFICATION MODELS - For Sub-Agent Verification System
# ============================================================================

class SkillVerificationResult(BaseModel):
    """Result of verifying a specific skill claim"""
    skill_name: str
    claimed_proficiency: Optional[str] = None  # e.g., "Expert", "Intermediate", "Beginner"
    verification_status: VerificationStatus = 'not_verified'
    verification_score: float = 0.0  # 0-10 scale
    questions_asked: List[str] = Field(default_factory=list)
    answers_summary: List[str] = Field(default_factory=list)
    evidence_for: List[str] = Field(default_factory=list)  # Evidence supporting the claim
    evidence_against: List[str] = Field(default_factory=list)  # Evidence contradicting the claim
    recommendation: Optional[str] = None  # Suggested action or assessment
    notes: Optional[str] = None


class WorkExperienceVerificationResult(BaseModel):
    """Result of verifying work experience claim"""
    position_title: str
    company: str
    duration_claimed: str
    verification_status: VerificationStatus = 'not_verified'
    verification_score: float = 0.0  # 0-10 scale
    responsibilities_verified: List[str] = Field(default_factory=list)
    responsibilities_unverified: List[str] = Field(default_factory=list)
    technical_depth_score: float = 0.0  # How deep is their knowledge of claimed work
    questions_asked: List[str] = Field(default_factory=list)
    answers_summary: List[str] = Field(default_factory=list)
    red_flags: List[str] = Field(default_factory=list)  # Inconsistencies or concerns
    strengths: List[str] = Field(default_factory=list)
    recommendation: Optional[str] = None
    notes: Optional[str] = None


class EducationVerificationResult(BaseModel):
    """Result of verifying education claim"""
    degree: str
    institution: str
    year: str
    verification_status: VerificationStatus = 'not_verified'
    verification_score: float = 0.0  # 0-10 scale
    knowledge_depth_score: float = 0.0  # Understanding of fundamental concepts
    questions_asked: List[str] = Field(default_factory=list)
    answers_summary: List[str] = Field(default_factory=list)
    topics_verified: List[str] = Field(default_factory=list)
    topics_weak: List[str] = Field(default_factory=list)
    recommendation: Optional[str] = None
    notes: Optional[str] = None


class CertificationVerificationResult(BaseModel):
    """Result of verifying certification claim"""
    certification_name: str
    verification_status: VerificationStatus = 'not_verified'
    verification_score: float = 0.0  # 0-10 scale
    practical_knowledge_score: float = 0.0  # Can they apply certified knowledge?
    questions_asked: List[str] = Field(default_factory=list)
    answers_summary: List[str] = Field(default_factory=list)
    concepts_verified: List[str] = Field(default_factory=list)
    concepts_weak: List[str] = Field(default_factory=list)
    recommendation: Optional[str] = None
    notes: Optional[str] = None


class ProjectVerificationResult(BaseModel):
    """Result of verifying project claim"""
    project_name: str
    technologies_claimed: List[str] = Field(default_factory=list)
    verification_status: VerificationStatus = 'not_verified'
    verification_score: float = 0.0  # 0-10 scale
    role_clarity_score: float = 0.0  # How clear is their role in the project
    technical_depth_score: float = 0.0  # Depth of technical understanding
    questions_asked: List[str] = Field(default_factory=list)
    answers_summary: List[str] = Field(default_factory=list)
    technologies_verified: List[str] = Field(default_factory=list)
    technologies_weak: List[str] = Field(default_factory=list)
    challenges_discussed: List[str] = Field(default_factory=list)
    red_flags: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    recommendation: Optional[str] = None
    notes: Optional[str] = None


class YearsOfExperienceVerificationResult(BaseModel):
    """Result of verifying years of experience claim"""
    claimed_years: int
    verification_status: VerificationStatus = 'not_verified'
    estimated_actual_years: Optional[int] = None  # Based on interview assessment
    verification_score: float = 0.0  # 0-10 scale
    maturity_indicators: List[str] = Field(default_factory=list)  # Signs of experience
    gaps_identified: List[str] = Field(default_factory=list)  # Areas lacking expected experience
    questions_asked: List[str] = Field(default_factory=list)
    answers_summary: List[str] = Field(default_factory=list)
    recommendation: Optional[str] = None
    notes: Optional[str] = None


class CVVerificationResults(BaseModel):
    """Aggregated results from all CV verification sub-agents"""
    overall_verification_score: float = 0.0  # 0-10 scale, average of all verifications
    overall_credibility: VerificationStatus = 'not_verified'
    
    # Individual verification results
    skills_verification: List[SkillVerificationResult] = Field(default_factory=list)
    work_experience_verification: List[WorkExperienceVerificationResult] = Field(default_factory=list)
    education_verification: List[EducationVerificationResult] = Field(default_factory=list)
    certifications_verification: List[CertificationVerificationResult] = Field(default_factory=list)
    projects_verification: List[ProjectVerificationResult] = Field(default_factory=list)
    years_experience_verification: Optional[YearsOfExperienceVerificationResult] = None
    
    # Summary insights
    total_questions_asked: int = 0
    total_items_verified: int = 0
    total_items_unverified: int = 0
    major_red_flags: List[str] = Field(default_factory=list)
    key_strengths: List[str] = Field(default_factory=list)
    areas_of_concern: List[str] = Field(default_factory=list)
    
    # Recommendations
    hiring_recommendation_impact: Optional[str] = None  # How CV verification affects hiring decision
    suggested_focus_areas: List[str] = Field(default_factory=list)  # Areas to probe further
    overall_assessment: Optional[str] = None


# ============================================================================
# UPDATED INTERVIEW STATE WITH CV VERIFICATION
# ============================================================================

class InterviewState(BaseModel):
    job_role: str
    candidate_id: str
    job_info: JobInformation = Field(default_factory=JobInformation)
    cv_info: Optional[CVInformation] = None  # CV information extracted from uploaded file
    cv_verification: Optional[CVVerificationResults] = None  # Results from CV verification sub-agents
    cv_jd_matching: Optional[Dict[str, Any]] = None  # NEW: CV-JD matching analysis results
    interview_history: List[Dict[str, Any]] = Field(default_factory=list)
    semantic_tree: Optional[Any] = Field(default=None, exclude=True)  # NEW: Semantic decision tree for token optimization (not serialized)
    current_question: Optional[Dict[str, Any]] = None
    candidate_response: Optional[str] = None
    response_analysis: Optional[Dict[str, Any]] = None
    response_evaluation: Optional[Dict[str, Any]] = None
    feedback: Optional[str] = None
    overall_score: float = 0.0
    interview_status: InterviewStatus = 'not_started'
    questions_asked_count: int = 0
    total_questions_planned: int = TOTAL_QUESTIONS_PLANNED
    available_questions_pool: List[Dict[str, Any]] = Field(default_factory=list)
    interview_config: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True