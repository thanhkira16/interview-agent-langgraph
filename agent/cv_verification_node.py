"""
CV Verification Node - Processes responses and updates CV verification results
This node is called after each response to update verification status for CV claims
"""
from typing import Dict, Any
from .models import InterviewState, CVVerificationResults
from .cv_verification_agents import (
    verify_skill_with_llm,
    verify_work_experience_with_llm,
    verify_education_with_llm,
    verify_certification_with_llm,
    verify_project_with_llm,
    verify_years_of_experience_with_llm,
    aggregate_cv_verification_results,
)
from .config import llm
import logging

logger = logging.getLogger(__name__)


def cv_verification_node(state: InterviewState) -> Dict[str, Any]:
    """
    Node that processes candidate's response and updates CV verification results.
    This runs after process_response_node to verify CV claims based on answers.
    """
    print("--- Node: cv_verification ---")
    
    # Skip if no CV info
    if not state.cv_info:
        print("No CV information available, skipping verification")
        return {}
    
    question = state.current_question
    response = state.candidate_response
    job_role = state.job_role
    
    if not question or not response:
        print("No question or response to verify against")
        return {}
    
    # Initialize CV verification if not exists
    if state.cv_verification is None:
        cv_verification = CVVerificationResults()
    else:
        cv_verification = state.cv_verification
    
    question_text = question.get('text', '')
    question_topic = question.get('topic', '').lower()
    
    print(f"Analyzing response for CV verification (topic: {question_topic})")
    
    # Determine what CV claim this question is verifying
    # Based on question topic and content
    
    # Check if verifying a skill
    for skill in state.cv_info.skills[:5]:  # Check top 5 skills
        if skill.lower() in question_text.lower() or skill.lower() in question_topic:
            print(f"  → Verifying skill: {skill}")
            skill_result = verify_skill_with_llm(
                skill_name=skill,
                candidate_answer=response,
                question_asked=question_text,
                job_role=job_role,
                llm=llm
            )
            
            # Update or add skill verification
            existing_idx = next(
                (i for i, s in enumerate(cv_verification.skills_verification) 
                 if s.skill_name == skill), 
                None
            )
            if existing_idx is not None:
                # Update existing verification
                existing = cv_verification.skills_verification[existing_idx]
                existing.questions_asked.append(question_text)
                existing.answers_summary.append(response[:200])
                # Average the scores
                existing.verification_score = (existing.verification_score + skill_result.verification_score) / 2
                existing.evidence_for.extend(skill_result.evidence_for)
                existing.evidence_against.extend(skill_result.evidence_against)
            else:
                cv_verification.skills_verification.append(skill_result)
            
            cv_verification.total_questions_asked += 1
            break
    
    # Check if verifying work experience
    for exp in state.cv_info.work_experience[:3]:  # Check top 3 experiences
        position = exp.get('title', '').lower()
        company = exp.get('company', '').lower()
        
        if position in question_text.lower() or company in question_text.lower():
            print(f"  → Verifying work experience: {exp.get('title')} at {exp.get('company')}")
            exp_result = verify_work_experience_with_llm(
                experience=exp,
                candidate_answer=response,
                question_asked=question_text,
                job_role=job_role,
                llm=llm
            )
            
            # Update or add experience verification
            existing_idx = next(
                (i for i, e in enumerate(cv_verification.work_experience_verification) 
                 if e.position_title == exp.get('title') and e.company == exp.get('company')), 
                None
            )
            if existing_idx is not None:
                existing = cv_verification.work_experience_verification[existing_idx]
                existing.questions_asked.append(question_text)
                existing.answers_summary.append(response[:200])
                existing.verification_score = (existing.verification_score + exp_result.verification_score) / 2
                existing.technical_depth_score = (existing.technical_depth_score + exp_result.technical_depth_score) / 2
                existing.responsibilities_verified.extend(exp_result.responsibilities_verified)
                existing.red_flags.extend(exp_result.red_flags)
                existing.strengths.extend(exp_result.strengths)
            else:
                cv_verification.work_experience_verification.append(exp_result)
            
            cv_verification.total_questions_asked += 1
            break
    
    # Check if verifying education
    for edu in state.cv_info.education[:2]:  # Check top 2 education entries
        degree = edu.get('degree', '').lower()
        institution = edu.get('institution', '').lower()
        
        if degree in question_text.lower() or institution in question_text.lower():
            print(f"  → Verifying education: {edu.get('degree')}")
            edu_result = verify_education_with_llm(
                education=edu,
                candidate_answer=response,
                question_asked=question_text,
                job_role=job_role,
                llm=llm
            )
            
            existing_idx = next(
                (i for i, e in enumerate(cv_verification.education_verification) 
                 if e.degree == edu.get('degree') and e.institution == edu.get('institution')), 
                None
            )
            if existing_idx is not None:
                existing = cv_verification.education_verification[existing_idx]
                existing.questions_asked.append(question_text)
                existing.answers_summary.append(response[:200])
                existing.verification_score = (existing.verification_score + edu_result.verification_score) / 2
                existing.knowledge_depth_score = (existing.knowledge_depth_score + edu_result.knowledge_depth_score) / 2
                existing.topics_verified.extend(edu_result.topics_verified)
                existing.topics_weak.extend(edu_result.topics_weak)
            else:
                cv_verification.education_verification.append(edu_result)
            
            cv_verification.total_questions_asked += 1
            break
    
    # Check if verifying certification
    for cert in state.cv_info.certifications[:3]:  # Check top 3 certifications
        if cert.lower() in question_text.lower() or cert.lower() in question_topic:
            print(f"  → Verifying certification: {cert}")
            cert_result = verify_certification_with_llm(
                certification_name=cert,
                candidate_answer=response,
                question_asked=question_text,
                job_role=job_role,
                llm=llm
            )
            
            existing_idx = next(
                (i for i, c in enumerate(cv_verification.certifications_verification) 
                 if c.certification_name == cert), 
                None
            )
            if existing_idx is not None:
                existing = cv_verification.certifications_verification[existing_idx]
                existing.questions_asked.append(question_text)
                existing.answers_summary.append(response[:200])
                existing.verification_score = (existing.verification_score + cert_result.verification_score) / 2
                existing.practical_knowledge_score = (existing.practical_knowledge_score + cert_result.practical_knowledge_score) / 2
                existing.concepts_verified.extend(cert_result.concepts_verified)
                existing.concepts_weak.extend(cert_result.concepts_weak)
            else:
                cv_verification.certifications_verification.append(cert_result)
            
            cv_verification.total_questions_asked += 1
            break
    
    # Check if verifying project
    for proj in state.cv_info.projects[:3]:  # Check top 3 projects
        project_name = proj.get('name', '').lower()
        technologies = [t.lower() for t in proj.get('technologies', [])]
        
        if project_name in question_text.lower() or any(tech in question_text.lower() for tech in technologies):
            print(f"  → Verifying project: {proj.get('name')}")
            proj_result = verify_project_with_llm(
                project=proj,
                candidate_answer=response,
                question_asked=question_text,
                job_role=job_role,
                llm=llm
            )
            
            existing_idx = next(
                (i for i, p in enumerate(cv_verification.projects_verification) 
                 if p.project_name == proj.get('name')), 
                None
            )
            if existing_idx is not None:
                existing = cv_verification.projects_verification[existing_idx]
                existing.questions_asked.append(question_text)
                existing.answers_summary.append(response[:200])
                existing.verification_score = (existing.verification_score + proj_result.verification_score) / 2
                existing.role_clarity_score = (existing.role_clarity_score + proj_result.role_clarity_score) / 2
                existing.technical_depth_score = (existing.technical_depth_score + proj_result.technical_depth_score) / 2
                existing.technologies_verified.extend(proj_result.technologies_verified)
                existing.technologies_weak.extend(proj_result.technologies_weak)
                existing.challenges_discussed.extend(proj_result.challenges_discussed)
                existing.red_flags.extend(proj_result.red_flags)
                existing.strengths.extend(proj_result.strengths)
            else:
                cv_verification.projects_verification.append(proj_result)
            
            cv_verification.total_questions_asked += 1
            break
    
    return {"cv_verification": cv_verification}


