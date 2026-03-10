# CV Verification Sub-Agent System

## Overview

This system implements intelligent CV verification through specialized sub-agents that analyze candidate responses during the interview to verify claims made in their CV.

## Architecture

### Sub-Agents

The system consists of 6 specialized verification sub-agents:

1. **Skills Verification Agent**
   - Verifies claimed technical skills
   - Assesses proficiency level (Expert/Intermediate/Beginner)
   - Scores: 0-10 scale
   - Tracks: Evidence for/against, recommendations

2. **Work Experience Verification Agent**
   - Verifies job roles and responsibilities
   - Assesses technical depth of claimed experience
   - Identifies red flags and strengths
   - Scores: Overall verification + technical depth

3. **Education Verification Agent**
   - Verifies fundamental knowledge from claimed degrees
   - Assesses knowledge depth
   - Tracks verified/weak topics
   - Scores: Overall verification + knowledge depth

4. **Certification Verification Agent**
   - Verifies practical application of certified knowledge
   - Assesses beyond memorization
   - Tracks verified/weak concepts
   - Scores: Overall verification + practical knowledge

5. **Project Verification Agent**
   - Verifies actual involvement in claimed projects
   - Assesses role clarity and technical depth
   - Identifies challenges and solutions discussed
   - Scores: Overall + role clarity + technical depth

6. **Years of Experience Verification Agent**
   - Verifies claimed years of experience
   - Estimates actual experience level
   - Identifies maturity indicators and gaps
   - Runs at interview end for holistic assessment

## Workflow

### 1. CV Upload & Extraction
```
User uploads CV → Extract text → LLM parses structured data → CVInformation model
```

### 2. Interview Process
```
For each question-answer cycle:
  1. Generate question (optionally targeting unverified CV claims)
  2. Candidate responds
  3. CV Verification Node analyzes response
  4. Updates verification scores for relevant CV sections
  5. Next question targets low-scoring or unverified claims
```

### 3. Finalization
```
End of interview:
  1. Verify years of experience (holistic)
  2. Aggregate all verification results
  3. Calculate overall credibility score
  4. Generate recommendations
```

## Verification Status

Each CV claim can have one of these statuses:
- `not_verified` - Not yet assessed
- `verified` - Claim confirmed (score >= 8)
- `partially_verified` - Some evidence (score 6-7.9)
- `unverified` - Insufficient evidence (score 4-5.9)
- `inconsistent` - Contradictory evidence (score < 4)

## Scoring System

### Individual Scores (0-10 scale)
- **10-9**: Exceptional - Far exceeds claimed level
- **8-7**: Verified - Matches claimed level
- **6-5**: Partially Verified - Some gaps but acceptable
- **4-3**: Unverified - Significant gaps
- **2-0**: Inconsistent - Major red flags

### Overall CV Credibility
```
Overall Score = Average of all verification scores
Credibility = verified | partially_verified | unverified | inconsistent
```

## Integration Points

### 1. Models (`agent/models.py`)
- `CVInformation` - Extracted CV data
- `CVVerificationResults` - Aggregated verification results
- Individual verification result models for each sub-agent
- `InterviewState` includes `cv_verification` field

### 2. CV Extraction (`agent/cv_extractor.py`)
- Supports PDF, DOCX, TXT formats
- Uses LLM to parse structured information
- Extracts: skills, experience, education, certifications, projects

### 3. Verification Agents (`agent/cv_verification_agents.py`)
- 6 specialized sub-agents
- Each uses LLM for intelligent analysis
- Returns structured verification results

### 4. Verification Node (`agent/cv_verification_node.py`)
- `cv_verification_node()` - Updates verification after each response
- `finalize_cv_verification_node()` - Final aggregation
- Intelligent matching of questions to CV claims

### 5. Question Generation (`agent/llm_helpers.py`)
- `call_llm_generate_question()` enhanced with CV verification
- Targets unverified claims
- Probes red flags
- Adaptive difficulty based on verification scores

