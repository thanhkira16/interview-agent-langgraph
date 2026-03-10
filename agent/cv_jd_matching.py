"""
CV-JD Matching and Question Generation Helpers
This module provides functions to calculate CV-JD matching scores
and generate targeted questions based on the matching results.
"""
from typing import Dict, Any, List, Optional
import json
import logging
from .models import CVInformation, JobInformation

logger = logging.getLogger(__name__)


def calculate_cv_jd_matching(
    cv_info: CVInformation,
    job_info: JobInformation,
    llm
) -> Dict[str, Any]:
    """
    Calculate matching score between CV and Job Description.
    Returns detailed matching analysis with scores for different aspects.
    """
    logger.info("Calculating CV-JD matching...")
    
    # Format CV information
    cv_summary = []
    if cv_info.skills:
        cv_summary.append(f"Skills: {', '.join(cv_info.skills)}")
    if cv_info.years_of_experience:
        cv_summary.append(f"Years of Experience: {cv_info.years_of_experience}")
    if cv_info.work_experience:
        cv_summary.append("Work Experience:")
        for exp in cv_info.work_experience[:5]:
            cv_summary.append(f"  - {exp.get('title')} at {exp.get('company')} ({exp.get('duration')})")
    if cv_info.education:
        cv_summary.append("Education:")
        for edu in cv_info.education:
            cv_summary.append(f"  - {edu.get('degree')} from {edu.get('institution')}")
    if cv_info.certifications:
        cv_summary.append(f"Certifications: {', '.join(cv_info.certifications)}")
    if cv_info.projects:
        cv_summary.append(f"Projects: {len(cv_info.projects)} project(s)")
        for proj in cv_info.projects[:3]:
            cv_summary.append(f"  - {proj.get('name')}: {', '.join(proj.get('technologies', []))}")
    
    # Format Job Description
    jd_summary = []
    if job_info.industry:
        jd_summary.append(f"Industry: {job_info.industry}")
    if job_info.job_level:
        jd_summary.append(f"Job Level: {job_info.job_level}")
    if job_info.employment_type:
        jd_summary.append(f"Employment Type: {job_info.employment_type}")
    if job_info.salary_range:
        jd_summary.append(f"Salary Range: {job_info.salary_range}")
    if job_info.job_description:
        jd_summary.append(f"Job Description:\n{job_info.job_description}")
    
    prompt = f"""
You are an expert recruiter analyzing the match between a candidate's CV and a job description.

Candidate CV:
{chr(10).join(cv_summary)}

Job Description:
{chr(10).join(jd_summary)}

Instructions:
Analyze how well the candidate's CV matches the job requirements. Consider:

1. **Skills Match**: Do the candidate's skills align with job requirements?
2. **Experience Level Match**: Does their experience level match the job level?
3. **Domain/Industry Match**: Is their background relevant to the industry?
4. **Education Match**: Does their education meet requirements?
5. **Project/Work Experience Relevance**: Are their past projects/roles relevant?

Provide your analysis in JSON format:

{{
  "overall_matching_score": 0-100,
  "matching_level": "Excellent | Good | Fair | Poor",
  "skills_matching": {{
    "score": 0-100,
    "matched_skills": ["skill1", "skill2", ...],
    "missing_skills": ["skill1", "skill2", ...],
    "transferable_skills": ["skill1", "skill2", ...]
  }},
  "experience_matching": {{
    "score": 0-100,
    "level_match": "Over-qualified | Perfect Match | Under-qualified",
    "relevant_experience": ["experience1", "experience2", ...],
    "gaps": ["gap1", "gap2", ...]
  }},
  "education_matching": {{
    "score": 0-100,
    "meets_requirements": true/false,
    "notes": "Brief note"
  }},
  "project_relevance": {{
    "score": 0-100,
    "relevant_projects": ["project1", "project2", ...],
    "key_technologies_match": ["tech1", "tech2", ...]
  }},
  "strengths": ["Strength 1", "Strength 2", ...],
  "concerns": ["Concern 1", "Concern 2", ...],
  "recommended_focus_areas": ["Area 1 to probe in interview", "Area 2", ...],
  "suggested_questions": [
    {{
      "area": "Skills | Experience | Projects | Education",
      "topic": "Specific topic to verify",
      "reason": "Why this should be asked"
    }}
  ]
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
        
        matching_result = json.loads(response_content)
        
        logger.info(f"✅ CV-JD Matching Score: {matching_result.get('overall_matching_score', 0)}/100")
        logger.info(f"   Matching Level: {matching_result.get('matching_level', 'Unknown')}")
        
        return matching_result
        
    except Exception as e:
        logger.error(f"Error calculating CV-JD matching: {e}")
        return {
            "overall_matching_score": 50,
            "matching_level": "Unknown",
            "error": str(e)
        }


def generate_targeted_question_from_matching(
    cv_jd_matching: Dict[str, Any],
    cv_info: CVInformation,
    job_info: JobInformation,
    interview_history: List[Dict[str, Any]],
    questions_asked_count: int,
    llm
) -> Dict[str, Any]:
    """
    Generate a targeted interview question based on CV-JD matching analysis.
    Focuses on areas with low matching scores or concerns.
    """
    logger.info("Generating targeted question from CV-JD matching...")
    
    # Extract key information from matching
    overall_score = cv_jd_matching.get('overall_matching_score', 50)
    missing_skills = cv_jd_matching.get('skills_matching', {}).get('missing_skills', [])
    matched_skills = cv_jd_matching.get('skills_matching', {}).get('matched_skills', [])
    concerns = cv_jd_matching.get('concerns', [])
    recommended_focus = cv_jd_matching.get('recommended_focus_areas', [])
    suggested_questions = cv_jd_matching.get('suggested_questions', [])
    experience_gaps = cv_jd_matching.get('experience_matching', {}).get('gaps', [])
    
    # Format history
    history_str = ""
    if interview_history:
        recent_topics = [
            turn.get('question', {}).get('topic', 'Unknown')
            for turn in interview_history[-3:]
            if turn.get('question')
        ]
        history_str = f"Recent topics covered: {', '.join(recent_topics)}"
    
    prompt = f"""
