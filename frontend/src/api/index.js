const API_BASE = 'http://localhost:8000'; // Adjust for prod

export const startInterview = async (jobRole, candidateId, jobInfo = {}, numQuestions = 5) => {
  const response = await fetch(`${API_BASE}/interview/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      job_role: jobRole,
      candidate_id: candidateId,
      job_info: jobInfo,
      num_questions: numQuestions
    })
  });
  return response.json();
};

export const submitAnswer = async (sessionId, candidateResponse) => {
  const response = await fetch(`${API_BASE}/interview/${sessionId}/submit_answer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ candidate_response: candidateResponse })
  });
  return response.json();
};