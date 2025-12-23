from typing import Dict, Any

from langgraph.types import interrupt

from .models import InterviewState
from langgraph.graph import END
from .database import fetch_questions_from_db
from .config import db
from datetime import datetime
from .llm_helpers import (
    call_llm_select_question,
    call_llm_analyze_and_evaluate_response,
    call_llm_generate_feedback,
)

def start_interview_node(state: InterviewState) -> Dict[str, Any]:
    print("--- Node: start_interview ---")
    job_role = state.job_role
    candidate_id = state.candidate_id

    print(f"Starting AI-powered interview for {candidate_id} ({job_role})")
    print("Interview mode: Dynamic question generation using AI")

    # No longer fetching questions from database
    # AI will generate questions dynamically based on context
    
    updates = {
        "interview_status": "in_progress",
        "questions_asked_count": 0,
        "overall_score": 0.0,
        "interview_history": [],
        "total_questions_planned": state.total_questions_planned,
        "current_question": None,
        "candidate_response": None,
        "response_analysis": None,
        "response_evaluation": None,
        "feedback": None,
        "error_message": None,
    }

    return updates
def select_question_node(state: InterviewState) -> Dict[str, Any]:
    print("--- Node: select_question ---")
    asked_count = state.questions_asked_count
    total_planned = state.total_questions_planned
    interview_history = state.interview_history
    job_role = state.job_role
    job_info = state.job_info

    if asked_count >= total_planned:
         print("System limit reached: Reached planned questions count. Forcing end.")
         return {"interview_status": "completed"}

    # Use AI to GENERATE question dynamically based on context
    # Instead of selecting from a fixed pool
    from .llm_helpers import call_llm_generate_question
    
    print(f"Generating question {asked_count + 1}/{total_planned} using AI...")
    generated_question = call_llm_generate_question(
        interview_history=interview_history,
        job_role=job_role,
        job_info=job_info,
        questions_asked_count=asked_count,
        total_planned=total_planned,
    )

    if generated_question is None:
        print("❌ LLM question generation failed.")
        error_message = "Failed to generate interview question."
        return {"interview_status": "terminated", "error_message": error_message}

    print(f"✅ Generated question: {generated_question.get('text', '')[:80]}...")
    
    updates = {
        "current_question": generated_question,
        "interview_status": state.interview_status
    }

    return updates
def ask_question_node(state: InterviewState) -> Dict[str, Any]:
    print("--- Node: ask_question ---")
    question = state.current_question

    if question and question.get('text'):
        print(f"\nAI Interviewer asks: {question['text']}\n")

    else:
        print("Error: No current question found in state to ask.")
        return {"error_message": state.error_message or "No question available to ask."}


    return {}
def receive_response_node(state: InterviewState) -> Dict[str, Any]:
    candidate_response = interrupt(
        {
            "Question": state.current_question
        }
    )

    print("--- Node: receive_response ---")

    updates = {
        "candidate_response": candidate_response,
        "error_message": None,
    }
    return updates
def process_response_node(state: InterviewState) -> Dict[str, Any]:
    print("--- Node: process_response ---")
    question = state.current_question
    response = state.candidate_response
    job_role = state.job_role
    job_info = state.job_info

    if not question or not response:
        print("Error: Missing question or response for processing.")
        error_msg = "Missing question or response for processing."
        return {"error_message": state.error_message or error_msg, "interview_status": "terminated"} # Terminate on critical error

    combined_result = call_llm_analyze_and_evaluate_response(question, response, job_role, job_info)

    updates = {}
    error_message = state.error_message

    if combined_result is None:
        print("Response analysis and evaluation failed.")
        error_message = error_message or "Response analysis and evaluation failed."
        updates = {"interview_status": "terminated"}
    else:
        print("Response analysis and evaluation successful.")
        updates = {
            "response_analysis": combined_result.get("analysis"),
            "response_evaluation": combined_result.get("evaluation"),
        }
        if combined_result.get("error_reason"):
             updates["error_message"] = combined_result["error_reason"]

    if error_message is not None:
        updates["error_message"] = error_message
    return updates
def generate_feedback_node(state: InterviewState) -> Dict[str, Any]:
    print("--- Node: generate_feedback ---")
    question = state.current_question
    response = state.candidate_response
    analysis = state.response_analysis
    evaluation = state.response_evaluation
    job_role = state.job_role
    job_info = state.job_info


    if not question or not response or not analysis or not evaluation:
        print("Error: Missing data (Q, A, Analysis, or Evaluation) for feedback generation.")
        error_msg = "Missing data for feedback generation."
        return {"error_message": state.error_message or error_msg, "interview_status": "terminated"}

    feedback_text = call_llm_generate_feedback(
        question=question,
        response=response,
        analysis=analysis,
        evaluation=evaluation,
        job_role=job_role,
        job_info=job_info,
    )

    updates = {}
    error_message = state.error_message

    if feedback_text is None:
        print("Feedback generation failed.")
        error_message = error_message or "Feedback generation failed."
        updates = {"interview_status": "terminated"}
    else:
        print("Feedback generation successful.")
        updates = {"feedback": feedback_text}

    if error_message is not None:
        updates["error_message"] = error_message

    return updates
