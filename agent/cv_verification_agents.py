"""
CV Verification Sub-Agents
Each sub-agent is responsible for verifying a specific section of the CV
through targeted interview questions and response analysis.
"""
from typing import Dict, Any, List, Optional
import json
import logging
from .models import (
    CVInformation,
    SkillVerificationResult,
    WorkExperienceVerificationResult,
    EducationVerificationResult,
    CertificationVerificationResult,
    ProjectVerificationResult,
    YearsOfExperienceVerificationResult,
    CVVerificationResults,
)

logger = logging.getLogger(__name__)


# ============================================================================
# SKILL VERIFICATION SUB-AGENT
# ============================================================================

def verify_skill_with_llm(
    skill_name: str,
    candidate_answer: str,
    question_asked: str,
    job_role: str,
    llm
) -> SkillVerificationResult:
    """
    Verify a specific skill claim based on candidate's answer to a targeted question.
    """
    logger.info(f"Verifying skill: {skill_name}")
    
    prompt = f"""
You are an expert technical interviewer verifying a candidate's skill claim.

Skill Being Verified: {skill_name}
Job Role: {job_role}
Question Asked: {question_asked}
Candidate's Answer: {candidate_answer}

Instructions:
Analyze the candidate's answer to determine if they truly possess the claimed skill.
Consider:
1. Technical accuracy of their answer
2. Depth of understanding (surface-level vs deep knowledge)
3. Practical application ability
4. Confidence and clarity in explanation
5. Use of correct terminology
6. Real-world experience indicators

Provide your assessment in JSON format:

{{
  "verification_status": "verified | partially_verified | unverified | inconsistent",
  "verification_score": 0-10,
  "claimed_proficiency": "Expert | Intermediate | Beginner | Unknown",
  "evidence_for": ["Point 1 supporting the claim", "Point 2", ...],
  "evidence_against": ["Point 1 contradicting the claim", "Point 2", ...],
  "recommendation": "Brief recommendation about this skill",
  "notes": "Additional observations"
}}

Respond ONLY with valid JSON.
"""
    
    try:
        llm_response = llm.invoke(prompt, {"recursion_limit": 100})
        response_content = llm_response.content.strip()
        
        # Clean markdown
        if response_content.startswith("```json"):
            response_content = response_content[7:].strip()
        if response_content.startswith("```"):
            response_content = response_content[3:].strip()
        if response_content.endswith("```"):
            response_content = response_content[:-3].strip()
        
        result_data = json.loads(response_content)
        
        return SkillVerificationResult(
            skill_name=skill_name,
            claimed_proficiency=result_data.get('claimed_proficiency'),
            verification_status=result_data.get('verification_status', 'not_verified'),
            verification_score=float(result_data.get('verification_score', 0)),
            questions_asked=[question_asked],
            answers_summary=[candidate_answer[:200]],
            evidence_for=result_data.get('evidence_for', []),
            evidence_against=result_data.get('evidence_against', []),
            recommendation=result_data.get('recommendation'),
            notes=result_data.get('notes')
        )
        
    except Exception as e:
        logger.error(f"Error verifying skill {skill_name}: {e}")
        return SkillVerificationResult(
            skill_name=skill_name,
            verification_status='not_verified',
            notes=f"Verification failed: {str(e)}"
        )


# ============================================================================
# WORK EXPERIENCE VERIFICATION SUB-AGENT
# ============================================================================

