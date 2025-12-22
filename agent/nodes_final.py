

def generate_final_report_node(state: InterviewState) -> Dict[str, Any]:
    """
    Generate comprehensive final report when interview is completed.
    """
    print("--- Node: generate_final_report ---")
    
    from .llm_helpers import call_llm_generate_final_report
    
    interview_history = state.interview_history
    overall_score = state.overall_score
    job_role = state.job_role
    job_info = state.job_info
    
    if not interview_history:
        print("No interview history to generate report from.")
        return {"feedback": "Interview completed with no questions answered."}
    
    final_report = call_llm_generate_final_report(
        interview_history=interview_history,
        overall_score=overall_score,
        job_role=job_role,
        job_info=job_info,
    )
    
    if final_report:
        print("✅ Final report generated successfully")
        return {"feedback": final_report}
    else:
        print("❌ Failed to generate final report")
        # Fallback to basic summary
        avg_score = overall_score / len(interview_history) if interview_history else 0
        fallback_report = f"""
Interview Completed

Total Questions: {len(interview_history)}
Overall Score: {overall_score:.1f}/{len(interview_history) * 10}
Average Score: {avg_score:.1f}/10

Performance: {'Excellent' if avg_score >= 8 else 'Good' if avg_score >= 6 else 'Fair' if avg_score >= 4 else 'Needs Improvement'}

Thank you for completing the interview!
"""
        return {"feedback": fallback_report.strip()}
