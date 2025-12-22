from typing import List, Dict, Any, Optional
import json
from .config import llm
from .models import JobInformation


def call_llm_generate_question(
        interview_history: List[Dict[str, Any]],
        job_role: str,
        job_info: Optional[JobInformation] = None,
        questions_asked_count: int = 0,
        total_planned: int = 5,
) -> Dict[str, Any] | None:
    """
    Use LLM to dynamically generate the next interview question based on context.
    This replaces selecting from a fixed pool.
    """
    print(f"→ LLM: Generating question {questions_asked_count + 1}/{total_planned}...")
    
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
            job_info_details.append(f"Job Description: {job_info.job_description}")
        job_info_str = "\n".join(job_info_details)
    
    # Format interview history
    history_summary = []
    if interview_history:
        history_summary.append(f"Previous {len(interview_history)} question(s) and answers:")
        for i, turn in enumerate(interview_history):
            history_summary.append(f"\nTurn {i + 1}:")
            if turn.get('question'):
                history_summary.append(f"  Q: {turn['question'].get('text', 'N/A')}")
            if turn.get('response'):
                history_summary.append(f"  A: {turn['response'][:200]}...")
            if turn.get('evaluation'):
                eval_details = turn['evaluation']
                score = eval_details.get('score', 'N/A')
                relevance = eval_details.get('relevance_judgment', 'N/A')
                history_summary.append(f"  Score: {score}/10, Relevance: {relevance}")
    
    prompt_text = f"""
You are an expert AI interviewer conducting a technical interview for a {job_role} position.

Job Context:
{'-' * 60}
Role: {job_role}
{job_info_str if job_info_str else 'No additional job information provided.'}
{'-' * 60}

Interview Progress:
- Current Question: {questions_asked_count + 1} of {total_planned}
- Questions Asked So Far: {questions_asked_count}

{chr(10).join(history_summary) if history_summary else 'This is the first question. No previous history.'}

Instructions:
1. **For the FIRST question** (if no history): Generate a warm-up question that assesses fundamental knowledge relevant to the {job_role} role and the job requirements.

2. **For SUBSEQUENT questions** (if history exists):
   - Analyze the candidate's previous answer(s) carefully
   - Identify areas where the candidate showed strength or weakness
   - Generate a follow-up question that:
     a) Explores topics the candidate mentioned but didn't fully explain
     b) Probes deeper into areas where they showed expertise
     c) Addresses gaps or misconceptions in their previous answers
     d) Progressively increases difficulty if candidate is performing well
     e) Adjusts to medium difficulty if candidate is struggling

3. **Question Quality Guidelines**:
   - Make questions specific to the role and job requirements
   - Ensure questions are clear and unambiguous
   - For technical roles, include practical scenarios when appropriate
   - Questions should be answerable in 2-3 minutes
   - Avoid yes/no questions; prefer open-ended questions

4. **Topics to Cover** (across all questions):
   - Technical skills relevant to {job_role}
   - Problem-solving ability
   - System design / Architecture (for senior roles)
   - Best practices and industry standards
   - Real-world application of knowledge

5. **Response Format**:
Respond ONLY with a valid JSON object in this exact format:

{{
  "question": {{
    "text": "The complete question text here",
    "topic": "Category/Topic of the question (e.g., 'System Design', 'Java Fundamentals', 'React Hooks')",
    "difficulty": "Easy | Medium | Hard",
    "rationale": "Brief explanation of why this question is chosen based on context"
  }}
}}

Important:
- Ensure the JSON is valid and properly formatted
- Do not include markdown code blocks or any extra text
- The question should be conversational and natural
- Consider the job level and requirements when setting difficulty
"""

    print(f"Sending question generation prompt ({len(prompt_text)} chars) to LLM...")
    
    try:
        llm_response = llm.invoke(prompt_text, {"recursion_limit": 100})
        response_content = llm_response.content.strip()
        print("LLM response received for question generation.")
        
        # Clean markdown formatting if present
        if response_content.startswith("```json"):
            response_content = response_content[len("```json"):].strip()
        if response_content.endswith("```"):
            response_content = response_content[:-len("```")].strip()
        
        # Parse JSON
        result = json.loads(response_content)
        
        if not isinstance(result, dict) or 'question' not in result:
            print(f"Invalid response structure: {result}")
            return None
        
        question_data = result['question']
        
        # Validate required fields
        if not question_data.get('text'):
            print("Generated question has no text")
            return None
        
        # Add a unique ID for tracking
        import uuid
        question_data['id'] = f"gen_{uuid.uuid4().hex[:8]}"
        
        print(f"✅ Generated question: {question_data.get('text')[:100]}...")
        print(f"   Topic: {question_data.get('topic')}, Difficulty: {question_data.get('difficulty')}")
        
        return question_data
        
    except json.JSONDecodeError as e:
        print(f"Failed to parse LLM response as JSON: {e}")
        print(f"Response was: {response_content[:200]}...")
        return None
    except Exception as e:
        print(f"Error generating question: {e}")
        return None