def verify_work_experience_with_llm(
    experience: Dict[str, Any],
    candidate_answer: str,
    question_asked: str,
    job_role: str,
    llm
) -> WorkExperienceVerificationResult:
    """
    Verify work experience claim based on candidate's answer.
    """
    position = experience.get('title', 'Unknown')
    company = experience.get('company', 'Unknown')
    logger.info(f"Verifying work experience: {position} at {company}")
    
    prompt = f"""
You are an expert interviewer verifying a candidate's work experience claim.

Claimed Experience:
- Position: {position}
- Company: {company}
- Duration: {experience.get('duration', 'Unknown')}
- Responsibilities: {experience.get('description', 'Not specified')}

Job Role Being Interviewed For: {job_role}
Question Asked: {question_asked}
Candidate's Answer: {candidate_answer}

Instructions:
Analyze the candidate's answer to verify their claimed work experience.
Consider:
1. Depth of knowledge about the role and responsibilities
2. Specific examples and details (vs vague descriptions)
3. Technical competence in claimed areas
4. Understanding of business context
5. Problem-solving approach
6. Red flags (inconsistencies, lack of detail, generic answers)

Provide your assessment in JSON format:

{{
  "verification_status": "verified | partially_verified | unverified | inconsistent",
  "verification_score": 0-10,
  "technical_depth_score": 0-10,
  "responsibilities_verified": ["Responsibility 1", "Responsibility 2", ...],
  "responsibilities_unverified": ["Responsibility 1", ...],
  "red_flags": ["Flag 1", "Flag 2", ...],
  "strengths": ["Strength 1", "Strength 2", ...],
  "recommendation": "Brief recommendation",
  "notes": "Additional observations"
}}

Respond ONLY with valid JSON.
"""
    
    try:
        llm_response = llm.invoke(prompt, {"recursion_limit": 100})
        response_content = llm_response.content.strip()
        
        # Clean markdown
        if response_content.startswith("```json"):
            response_content = response_content[7:].strip()
        if response_content.startswith("```"):
            response_content = response_content[3:].strip()
        if response_content.endswith("```"):
            response_content = response_content[:-3].strip()
        
        result_data = json.loads(response_content)
        
        return WorkExperienceVerificationResult(
            position_title=position,
            company=company,
            duration_claimed=experience.get('duration', 'Unknown'),
            verification_status=result_data.get('verification_status', 'not_verified'),
            verification_score=float(result_data.get('verification_score', 0)),
            technical_depth_score=float(result_data.get('technical_depth_score', 0)),
            responsibilities_verified=result_data.get('responsibilities_verified', []),
            responsibilities_unverified=result_data.get('responsibilities_unverified', []),
            questions_asked=[question_asked],
            answers_summary=[candidate_answer[:200]],
            red_flags=result_data.get('red_flags', []),
            strengths=result_data.get('strengths', []),
            recommendation=result_data.get('recommendation'),
            notes=result_data.get('notes')
        )
        
    except Exception as e:
        logger.error(f"Error verifying work experience: {e}")
        return WorkExperienceVerificationResult(
            position_title=position,
            company=company,
            duration_claimed=experience.get('duration', 'Unknown'),
            verification_status='not_verified',
            notes=f"Verification failed: {str(e)}"
        )


# ============================================================================
# EDUCATION VERIFICATION SUB-AGENT
# ============================================================================

def verify_education_with_llm(
    education: Dict[str, Any],
    candidate_answer: str,
    question_asked: str,
    job_role: str,
    llm
) -> EducationVerificationResult:
    """
    Verify education claim based on fundamental knowledge assessment.
    """
    degree = education.get('degree', 'Unknown')
    institution = education.get('institution', 'Unknown')
    logger.info(f"Verifying education: {degree} from {institution}")
    
    prompt = f"""
You are an expert interviewer verifying a candidate's education claim.

Claimed Education:
- Degree: {degree}
- Institution: {institution}
- Year: {education.get('year', 'Unknown')}

Job Role: {job_role}
Question Asked: {question_asked}
Candidate's Answer: {candidate_answer}

Instructions:
Assess whether the candidate has the fundamental knowledge expected from their claimed degree.
Consider:
1. Understanding of core concepts related to their field of study
2. Ability to apply theoretical knowledge
3. Depth vs breadth of knowledge
4. Critical thinking and problem-solving approach
5. Gaps in expected knowledge

Provide your assessment in JSON format:

{{
  "verification_status": "verified | partially_verified | unverified | inconsistent",
  "verification_score": 0-10,
  "knowledge_depth_score": 0-10,
  "topics_verified": ["Topic 1", "Topic 2", ...],
  "topics_weak": ["Topic 1", "Topic 2", ...],
  "recommendation": "Brief recommendation",
  "notes": "Additional observations"
}}

Respond ONLY with valid JSON.
"""
    
    try:
        llm_response = llm.invoke(prompt, {"recursion_limit": 100})
        response_content = llm_response.content.strip()
        
        # Clean markdown
        if response_content.startswith("```json"):
            response_content = response_content[7:].strip()
        if response_content.startswith("```"):
            response_content = response_content[3:].strip()
        if response_content.endswith("```"):
            response_content = response_content[:-3].strip()
        
        result_data = json.loads(response_content)
        
        return EducationVerificationResult(
            degree=degree,
            institution=institution,
            year=education.get('year', 'Unknown'),
            verification_status=result_data.get('verification_status', 'not_verified'),
            verification_score=float(result_data.get('verification_score', 0)),
            knowledge_depth_score=float(result_data.get('knowledge_depth_score', 0)),
            questions_asked=[question_asked],
            answers_summary=[candidate_answer[:200]],
            topics_verified=result_data.get('topics_verified', []),
            topics_weak=result_data.get('topics_weak', []),
            recommendation=result_data.get('recommendation'),
            notes=result_data.get('notes')
        )
        
    except Exception as e:
        logger.error(f"Error verifying education: {e}")
        return EducationVerificationResult(
            degree=degree,
            institution=institution,
            year=education.get('year', 'Unknown'),
            verification_status='not_verified',
            notes=f"Verification failed: {str(e)}"
        )