def provide_feedback_node(state: InterviewState) -> Dict[str, Any]:
    print("--- Node: provide_feedback ---")
    feedback = state.feedback

    if feedback:
        print(f"\nAI Interviewer provides feedback: {feedback}\n")
    else:
        print("Error: No feedback found in state to provide.")

        pass
    return {}


def update_state_node(state: InterviewState) -> Dict[str, Any]:
    print("--- Node: update_state ---")

    current_cycle_data = {
        "question": state.current_question,
        "response": state.candidate_response,
        "analysis": state.response_analysis,
        "evaluation": state.response_evaluation,
        "feedback": state.feedback,
        "timestamp": datetime.now()
    }

    interview_history = state.interview_history + [current_cycle_data]

    latest_score = state.response_evaluation.get("score", 0.0) if state.response_evaluation else 0.0
    if latest_score is  None:
        latest_score=0
    current_overall_score = state.overall_score + latest_score

    new_questions_asked_count = state.questions_asked_count + 1

    print(f"Cycle completed: Q {new_questions_asked_count}. Score for this Q: {latest_score:.2f}. Cumulative Score: {current_overall_score:.2f}")

    interview_status = state.interview_status
    if new_questions_asked_count >= state.total_questions_planned:
        print("Completion criteria met: Reached planned questions count.")
        interview_status = "completed"
    elif state.error_message:
         print(f"Error message found: {state.error_message}. Setting status to terminated.")
         interview_status = "terminated"


    updates = {
        "interview_history": interview_history,
        "overall_score": current_overall_score,
        "questions_asked_count": new_questions_asked_count,
        "interview_status": interview_status,
        "current_question": None,
        "candidate_response": None,
    }

    return updates

def decide_next_after_select(state: InterviewState):

    print("--- Router: decide_next_after_select ---")
    if state.interview_status in ['completed', 'terminated']:
        print(f"Interview status is {state.interview_status}. Going to final report.")
        return "generate_final_report"
    elif state.current_question:
        print("Question selected. Proceeding to ask_question.")
        return "ask_question"
    else:
        print("No question selected and status not terminal. Going to final report.")
        return "generate_final_report"

def decide_next_after_update(state: InterviewState):

    print("--- Router: decide_next_after_update ---")
    if state.interview_status in ['completed', 'terminated']:
        print(f"Interview status is {state.interview_status}. Going to final report.")
        return "generate_final_report"
    elif state.questions_asked_count < state.total_questions_planned:
        print(f"Asked {state.questions_asked_count}/{state.total_questions_planned} questions. Proceeding to select next question.")
        return "select_question"
    else:
        print("Completion criteria met. Going to final report.")
        return "generate_final_report"



def generate_final_report_node(state: InterviewState) -> Dict[str, Any]:
    """
    Generate comprehensive final report when interview is completed.
    """
    print("--- Node: generate_final_report ---")
    
    from .llm_helpers import call_llm_generate_final_report
    import json
    
    interview_history = state.interview_history
    overall_score = state.overall_score
    job_role = state.job_role
    job_info = state.job_info
    
    if not interview_history:
        print("No interview history to generate report from.")
        fallback_report = {
            "executive_summary": "Interview completed with no questions answered.",
            "strengths": [],
            "areas_for_improvement": [],
            "technical_assessment": "Unable to assess.",
            "recommendation": {
                "final_score": "0/0",
                "average_score": 0,
                "hiring_recommendation": "Not Recommend",
                "justification": "No data available."
            },
            "additional_notes": "No interview data available."
        }
        return {"feedback": json.dumps(fallback_report, indent=2, ensure_ascii=False)}
    
    final_report = call_llm_generate_final_report(
        interview_history=interview_history,
        overall_score=overall_score,
        job_role=job_role,
        job_info=job_info,
    )
    
    if final_report:
        print("✅ Final report generated successfully")
        # Convert dict to JSON string with indentation
        return {"feedback": json.dumps(final_report, indent=2, ensure_ascii=False)}
    else:
        print("❌ Failed to generate final report")
        # Fallback to basic summary in JSON format
        avg_score = overall_score / len(interview_history) if interview_history else 0
        fallback_report = {
            "executive_summary": f"Interview completed for {job_role} position.",
            "strengths": ["Candidate engaged with interview questions."],
            "areas_for_improvement": ["Review feedback from individual questions for improvement areas."],
            "technical_assessment": f"Average performance: {avg_score:.1f}/10",
            "recommendation": {
                "final_score": f"{avg_score:.1f}/10",
                "average_score": round(avg_score, 2),
                "hiring_recommendation": "Maybe" if avg_score >= 5 else "Not Recommend",
                "justification": "See individual question evaluations for detailed assessment."
            },
            "additional_notes": "Thank you for completing the interview!"
        }
        return {"feedback": json.dumps(fallback_report, indent=2, ensure_ascii=False)}