### 6. Interview Flow (`agent/nodes.py`)
- `select_question_node()` passes CV verification to question generator
- Prints verification status during interview

### 7. API (`agent/api.py`)
- `/interview/start` accepts CV file upload (multipart/form-data)
- Processes CV before starting interview
- Returns verification results in final report

## Usage Example

### API Request
```bash
curl -X POST "http://localhost:8000/interview/start" \
  -F "job_role=Senior Software Engineer" \
  -F "candidate_id=candidate_123" \
  -F "num_questions=10" \
  -F "cv_file=@resume.pdf" \
  -F 'job_info={"industry":"Technology","job_level":"Senior"}'
```

### Response Flow
```json
{
  "session_id": "uuid-here",
  "status": "in_progress",
  "current_question": {
    "text": "I see you have 5 years of React experience. Can you explain...",
    "topic": "React",
    "cv_verification_target": "React skill"
  }
}
```

## Verification Results Structure

```python
CVVerificationResults(
    overall_verification_score=7.5,  # 0-10
    overall_credibility='partially_verified',
    
    skills_verification=[
        SkillVerificationResult(
            skill_name='React',
            verification_score=8.5,
            verification_status='verified',
            evidence_for=['Deep understanding of hooks', 'Explained context API well'],
            evidence_against=[],
            recommendation='Strong React knowledge confirmed'
        ),
        # ... more skills
    ],
    
    work_experience_verification=[...],
    education_verification=[...],
    certifications_verification=[...],
    projects_verification=[...],
    years_experience_verification=YearsOfExperienceVerificationResult(...),
    
    major_red_flags=['Vague about project role', 'Inconsistent timeline'],
    key_strengths=['Strong problem-solving', 'Good architectural thinking'],
    areas_of_concern=['Limited system design experience'],
    
    hiring_recommendation_impact='Positive - CV claims largely verified',
    suggested_focus_areas=['System design', 'Leadership experience']
)
```

## Benefits

1. **Objective CV Assessment** - Data-driven verification vs subjective judgment
2. **Adaptive Interviewing** - Questions target unverified claims
3. **Red Flag Detection** - Identifies inconsistencies automatically
4. **Comprehensive Reports** - Detailed verification for each CV section
5. **Hiring Confidence** - Know which claims are verified vs unverified
6. **Fair Evaluation** - Systematic approach reduces bias

## Configuration

### Verification Thresholds
Edit in `agent/cv_verification_agents.py`:
```python
# Adjust scoring thresholds
if overall_score >= 8:
    overall_credibility = 'verified'
elif overall_score >= 6:
    overall_credibility = 'partially_verified'
# ... etc
```

### Question Targeting
Edit in `agent/llm_helpers.py`:
```python
# Adjust priority for unverified claims
if cv_verification:
    unverified_skills = [
        s for s in cv_verification.skills_verification 
        if s.verification_score < 6  # Adjust threshold
    ]
```

## Future Enhancements

1. **Multi-round Verification** - Ask follow-up questions for low scores
2. **Confidence Intervals** - Statistical confidence in verification
3. **Comparative Analysis** - Compare against industry benchmarks
4. **Visual Reports** - Charts showing verification scores
5. **Historical Tracking** - Track verification accuracy over time
6. **Custom Rubrics** - Company-specific verification criteria

## Troubleshooting

### CV Extraction Fails
- Check file format (PDF, DOCX, TXT only)
- Ensure file is not corrupted
- Check LLM token limits for very long CVs

### Low Verification Scores
- May indicate insufficient questions asked
- Consider increasing `num_questions` parameter
- Review question quality and relevance

### No Verification Data
- Ensure CV file was uploaded
- Check that `cv_info` is in InterviewState
- Verify CV verification node is in graph

## Dependencies

```
PyPDF2~=3.0.1          # PDF extraction
python-docx~=1.1.0     # DOCX extraction
python-multipart~=0.0.6 # File upload handling
```

Install with:
```bash
pip install -r requirements.txt
```