# ============================================================================
# CERTIFICATION VERIFICATION SUB-AGENT
# ============================================================================

def verify_certification_with_llm(
    certification_name: str,
    candidate_answer: str,
    question_asked: str,
    job_role: str,
    llm
) -> CertificationVerificationResult:
    """
    Verify certification claim based on practical knowledge.
    """
    logger.info(f"Verifying certification: {certification_name}")
    
    prompt = f"""
You are an expert interviewer verifying a candidate's certification claim.

Claimed Certification: {certification_name}
Job Role: {job_role}
Question Asked: {question_asked}
Candidate's Answer: {candidate_answer}

Instructions:
Assess whether the candidate truly understands and can apply the knowledge from their claimed certification.
Consider:
1. Practical application of certified concepts
2. Understanding of certification-specific terminology
3. Real-world use cases
4. Depth beyond memorization
5. Currency of knowledge (is it up-to-date?)

Provide your assessment in JSON format:

{{
  "verification_status": "verified | partially_verified | unverified | inconsistent",
  "verification_score": 0-10,
  "practical_knowledge_score": 0-10,
  "concepts_verified": ["Concept 1", "Concept 2", ...],
  "concepts_weak": ["Concept 1", ...],
  "recommendation": "Brief recommendation",
  "notes": "Additional observations"
}}

Respond ONLY with valid JSON.
"""
    
    try:
        llm_response = llm.invoke(prompt, {"recursion_limit": 100})
        response_content = llm_response.content.strip()
        
        # Clean markdown
        if response_content.startswith("```json"):
            response_content = response_content[7:].strip()
        if response_content.startswith("```"):
            response_content = response_content[3:].strip()
        if response_content.endswith("```"):
            response_content = response_content[:-3].strip()
        
        result_data = json.loads(response_content)
        
        return CertificationVerificationResult(
            certification_name=certification_name,
            verification_status=result_data.get('verification_status', 'not_verified'),
            verification_score=float(result_data.get('verification_score', 0)),
            practical_knowledge_score=float(result_data.get('practical_knowledge_score', 0)),
            questions_asked=[question_asked],
            answers_summary=[candidate_answer[:200]],
            concepts_verified=result_data.get('concepts_verified', []),
            concepts_weak=result_data.get('concepts_weak', []),
            recommendation=result_data.get('recommendation'),
            notes=result_data.get('notes')
        )
        
    except Exception as e:
        logger.error(f"Error verifying certification: {e}")
        return CertificationVerificationResult(
            certification_name=certification_name,
            verification_status='not_verified',
            notes=f"Verification failed: {str(e)}"
        )


# ============================================================================
# PROJECT VERIFICATION SUB-AGENT
# ============================================================================

