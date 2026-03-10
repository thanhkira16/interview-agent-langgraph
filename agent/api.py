from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List, Awaitable
from langgraph.types import Command
from .graph import workflow
from .models import InterviewState, JobInformation, CVInformation
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
import uuid
import logging
import os
import tempfile
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


DATABASE_URL = "./db/checkpoints.db"

api = FastAPI(title="AI agent-backend API")

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    # "https://your-production-frontend.com",
]

api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

runnable_app = None
saver_instance: Optional[AsyncSqliteSaver] = None
saver_context_manager: Optional[Awaitable] = None


interview_sessions: Dict[str, str] = {}


class StartInterviewRequest(BaseModel):
    job_role: str
    candidate_id: str
    job_info: Optional[JobInformation] = None
    num_questions: Optional[int] = 5  # Number of questions to ask in this interview

class InterviewResponse(BaseModel):
    session_id: str # This will now be the generated UUID
    status: str
    current_question: Optional[Dict[str, Any]] = None
    feedback: Optional[str] = None
    overall_score: Optional[float] = None
    error_message: Optional[str] = None
    interview_history_summary: Optional[List[Dict[str, Any]]] = None


class SubmitAnswerRequest(BaseModel):
    candidate_response: str


@api.on_event("startup")
async def startup_event():
    global runnable_app, saver_instance, saver_context_manager
    try:
        # Ensure database directory exists
        import os
        os.makedirs("./db", exist_ok=True)
        
        # TEMPORARY: Use MemorySaver instead of AsyncSqliteSaver to avoid connection issues
        # TODO: Fix AsyncSqliteSaver initialization
        from langgraph.checkpoint.memory import MemorySaver
        saver_instance = MemorySaver()
        
        logger.info("MemorySaver initialized (temporary solution)")
        logger.warning("Using in-memory checkpointing - conversation state will be lost on restart")
        
        # Compile workflow with checkpointer
        runnable_app = workflow.compile(checkpointer=saver_instance)
        logger.info("LangGraph workflow compiled with MemorySaver.")

    except Exception as e:
        logger.error(f"Error during startup: Could not initialize saver or compile graph: {e}", exc_info=True)
        raise e


@api.on_event("shutdown")
async def shutdown_event():
    global saver_context_manager
    if saver_context_manager:
        try:
            await saver_context_manager.__aexit__(None, None, None)
            logger.info("AsyncSqliteSaver context exited.")
        except Exception as e:
            logger.warning(f"Error closing AsyncSqliteSaver: {e}")


@api.post("/interview/start", response_model=InterviewResponse)
async def start_interview(
    job_role: str = Form(...),
    candidate_id: str = Form(...),
    job_info: Optional[str] = Form(None),  # JSON string
    num_questions: Optional[int] = Form(5),
    cv_file: Optional[UploadFile] = File(None)
):
    """
    Start a new interview session with optional CV file upload.
    
    Args:
        job_role: The role being interviewed for
        candidate_id: Unique identifier for the candidate
        job_info: JSON string containing job information (optional)
        num_questions: Number of questions to ask (default: 5)
        cv_file: CV file upload (PDF, DOCX, or TXT) (optional)
    """
    global runnable_app
    if runnable_app is None:
        raise HTTPException(status_code=500,
                            detail="Graph not initialized. Server encountered a startup error.")

    generated_session_id = str(uuid.uuid4())
    interview_sessions[generated_session_id] = candidate_id
    logger.info(f"Generated session ID {generated_session_id} for candidate {candidate_id}")

    # Parse job_info from JSON string if provided
    parsed_job_info = JobInformation()
    if job_info:
        try:
            job_info_dict = json.loads(job_info)
            parsed_job_info = JobInformation(**job_info_dict)
        except Exception as e:
            logger.warning(f"Failed to parse job_info: {e}")

    # Process CV file if provided
    cv_information = None
    if cv_file:
        try:
            logger.info(f"Processing CV file: {cv_file.filename}")
            
            # Save uploaded file temporarily
            file_extension = os.path.splitext(cv_file.filename)[1].lower()
            if file_extension not in ['.pdf', '.docx', '.doc', '.txt']:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file format: {file_extension}. Supported formats: PDF, DOCX, TXT"
                )
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                content = await cv_file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            try:
                # Extract CV information
                from .cv_extractor import process_cv_file
                from .config import llm
                
                cv_data = process_cv_file(temp_file_path, llm)
                
                if cv_data:
                    cv_information = CVInformation(**cv_data)
                    logger.info(f"✅ CV extracted successfully for: {cv_information.candidate_name or 'Unknown'}")
                else:
                    logger.warning("Failed to extract CV information")
                    
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing CV file: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to process CV file: {str(e)}")

    initial_state = InterviewState(
        job_role=job_role,
        candidate_id=generated_session_id,
        job_info=parsed_job_info,
        cv_info=cv_information,  # Include CV information in state
        total_questions_planned=num_questions or 5
    )

    try:
        final_state = await runnable_app.ainvoke(
            initial_state,
            config={"configurable": {"thread_id": generated_session_id}}
        )

        response_data = InterviewResponse(
            session_id=generated_session_id,
            status=final_state.get('interview_status', 'unknown'),
            current_question=final_state.get('current_question'),
            feedback=final_state.get('feedback'),
            overall_score=final_state.get('overall_score'),
            error_message=final_state.get('error_message'),
            interview_history_summary=final_state.get('interview_history_summary')
        )
        logger.info(f"Started interview session {generated_session_id} successfully.")
        return response_data

    except Exception as e:
        logger.error(f"Error starting interview for candidate {candidate_id} (session {generated_session_id}): {e}", exc_info=True)
        return InterviewResponse(
             session_id=generated_session_id,
             status='error',
             error_message=f"An internal error occurred while starting the interview: {e}"
        )


@api.post("/interview/{session_id}/submit_answer", response_model=InterviewResponse)
async def submit_answer(session_id: str, request: SubmitAnswerRequest):
    global runnable_app
    if runnable_app is None:
        raise HTTPException(status_code=500,
                            detail="Graph not initialized. Server encountered a startup error.")


    if session_id not in interview_sessions:
         logger.warning(f"Received submit for unknown session ID: {session_id}")
         raise HTTPException(status_code=404, detail=f"Interview session {session_id} not found or has expired.")

    logger.info(f"Received submit for session ID: {session_id}")


    try:

        final_state = await runnable_app.ainvoke(
            Command(resume=request.candidate_response),
            config={"configurable": {"thread_id": session_id}} # Use the UUID from the path
        )

        response_data = InterviewResponse(
            session_id=session_id,
            status=final_state.get('interview_status', 'unknown'),
            current_question=final_state.get('current_question'),
            feedback=final_state.get('feedback'),
            overall_score=final_state.get('overall_score'),
            error_message=final_state.get('error_message'),
            interview_history_summary=final_state.get('interview_history_summary')
        )
        logger.info(f"Processed answer for session {session_id}, status: {response_data.status}")
        return response_data

    except Exception as e:
        logger.error(f"Error submitting answer for session {session_id}: {e}", exc_info=True)
        return InterviewResponse(
             session_id=session_id,
             status='error',
             error_message=f"An error occurred while processing the answer: {e}"
        )


# uvicorn agent.api:api --reload