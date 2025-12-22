

def call_llm_generate_final_report(
        interview_history: List[Dict[str, Any]],
        overall_score: float,
        job_role: str,
        job_info: Optional[JobInformation] = None,
) -> str | None:
    """
    Generate comprehensive final interview report with overall assessment.
    Called when interview is completed.
    """
    print(f"-> LLM: Generating final interview report...")
    
    # Format job information
    job_info_str = ""
    if job_info:
        job_info_details = []
        if job_info.industry:
            job_info_details.append(f"Industry: {job_info.industry}")
        if job_info.job_level:
            job_info_details.append(f"Job Level: {job_info.job_level}")
        if job_info.employment_type:
            job_info_details.append(f"Employment Type: {job_info.employment_type}")
        if job_info.salary_range:
            job_info_details.append(f"Salary Range: {job_info.salary_range}")
        if job_info.job_description:
            job_info_details.append(f"Job Description: {job_info.job_description[:300]}...")
        job_info_str = "\n".join(job_info_details)
    
    # Calculate statistics
    total_questions = len(interview_history)
    if total_questions == 0:
        return "No questions were answered in this interview."
    
    average_score = overall_score / total_questions
    
    # Build comprehensive history summary
    history_summary = []
    for i, turn in enumerate(interview_history):
        history_summary.append(f"\n{'='*60}")
        history_summary.append(f"Question {i + 1}:")
        if turn.get('question'):
            history_summary.append(f"Topic: {turn['question'].get('topic', 'N/A')}")
            history_summary.append(f"Difficulty: {turn['question'].get('difficulty', 'N/A')}")
            history_summary.append(f"Q: {turn['question'].get('text', 'N/A')}")
        if turn.get('response'):
            history_summary.append(f"\nCandidate Answer:")
            history_summary.append(f"{turn['response'][:300]}{'...' if len(turn['response']) > 300 else ''}")
        if turn.get('evaluation'):
            eval_data = turn['evaluation']
            history_summary.append(f"\nEvaluation:")
            history_summary.append(f"  Score: {eval_data.get('score', 'N/A')}/10")
            history_summary.append(f"  Relevance: {eval_data.get('relevance_judgment', 'N/A')}")
            if eval_data.get('strengths'):
                history_summary.append(f"  Strengths: {', '.join(eval_data['strengths'][:3])}")
            if eval_data.get('areas_for_improvement'):
                history_summary.append(f"  Areas to improve: {', '.join(eval_data['areas_for_improvement'][:3])}")
    
    prompt_text = f"""
You are an expert AI interviewer providing a comprehensive final report for a {job_role} interview.

Interview Summary:
{'='*60}
Position: {job_role}
{job_info_str if job_info_str else 'No additional job information provided.'}
{'='*60}

Interview Statistics:
- Total Questions Asked: {total_questions}
- Total Score: {overall_score:.1f}/{total_questions * 10}
- Average Score per Question: {average_score:.1f}/10
- Overall Performance: {
    'Excellent' if average_score >= 8 else
    'Good' if average_score >= 6 else
    'Fair' if average_score >= 4 else
    'Needs Improvement'
}

Complete Interview Transcript:
{chr(10).join(history_summary)}
{'='*60}

Instructions:
Generate a comprehensive, professional final interview report that includes:

1. **Executive Summary** (2-3 sentences)
   - Overall impression of the candidate
   - Key takeaway from the interview

2. **Strengths** (3-5 bullet points)
   - What the candidate did well across all questions
   - Specific examples from their answers
   - Skills demonstrated

3. **Areas for Improvement** (3-5 bullet points)
   - Topics where the candidate struggled
   - Knowledge gaps identified
   - Specific recommendations for growth

4. **Technical Assessment** (if applicable to role)
   - Depth of technical knowledge
   - Problem-solving approach
   - Best practices awareness

5. **Overall Recommendation**
   - Final score: {overall_score:.1f}/{total_questions * 10} ({average_score:.1f}/10 average)
   - Hiring recommendation (Strongly Recommend / Recommend / Maybe / Not Recommend)
   - Justification based on job requirements

6. **Additional Notes**
   - Any standout moments (positive or negative)
   - Suggestions for next steps

Format the report professionally with clear sections and bullet points.
Be constructive, specific, and balanced in your assessment.
Consider the job requirements when making recommendations.

Provide ONLY the final report text. Do not include JSON or code formatting.
"""

    print(f"Sending final report prompt ({len(prompt_text)} chars) to LLM...")
    
    try:
        llm_response = llm.invoke(prompt_text, {"recursion_limit": 100})
        response_content = llm_response.content.strip()
        print("LLM final report received.")
        
        if not response_content:
            print("LLM final report response was empty.")
            return None
        
        print(f"Generated final report (first 100 chars): {response_content[:100]}...")
        return response_content
        
    except Exception as e:
        print(f"LLM final report generation failed: {e}")
        return None