def verify_project_with_llm(
    project: Dict[str, Any],
    candidate_answer: str,
    question_asked: str,
    job_role: str,
    llm
) -> ProjectVerificationResult:
    """
    Verify project claim based on technical depth and role clarity.
    """
    project_name = project.get('name', 'Unknown Project')
    logger.info(f"Verifying project: {project_name}")
    
    prompt = f"""
You are an expert interviewer verifying a candidate's project claim.

Claimed Project:
- Name: {project_name}
- Description: {project.get('description', 'Not specified')}
- Technologies: {', '.join(project.get('technologies', []))}

Job Role: {job_role}
Question Asked: {question_asked}
Candidate's Answer: {candidate_answer}

Instructions:
Assess the candidate's actual involvement and technical depth in the claimed project.
Consider:
1. Clarity about their specific role and contributions
2. Technical depth in claimed technologies
3. Understanding of project architecture and design decisions
4. Challenges faced and how they were solved
5. Red flags (vague answers, lack of detail, inconsistencies)
6. Evidence of hands-on work vs theoretical knowledge

Provide your assessment in JSON format:

{{
  "verification_status": "verified | partially_verified | unverified | inconsistent",
  "verification_score": 0-10,
  "role_clarity_score": 0-10,
  "technical_depth_score": 0-10,
  "technologies_verified": ["Tech 1", "Tech 2", ...],
  "technologies_weak": ["Tech 1", ...],
  "challenges_discussed": ["Challenge 1", ...],
  "red_flags": ["Flag 1", ...],
  "strengths": ["Strength 1", ...],
  "recommendation": "Brief recommendation",
  "notes": "Additional observations"
}}

Respond ONLY with valid JSON.
"""
    
    try:
        llm_response = llm.invoke(prompt, {"recursion_limit": 100})
        response_content = llm_response.content.strip()
        
        # Clean markdown
        if response_content.startswith("```json"):
            response_content = response_content[7:].strip()
        if response_content.startswith("```"):
            response_content = response_content[3:].strip()
        if response_content.endswith("```"):
            response_content = response_content[:-3].strip()
        
        result_data = json.loads(response_content)
        
        return ProjectVerificationResult(
            project_name=project_name,
            technologies_claimed=project.get('technologies', []),
            verification_status=result_data.get('verification_status', 'not_verified'),
            verification_score=float(result_data.get('verification_score', 0)),
            role_clarity_score=float(result_data.get('role_clarity_score', 0)),
            technical_depth_score=float(result_data.get('technical_depth_score', 0)),
            questions_asked=[question_asked],
            answers_summary=[candidate_answer[:200]],
            technologies_verified=result_data.get('technologies_verified', []),
            technologies_weak=result_data.get('technologies_weak', []),
            challenges_discussed=result_data.get('challenges_discussed', []),
            red_flags=result_data.get('red_flags', []),
            strengths=result_data.get('strengths', []),
            recommendation=result_data.get('recommendation'),
            notes=result_data.get('notes')
        )
        
    except Exception as e:
        logger.error(f"Error verifying project: {e}")
        return ProjectVerificationResult(
            project_name=project_name,
            technologies_claimed=project.get('technologies', []),
            verification_status='not_verified',
            notes=f"Verification failed: {str(e)}"
        )


# ============================================================================
# YEARS OF EXPERIENCE VERIFICATION SUB-AGENT
# ============================================================================