def finalize_cv_verification_node(state: InterviewState) -> Dict[str, Any]:
    """
    Final node to aggregate all CV verification results and verify years of experience.
    Called at the end of the interview.
    """
    print("--- Node: finalize_cv_verification ---")
    
    if not state.cv_info or not state.cv_verification:
        print("No CV verification to finalize")
        return {}
    
    cv_verification = state.cv_verification
    
    # Verify years of experience based on overall interview performance
    if state.cv_info.years_of_experience:
        print(f"Verifying claimed {state.cv_info.years_of_experience} years of experience...")
        years_result = verify_years_of_experience_with_llm(
            claimed_years=state.cv_info.years_of_experience,
            interview_history=state.interview_history,
            job_role=state.job_role,
            llm=llm
        )
        cv_verification.years_experience_verification = years_result
    
    # Aggregate all results
    cv_verification = aggregate_cv_verification_results(cv_verification, llm)
    
    print(f"✅ CV Verification Complete:")
    print(f"   Overall Score: {cv_verification.overall_verification_score:.1f}/10")
    print(f"   Credibility: {cv_verification.overall_credibility}")
    print(f"   Items Verified: {cv_verification.total_items_verified}")
    print(f"   Items Unverified: {cv_verification.total_items_unverified}")
    print(f"   Red Flags: {len(cv_verification.major_red_flags)}")
    
    return {"cv_verification": cv_verification}