def call_llm_select_question(
        available_questions: List[Dict[str, Any]],
        interview_history: List[Dict[str, Any]],
        interview_config: Dict[str, Any],
        job_role: str,
        job_info: Optional[JobInformation] = None,
) -> Dict[str, Any] | None:
    """
    DEPRECATED: This function selects from a fixed pool.
    Use call_llm_generate_question() instead for dynamic question generation.
    
    Kept for backward compatibility.
    """
    print("⚠️ WARNING: Using deprecated call_llm_select_question. Consider using call_llm_generate_question instead.")
    print("Loading next question from pool...")

    history_summary = []
    for i, turn in enumerate(interview_history[-3:]):
        history_summary.append(f"Turn {len(interview_history) - len(interview_history[-3:]) + i + 1}:")
        if turn.get('question'):
            history_summary.append(f"Q: {turn['question'].get('text', 'N/A')}")
        if turn.get('response'):
            history_summary.append(f"A: {turn['response'][:150]}...")
        if turn.get('evaluation'):
            eval_details = turn['evaluation']
            history_summary.append(
                f"Eval: Score={eval_details.get('score')}, Relevance={eval_details.get('relevance')}")
        if turn.get('feedback'):
            history_summary.append(f"Feedback Points: {turn['feedback'][:100]}...")

    available_q_list = []
    for q in available_questions:
        if q.get('id') and q.get('text'):
            available_q_list.append(
                f"- ID: {q.get('id')}, Topic: {q.get('topic', 'N/A')}, Difficulty: {q.get('difficulty', 'N/A')}, Text: {q.get('text', '')[:100]}...")

    # Format job information for the prompt
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
            job_info_details.append(f"Job Description: {job_info.job_description[:200]}...")
        job_info_str = "\n".join(job_info_details)

    prompt_text = f"""
    You are an AI interviewer conducting an interview for a {job_role} role.
    Your goal is to select the best next question from the provided list or determine if the interview should end.

    Interview Context:
    - Job Role: {job_role}
    - Interview Configuration: {json.dumps(interview_config)}
    {f'- Job Information:{chr(10)}{job_info_str}' if job_info_str else ''}
    - Recent Interview History:
    {'-' * 20}
    {chr(10).join(history_summary) if history_summary else 'No history yet.'}
    {'-' * 20}

    Available Questions in Pool ({len(available_questions)} questions):
    {chr(10).join(available_q_list) if available_q_list else 'No questions left in pool.'}

    Instructions:
    1. Review the interview history to understand what has been covered and the candidate's performance (especially the most recent turn).
    2. Review the available questions, considering their topic and difficulty.
    3. Consider the job requirements (industry, level, employment type, description) when selecting questions that are most relevant to the role.
    4. Choose ONE best question from the "Available Questions in Pool" list to ask next. Prioritize covering diverse topics relevant to the job role and requirements, potentially adjusting difficulty based on performance. Consider asking follow-up style questions from the pool if the last answer was insufficient on a specific point related to an available question.
    5. If the available pool is empty OR if based on the history and remaining questions you determine the interview should logically conclude (e.g., all key areas covered, candidate performance is clear, candidate seems struggling/expert), indicate that the interview should end. The primary end condition check (total planned questions reached) is handled by the main graph, but the LLM can suggest ending early.
    6. Respond ONLY with a valid JSON object.
    7. If you select a question, the JSON must have the key "selected_question_id" with the exact string ID from the "Available Questions in Pool" list.
    8. If you decide to end, the JSON must have the key "action" with the value "end_interview" and optionally a "reason" key.

    JSON Response Format Examples:
    {{ "action": "ask_question", "selected_question_id": "q5_se" }}
    {{ "action": "end_interview", "reason": "Candidate performance is clear." }}

    Ensure your response contains ONLY the JSON object and is valid. Do not add any other text before or after the JSON. Also ensure the each JSON object should contain an "action".
    """

    print(f"Sending prompt ({len(prompt_text)} chars) to LLM...")
    response_content = None
    try:
        llm_response = llm.invoke(prompt_text, {"recursion_limit": 100})
        response_content = llm_response.content
        print(f"LLM Raw Response received.")
    except Exception as e:
        print(f"LLM call failed: {e}")
        return None

    if not response_content:
        print("LLM response was empty.")
        return None

    response_content = response_content.strip()
    if response_content.startswith("```json"):
        response_content = response_content[len("```json"):].strip()
        if response_content.endswith("```"):
            response_content = response_content[:-len("```")].strip()

    llm_decision = None
    try:
        llm_decision = json.loads(response_content)
        print(f"Parsed LLM Decision: {llm_decision}")
    except json.JSONDecodeError:
        print(f"Failed to parse LLM response as JSON: {response_content}")
        return None

    if not isinstance(llm_decision, dict):
        print(f"Parsed LLM response is not a dictionary: {llm_decision}")
        return None

    action = llm_decision.get("action")

    if action == "ask_question":
        selected_id = llm_decision.get("selected_question_id")
        if selected_id:
            selected_question = next((q for q in available_questions if q.get('id') == selected_id), None)
            if selected_question:
                print(f"LLM selected question ID: {selected_id}")
                return selected_question
            else:
                print(f"LLM selected ID '{selected_id}' not found in available pool.")
                return None

        else:
            print("LLM action was 'ask_question' but no 'selected_question_id' provided.")
            return None

    elif action == "end_interview":
        print(f"LLM decided to end interview. Reason: {llm_decision.get('reason', 'N/A')}")
        return {"action": "end_interview", "reason": llm_decision.get('reason')}

    else:
        print(f"LLM returned unknown action: {action}")
        return None