You are an expert AI interviewer generating the next question for a technical interview.

CV-JD Matching Analysis:
{'='*60}
Overall Matching Score: {overall_score}/100
Matching Level: {cv_jd_matching.get('matching_level', 'Unknown')}

Skills Analysis:
- Matched Skills: {', '.join(matched_skills[:10]) if matched_skills else 'None identified'}
- Missing Skills: {', '.join(missing_skills[:10]) if missing_skills else 'None identified'}

Experience Gaps: {', '.join(experience_gaps) if experience_gaps else 'None identified'}

Concerns to Address:
{chr(10).join(f"- {c}" for c in concerns[:5]) if concerns else '- None'}

Recommended Focus Areas:
{chr(10).join(f"- {f}" for f in recommended_focus[:5]) if recommended_focus else '- None'}

Suggested Question Areas:
{chr(10).join(f"- {q.get('area')}: {q.get('topic')} (Reason: {q.get('reason')})" for q in suggested_questions[:3]) if suggested_questions else '- None'}
{'='*60}

Interview Progress:
- Question Number: {questions_asked_count + 1}
- {history_str}

Instructions:
Generate the NEXT interview question that:

1. **Prioritizes verification of matched skills** - Ask about skills they claim to have that match the JD
2. **Probes concerns** - Address any concerns identified in the matching analysis
3. **Explores gaps** - Ask about missing skills or experience gaps to see if they have transferable knowledge
4. **Targets recommended focus areas** - Focus on areas suggested by the matching analysis
5. **Avoids repetition** - Don't ask about topics already covered in recent history

Question Strategy by Matching Score:
- **80-100 (Excellent)**: Ask advanced questions about matched skills to verify depth
- **60-79 (Good)**: Ask about matched skills and explore how they'd handle missing skills
- **40-59 (Fair)**: Focus on transferable skills and learning ability
- **0-39 (Poor)**: Assess foundational knowledge and potential to learn

Respond ONLY with valid JSON:

{{
  "question": {{
    "text": "The complete question text here",
    "topic": "Specific topic (e.g., 'Python Programming', 'System Design')",
    "difficulty": "Easy | Medium | Hard",
    "cv_verification_target": "What this question verifies (e.g., 'Python skill from CV')",
    "jd_alignment": "How this relates to JD requirements",
    "matching_focus": "matched_skill | missing_skill | experience_gap | concern | general"
  }}
}}
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
        
        result = json.loads(response_content)
        
        if 'question' in result:
            question_data = result['question']
            
            # Add unique ID
            import uuid
            question_data['id'] = f"cvjd_{uuid.uuid4().hex[:8]}"
            
            logger.info(f"✅ Generated CV-JD targeted question: {question_data.get('text', '')[:80]}...")
            logger.info(f"   Focus: {question_data.get('matching_focus', 'Unknown')}")
            logger.info(f"   JD Alignment: {question_data.get('jd_alignment', 'N/A')[:60]}...")
            
            return question_data
        else:
            logger.error("Generated response missing 'question' key")
            return None
            
    except Exception as e:
        logger.error(f"Error generating targeted question: {e}")
        return None


def get_priority_verification_targets(
    cv_jd_matching: Dict[str, Any],
    cv_verification: Optional['CVVerificationResults'] = None
) -> List[Dict[str, Any]]:
    """
    Get prioritized list of CV claims to verify based on:
    1. CV-JD matching (focus on matched skills first)
    2. Current verification status (unverified items)
    3. Concerns from matching analysis
    
    Returns list of targets with priority scores.
    """
    targets = []
    
    # 1. Matched skills (HIGH PRIORITY) - These are most relevant to the job
    matched_skills = cv_jd_matching.get('skills_matching', {}).get('matched_skills', [])
    for skill in matched_skills:
        # Check if already verified
        is_verified = False
        verification_score = 0
        
        if cv_verification:
            for skill_verif in cv_verification.skills_verification:
                if skill_verif.skill_name.lower() == skill.lower():
                    is_verified = skill_verif.verification_score >= 6
                    verification_score = skill_verif.verification_score
                    break
        
        if not is_verified:
            targets.append({
                "type": "skill",
                "name": skill,
                "priority": 100 - verification_score,  # Higher priority if lower verification
                "reason": "Matched skill from JD - needs verification",
                "jd_relevant": True
            })
    
    # 2. Missing skills (MEDIUM PRIORITY) - Check if they have transferable knowledge
    missing_skills = cv_jd_matching.get('skills_matching', {}).get('missing_skills', [])
    for skill in missing_skills[:5]:  # Top 5 missing skills
        targets.append({
            "type": "missing_skill",
            "name": skill,
            "priority": 60,
            "reason": "Missing skill from JD - assess transferable knowledge",
            "jd_relevant": True
        })
    
    # 3. Experience gaps (MEDIUM PRIORITY)
    experience_gaps = cv_jd_matching.get('experience_matching', {}).get('gaps', [])
    for gap in experience_gaps[:3]:
        targets.append({
            "type": "experience_gap",
            "name": gap,
            "priority": 70,
            "reason": "Experience gap identified",
            "jd_relevant": True
        })
    
    # 4. Concerns (HIGH PRIORITY)
    concerns = cv_jd_matching.get('concerns', [])
    for concern in concerns[:3]:
        targets.append({
            "type": "concern",
            "name": concern,
            "priority": 90,
            "reason": "Concern from matching analysis",
            "jd_relevant": True
        })
    
    # 5. Unverified CV items (LOWER PRIORITY if not JD-matched)
    if cv_verification:
        for skill_verif in cv_verification.skills_verification:
            if skill_verif.verification_score < 6:
                # Check if this skill is JD-relevant
                is_jd_relevant = skill_verif.skill_name in matched_skills
                
                if not is_jd_relevant:  # Only add if not already added above
                    targets.append({
                        "type": "skill",
                        "name": skill_verif.skill_name,
                        "priority": 40,
                        "reason": "Unverified CV skill (not in JD)",
                        "jd_relevant": False
                    })
    
    # Sort by priority (descending)
    targets.sort(key=lambda x: x['priority'], reverse=True)
    
    logger.info(f"📋 Generated {len(targets)} priority verification targets")
    if targets:
        logger.info(f"   Top priority: {targets[0]['name']} ({targets[0]['reason']})")
    
    return targets