def verify_years_of_experience_with_llm(
    claimed_years: int,
    interview_history: List[Dict[str, Any]],
    job_role: str,
    llm
) -> YearsOfExperienceVerificationResult:
    """
    Verify years of experience claim based on overall interview performance.
    This is called at the end of the interview to assess maturity level.
    """
    logger.info(f"Verifying years of experience: {claimed_years} years claimed")
    
    # Summarize interview history
    history_summary = []
    for i, turn in enumerate(interview_history[-10:], 1):  # Last 10 questions
        if turn.get('question') and turn.get('response'):
            history_summary.append(f"Q{i}: {turn['question'].get('text', '')[:100]}")
            history_summary.append(f"A{i}: {turn['response'][:150]}")
            if turn.get('evaluation'):
                history_summary.append(f"Score: {turn['evaluation'].get('score', 'N/A')}/10")
    
    prompt = f"""
You are an expert interviewer assessing a candidate's claimed years of experience.

Claimed Years of Experience: {claimed_years} years
Job Role: {job_role}

Interview Performance Summary:
{chr(10).join(history_summary)}

Instructions:
Based on the candidate's overall interview performance, assess whether their claimed years of experience is accurate.
Consider:
1. Maturity indicators (problem-solving approach, best practices awareness, architectural thinking)
2. Depth of knowledge (surface-level vs deep understanding)
3. Breadth of experience (exposure to different aspects of the field)
4. Communication and articulation (clarity, use of terminology)
5. Gaps that would be unusual for someone with claimed experience
6. Signs of inflated or deflated experience claims

Provide your assessment in JSON format:

{{
  "verification_status": "verified | partially_verified | unverified | inconsistent",
  "verification_score": 0-10,
  "estimated_actual_years": 0-20,
  "maturity_indicators": ["Indicator 1", "Indicator 2", ...],
  "gaps_identified": ["Gap 1", "Gap 2", ...],
  "recommendation": "Brief recommendation about experience level",
  "notes": "Additional observations"
}}

Respond ONLY with valid JSON.
"""
    
    try:
        llm_response = llm.invoke(prompt, {"recursion_limit": 100})
        response_content = llm_response.content.strip()
        
        # Clean markdown
        if response_content.startswith("```json"):
            response_content = response_content[7:].strip()
        if response_content.startswith("```"):
            response_content = response_content[3:].strip()
        if response_content.endswith("```"):
            response_content = response_content[:-3].strip()
        
        result_data = json.loads(response_content)
        
        # Collect all questions asked
        all_questions = [turn.get('question', {}).get('text', '') for turn in interview_history if turn.get('question')]
        all_answers = [turn.get('response', '')[:100] for turn in interview_history if turn.get('response')]
        
        return YearsOfExperienceVerificationResult(
            claimed_years=claimed_years,
            verification_status=result_data.get('verification_status', 'not_verified'),
            estimated_actual_years=result_data.get('estimated_actual_years'),
            verification_score=float(result_data.get('verification_score', 0)),
            maturity_indicators=result_data.get('maturity_indicators', []),
            gaps_identified=result_data.get('gaps_identified', []),
            questions_asked=all_questions,
            answers_summary=all_answers,
            recommendation=result_data.get('recommendation'),
            notes=result_data.get('notes')
        )
        
    except Exception as e:
        logger.error(f"Error verifying years of experience: {e}")
        return YearsOfExperienceVerificationResult(
            claimed_years=claimed_years,
            verification_status='not_verified',
            notes=f"Verification failed: {str(e)}"
        )


# ============================================================================
# AGGREGATE CV VERIFICATION RESULTS
# ============================================================================

def aggregate_cv_verification_results(
    cv_verification: CVVerificationResults,
    llm
) -> CVVerificationResults:
    """
    Aggregate all verification results and generate overall assessment.
    """
    logger.info("Aggregating CV verification results...")
    
    # Calculate overall score
    all_scores = []
    
    for skill_result in cv_verification.skills_verification:
        all_scores.append(skill_result.verification_score)
    
    for exp_result in cv_verification.work_experience_verification:
        all_scores.append(exp_result.verification_score)
    
    for edu_result in cv_verification.education_verification:
        all_scores.append(edu_result.verification_score)
    
    for cert_result in cv_verification.certifications_verification:
        all_scores.append(cert_result.verification_score)
    
    for proj_result in cv_verification.projects_verification:
        all_scores.append(proj_result.verification_score)
    
    if cv_verification.years_experience_verification:
        all_scores.append(cv_verification.years_experience_verification.verification_score)
    
    overall_score = sum(all_scores) / len(all_scores) if all_scores else 0
    
    # Determine overall credibility
    if overall_score >= 8:
        overall_credibility = 'verified'
    elif overall_score >= 6:
        overall_credibility = 'partially_verified'
    elif overall_score >= 4:
        overall_credibility = 'unverified'
    else:
        overall_credibility = 'inconsistent'
    
    # Collect red flags and strengths
    major_red_flags = []
    key_strengths = []
    
    for exp_result in cv_verification.work_experience_verification:
        major_red_flags.extend(exp_result.red_flags)
        key_strengths.extend(exp_result.strengths)
    
    for proj_result in cv_verification.projects_verification:
        major_red_flags.extend(proj_result.red_flags)
        key_strengths.extend(proj_result.strengths)
    
    cv_verification.overall_verification_score = overall_score
    cv_verification.overall_credibility = overall_credibility
    cv_verification.major_red_flags = list(set(major_red_flags))[:10]  # Top 10 unique
    cv_verification.key_strengths = list(set(key_strengths))[:10]  # Top 10 unique
    
    # Count verified vs unverified
    verified_count = sum(1 for s in all_scores if s >= 6)
    cv_verification.total_items_verified = verified_count
    cv_verification.total_items_unverified = len(all_scores) - verified_count
    
    logger.info(f"✅ Overall CV verification score: {overall_score:.1f}/10 ({overall_credibility})")
    
    return cv_verification