def call_llm_analyze_and_evaluate_response(
        question: Dict[str, Any],
        response: str,
        job_role: str,
        job_info: Optional[JobInformation] = None,
) -> Dict[str, Any] | None:
    print(f"-> LLM: Calling Gemini for combined analysis & evaluation...")

    # Format job information for the prompt
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
            job_info_details.append(f"Job Description: {job_info.job_description[:200]}...")
        job_info_str = "\n".join(job_info_details)

    prompt_text = f"""
    You are an AI interviewer evaluating a candidate's response for a {job_role} role.

    Question Asked: {question.get('text', 'N/A')}
    Candidate Response: {response}
    {f'Job Information:{chr(10)}{job_info_str}' if job_info_str else ''}

    Instructions:
    Analyze the candidate's response thoroughly based on the question asked and the context of a {job_role} role.
    Consider the job requirements (industry, level, employment type, description) in your evaluation.
    Then, evaluate the response quality and assign a score.
    Respond ONLY with a valid JSON object containing both analysis and evaluation details.

    JSON Response Format:
    {{
      "analysis": {{
        "key_points_extracted": [], // List of main ideas/facts mentioned
        "relevance_to_question": "", // How well the response addresses the question ("high" | "medium" | "low" | "partial")
        "clarity_assessment": "", // How easy the response was to understand ("clear" | "somewhat clear" | "unclear")
        "technical_accuracy_assessment": "", // If applicable, assess technical correctness ("accurate" | "mostly accurate" | "some inaccuracies" | "inaccurate" | "not applicable")
        "confidence_level": "", // Based on language used ("high" | "medium" | "low")
        "sentiment": "", // ("positive" | "neutral" | "negative")
        "keywords": [] // Relevant terms mentioned
        // Add other analysis points relevant to job role
      }},
      "evaluation": {{
        "score": null, // Assign a score (int out of 10). Use null if not scorable.
        "overall_evaluation_summary": "", // Concise summary of the evaluation for this response
        "relevance_judgment": "", // ("Relevant" | "Partially Relevant" | "Not Relevant")
        "strengths": [], // Key positive points
        "areas_for_improvement": [] // Key points to improve or points missed
        // Add other evaluation points specific to question/role
      }}
    }}

    Ensure your response contains ONLY the JSON object and is valid. Do not add any other text.
    Fill all keys in the JSON object based on the response. Use null or empty arrays/strings where information is not applicable or found.
    """

    print(f"Sending combined analysis/evaluation prompt ({len(prompt_text)} chars) to LLM...")
    response_content = None

    try:
        llm_response = llm.invoke(prompt_text, {"recursion_limit": 100})
        response_content = llm_response.content
        print("LLM Raw Response for combined analysis/evaluation received.")
    except Exception as e:
        print(f"LLM combined analysis/evaluation call failed: {e}")
        return None

    if not response_content:
        print("LLM combined analysis/evaluation response was empty.")
        return None

    response_content = response_content.strip()
    if response_content.startswith("```json"):
        response_content = response_content[len("```json"):].strip()
        if response_content.endswith("```"):
            response_content = response_content[:-len("```")].strip()

    combined_result = None
    try:
        combined_result = json.loads(response_content)
        print("Parsed LLM Combined Result.")
        if (
                not isinstance(combined_result, dict) or
                "analysis" not in combined_result or
                "evaluation" not in combined_result or
                not isinstance(combined_result.get("evaluation"), dict) or
                "score" not in combined_result["evaluation"]
        ):
            print("Parsed combined result is not a valid structure or missing score.")
            return None

        score = combined_result["evaluation"].get("score")
        if score is not None and not isinstance(score, (int, float)):
            try:
                combined_result["evaluation"]["score"] = float(score)
            except (ValueError, TypeError):
                print(f"Evaluation score is not a valid number: {score}")
                return None


    except json.JSONDecodeError:
        print(f"Failed to parse LLM combined analysis/evaluation response as JSON: {response_content}")
        return None

    return combined_result


