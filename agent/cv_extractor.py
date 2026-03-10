"""
CV Extraction Utilities
Extract structured information from CV files (PDF, DOCX, TXT)
"""
from typing import Dict, Any, Optional
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file"""
    try:
        import PyPDF2
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file"""
    try:
        from docx import Document
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {e}")
        raise


def extract_text_from_txt(file_path: str) -> str:
    """Extract text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except Exception as e:
        logger.error(f"Error extracting text from TXT: {e}")
        raise


def extract_text_from_file(file_path: str) -> str:
    """
    Extract text from various file formats (PDF, DOCX, TXT)
    
    Args:
        file_path: Path to the CV file
        
    Returns:
        Extracted text content
    """
    file_extension = Path(file_path).suffix.lower()
    
    if file_extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension in ['.docx', '.doc']:
        return extract_text_from_docx(file_path)
    elif file_extension == '.txt':
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")


def extract_cv_information_with_llm(cv_text: str, llm) -> Optional[Dict[str, Any]]:
    """
    Use LLM to extract structured information from CV text
    
    Args:
        cv_text: Raw text extracted from CV
        llm: Language model instance
        
    Returns:
        Dictionary containing extracted CV information
    """
    logger.info("Extracting CV information using LLM...")
    
    prompt = f"""
You are an expert CV/Resume parser. Extract structured information from the following CV text.

CV Text:
{'-' * 80}
{cv_text[:4000]}  # Limit to avoid token overflow
{'-' * 80}

Instructions:
1. Carefully read the CV and extract all relevant information
2. Identify the candidate's name, contact information, skills, work experience, education, certifications, and projects
3. Calculate approximate years of experience based on work history
4. Extract a professional summary if available, or create a brief one based on the CV content
5. Return the information in a structured JSON format

JSON Response Format:
{{
  "candidate_name": "Full name of the candidate",
  "email": "Email address",
  "phone": "Phone number",
  "skills": ["Skill 1", "Skill 2", "Skill 3", ...],
  "work_experience": [
    {{
      "title": "Job title",
      "company": "Company name",
      "duration": "Duration (e.g., 'Jan 2020 - Present')",
      "description": "Brief description of responsibilities and achievements"
    }}
  ],
  "education": [
    {{
      "degree": "Degree name",
      "institution": "University/School name",
      "year": "Graduation year or duration"
    }}
  ],
  "certifications": ["Certification 1", "Certification 2", ...],
  "projects": [
    {{
      "name": "Project name",
      "description": "Project description",
      "technologies": ["Tech 1", "Tech 2", ...]
    }}
  ],
  "summary": "Professional summary or objective statement",
  "years_of_experience": 5
}}

Important:
- Extract all information accurately from the CV
- Use null for fields that are not found in the CV
- Use empty arrays [] for list fields with no data
- Ensure the JSON is valid and properly formatted
- Do not include markdown code blocks or extra text

Provide ONLY the JSON object.
"""
    
    try:
        llm_response = llm.invoke(prompt, {"recursion_limit": 100})
        response_content = llm_response.content.strip()
        
        logger.info("LLM response received for CV extraction")
        
        # Clean markdown formatting if present
        if response_content.startswith("```json"):
            response_content = response_content[7:].strip()
        if response_content.startswith("```"):
            response_content = response_content[3:].strip()
        if response_content.endswith("```"):
            response_content = response_content[:-3].strip()
        
        # Parse JSON
        cv_data = json.loads(response_content)
        
        if not isinstance(cv_data, dict):
            logger.error("Invalid CV extraction result - not a dictionary")
            return None
        
        # Add raw text for reference
        cv_data['raw_text'] = cv_text
        
        logger.info(f"✅ Successfully extracted CV information for: {cv_data.get('candidate_name', 'Unknown')}")
        return cv_data
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        logger.error(f"Response was: {response_content[:200]}...")
        return None
    except Exception as e:
        logger.error(f"Error extracting CV information: {e}")
        return None


def process_cv_file(file_path: str, llm) -> Optional[Dict[str, Any]]:
    """
    Complete pipeline to process CV file and extract information
    
    Args:
        file_path: Path to the CV file
        llm: Language model instance
        
    Returns:
        Dictionary containing extracted CV information
    """
    try:
        # Step 1: Extract text from file
        logger.info(f"Processing CV file: {file_path}")
        cv_text = extract_text_from_file(file_path)
        
        if not cv_text or len(cv_text) < 50:
            logger.error("Extracted text is too short or empty")
            return None
        
        logger.info(f"Extracted {len(cv_text)} characters from CV")
        
        # Step 2: Use LLM to extract structured information
        cv_info = extract_cv_information_with_llm(cv_text, llm)
        
        return cv_info
        
    except Exception as e:
        logger.error(f"Error processing CV file: {e}")
        return None