def call_llm_generate_feedback(
        question: Dict[str, Any],
        response: str,
        analysis: Dict[str, Any],
        evaluation: Dict[str, Any],
        job_role: str,
        job_info: Optional[JobInformation] = None,
) -> str | None:
    print(f"-> LLM: Calling Gemini for feedback generation...")

    # Format job information for the prompt
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
            job_info_details.append(f"Job Description: {job_info.job_description[:200]}...")
        job_info_str = "\n".join(job_info_details)

    prompt_text = f"""
    You are an AI interviewer providing feedback on a candidate's response for a {job_role} role.
    You have analyzed and evaluated their response.

    Question Asked: {question.get('text', 'N/A')}
    Candidate Response: {response[:200]}... # Provide snippet of raw response for context
    Analysis Results: {json.dumps(analysis, indent=2)[:500]}... # Provide snippet of analysis
    Evaluation Results: {json.dumps(evaluation, indent=2)[:500]}... # Provide snippet of evaluation (includes score, strengths, improvements)
    {f'Job Information:{chr(10)}{job_info_str}' if job_info_str else ''}

    Instructions:
    1. Generate clear, constructive, and encouraging feedback for the candidate regarding their response to the question.
    2. Base the feedback on the provided Analysis and Evaluation results, specifically mentioning strengths and areas for improvement identified in the evaluation.
    3. Include the score for this specific response (from Evaluation Results) in the feedback.
    4. Keep the feedback concise and directly related to the response provided.
    5. Address the candidate directly (e.g., "Your response regarding...").
    6. Consider the job requirements in your feedback - highlight how their response aligns or doesn't align with what's needed for this role.
    7. Avoid conversational filler outside the direct feedback role.

    Provide ONLY the feedback text as a plain string. Do not include JSON or any other formatting unless explicitly part of the feedback content.
    """

    print(f"Sending feedback prompt ({len(prompt_text)} chars) to LLM...")
    response_content = None
    try:
        llm_response = llm.invoke(prompt_text, {"recursion_limit": 100})
        response_content = llm_response.content
        print("LLM Raw Response for feedback received.")
    except Exception as e:
        print(f"LLM feedback generation call failed: {e}")
        return None

    if not response_content:
        print("LLM feedback response was empty.")
        return None

    feedback_text = response_content.strip()

    print(f"Generated feedback (first 50 chars): {feedback_text[:50]}...")

    return feedback_text


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
