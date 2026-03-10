# Prompt để tạo Graph Workflow Visualization

## Yêu cầu tổng quan
Tạo một biểu đồ workflow visualization chi tiết cho hệ thống AI Interview Agent sử dụng LangGraph, bao gồm main agent workflow và các CV verification sub-agents.

---

## 1. MAIN INTERVIEW WORKFLOW (Primary Agent)

### Các Node chính:

1. **start_interview** (Entry Point)
   - Khởi tạo interview session
   - Thiết lập state ban đầu
   - Input: candidate_id, job_role, job_info, cv_info
   - Output: interview_status = "in_progress"

2. **generate_question** 
   - Sử dụng LLM để generate câu hỏi động
   - Dựa trên: interview_history, job_role, job_info, cv_info, cv_verification
   - Ưu tiên verify các CV claims chưa được xác minh
   - Output: current_question

3. **ask_question**
   - Hiển thị câu hỏi cho candidate
   - Output: Question text

4. **receive_response**
   - Sử dụng interrupt() để nhận response từ candidate
   - Output: candidate_response

5. **process_response**
   - Phân tích và đánh giá response bằng LLM
   - Output: response_analysis, response_evaluation (score)

6. **cv_verification** (Sub-workflow - xem phần 2)
   - Verify CV claims dựa trên response
   - Gọi các CV verification sub-agents
   - Output: cv_verification (updated)

7. **generate_feedback**
   - Tạo feedback cho candidate
   - Output: feedback text

8. **provide_feedback**
   - Hiển thị feedback cho candidate

9. **update_state**
   - Cập nhật interview_history
   - Tăng questions_asked_count
   - Tính overall_score
   - Kiểm tra điều kiện kết thúc

10. **finalize_cv_verification**
    - Verify years_of_experience
    - Aggregate tất cả CV verification results
    - Output: overall_verification_score, overall_credibility

11. **generate_final_report** (Exit Point)
    - Tạo báo cáo tổng hợp cuối cùng
    - Bao gồm: executive_summary, strengths, weaknesses, recommendation
    - Output: final_report → END

### Conditional Edges:

**decide_next_after_select:**
- Nếu interview_status = "completed" hoặc "terminated" → generate_final_report
- Nếu có current_question → ask_question
- Ngược lại → generate_final_report

**decide_next_after_update:**
- Nếu interview_status = "completed" hoặc "terminated" → finalize_cv_verification
- Nếu questions_asked_count < total_questions_planned → generate_question
- Ngược lại → finalize_cv_verification

### Flow chính:
```
START → start_interview → generate_question → [decide_next_after_select]
                                                    ↓
                                              ask_question
                                                    ↓
                                            receive_response
                                                    ↓
                                            process_response
                                                    ↓
                                            cv_verification (Sub-workflow)
                                                    ↓
                                            generate_feedback
                                                    ↓
                                            provide_feedback
                                                    ↓
                                              update_state
                                                    ↓
                                          [decide_next_after_update]
                                                    ↓
                                    (loop back to generate_question OR)
                                                    ↓
                                        finalize_cv_verification
                                                    ↓
                                          generate_final_report
                                                    ↓
                                                   END
```


---

## 2. CV VERIFICATION SUB-AGENTS WORKFLOW

### Trigger: 
Được gọi sau **process_response_node** trong mỗi interview cycle

### Input:
- current_question (Dict với text, topic, cv_verification_target)
- candidate_response (str)
- cv_info (CVInformation object)
- cv_verification (CVVerificationResults - current state)

### Matching Logic:
Trước khi gọi sub-agents, `cv_verification_node` thực hiện matching:
1. **Skill matching**: Check nếu skill_name xuất hiện trong question_text hoặc question_topic
2. **Work Experience matching**: Check nếu position_title hoặc company xuất hiện trong question
3. **Education matching**: Check nếu degree hoặc institution xuất hiện trong question
4. **Certification matching**: Check nếu certification_name xuất hiện trong question
5. **Project matching**: Check nếu project_name hoặc technologies xuất hiện trong question

---

### Sub-Agents Chi Tiết:

#### 2.1. **Skill Verification Sub-Agent** (`verify_skill_with_llm`)

**Mục đích**: Verify kỹ năng kỹ thuật thông qua phân tích độ sâu kiến thức và khả năng ứng dụng thực tế.

**Input Parameters**:
- `skill_name`: str - Tên skill cần verify (e.g., "Python", "React", "AWS")
- `candidate_answer`: str - Câu trả lời của candidate
- `question_asked`: str - Câu hỏi đã hỏi
- `job_role`: str - Vị trí đang phỏng vấn
- `llm`: LLM instance

**LLM Prompt Analysis Criteria**:
```
1. Technical accuracy (độ chính xác kỹ thuật)
2. Depth of understanding (surface-level vs deep knowledge)
3. Practical application ability (khả năng ứng dụng thực tế)
4. Confidence and clarity (sự tự tin và rõ ràng)
5. Use of correct terminology (sử dụng thuật ngữ đúng)
6. Real-world experience indicators (dấu hiệu kinh nghiệm thực tế)
```

**Output Structure** (`SkillVerificationResult`):
```python
{
    "skill_name": str,
    "claimed_proficiency": "Expert | Intermediate | Beginner | Unknown",
    "verification_status": "verified | partially_verified | unverified | inconsistent",
    "verification_score": float (0-10),
    "questions_asked": List[str],
    "answers_summary": List[str],  # Truncated to 200 chars each
    "evidence_for": List[str],      # Points supporting the claim
    "evidence_against": List[str],  # Points contradicting the claim
    "recommendation": str,
    "notes": str
}
```

**Scoring Logic**:
- **8-10**: Verified - Strong evidence, deep understanding, practical experience
- **6-7**: Partially verified - Some evidence, decent understanding
- **4-5**: Unverified - Weak evidence, surface-level knowledge
- **0-3**: Inconsistent - Red flags, contradictions, lack of knowledge

**Incremental Update**: Nếu skill đã được verify trước đó:
- Append new question và answer
- **Average** verification_score với score mới
- Extend evidence_for và evidence_against lists

---

#### 2.2. **Work Experience Verification Sub-Agent** (`verify_work_experience_with_llm`)

**Mục đích**: Verify kinh nghiệm làm việc thông qua đánh giá độ sâu kỹ thuật, hiểu biết về trách nhiệm, và phát hiện red flags.

**Input Parameters**:
- `experience`: Dict với {title, company, duration, description/responsibilities}
- `candidate_answer`: str
- `question_asked`: str
- `job_role`: str
- `llm`: LLM instance

**LLM Prompt Analysis Criteria**:
```
1. Depth of knowledge về role và responsibilities
2. Specific examples và details (vs vague descriptions)
3. Technical competence trong claimed areas
4. Understanding of business context
5. Problem-solving approach
6. Red flags detection:
   - Inconsistencies (mâu thuẫn)
   - Lack of detail (thiếu chi tiết)
   - Generic answers (câu trả lời chung chung)
   - Inability to explain decisions (không giải thích được quyết định)
```

**Output Structure** (`WorkExperienceVerificationResult`):
```python
{
    "position_title": str,
    "company": str,
    "duration_claimed": str,
    "verification_status": "verified | partially_verified | unverified | inconsistent",
    "verification_score": float (0-10),
    "technical_depth_score": float (0-10),
    "responsibilities_verified": List[str],
    "responsibilities_unverified": List[str],
    "questions_asked": List[str],
    "answers_summary": List[str],
    "red_flags": List[str],
    "strengths": List[str],
    "recommendation": str,
    "notes": str
}
```

**Dual Scoring System**:
1. **verification_score**: Overall credibility của experience claim
2. **technical_depth_score**: Độ sâu kỹ thuật trong role

**Red Flags Examples**:
- "Vague about specific contributions"
- "Cannot explain technical decisions"
- "Inconsistent timeline"
- "Generic answers without specifics"

**Strengths Examples**:
- "Clear understanding of architecture"
- "Detailed problem-solving examples"
- "Strong technical depth"

---

#### 2.3. **Education Verification Sub-Agent** (`verify_education_with_llm`)

**Mục đích**: Verify học vấn thông qua đánh giá kiến thức nền tảng và khả năng áp dụng lý thuyết.

**Input Parameters**:
- `education`: Dict với {degree, institution, year, field}
- `candidate_answer`: str
- `question_asked`: str
- `job_role`: str
- `llm`: LLM instance

**LLM Prompt Analysis Criteria**:
```
1. Understanding of core concepts (hiểu khái niệm cốt lõi)
2. Ability to apply theoretical knowledge (áp dụng lý thuyết)
3. Depth vs breadth of knowledge (sâu vs rộng)
4. Critical thinking and problem-solving approach
5. Gaps in expected knowledge (thiếu hụt kiến thức)
```

**Output Structure** (`EducationVerificationResult`):
```python
{
    "degree": str,
    "institution": str,
    "year": str,
    "verification_status": "verified | partially_verified | unverified | inconsistent",
    "verification_score": float (0-10),
    "knowledge_depth_score": float (0-10),
    "questions_asked": List[str],
    "answers_summary": List[str],
    "topics_verified": List[str],    # Topics they demonstrated knowledge in
    "topics_weak": List[str],         # Topics they struggled with
    "recommendation": str,
    "notes": str
}
```

**Focus Areas by Degree**:
- **Computer Science**: Algorithms, Data Structures, OOP, Databases
- **Software Engineering**: SDLC, Design Patterns, Testing
- **Information Technology**: Networks, Systems, Security

---

#### 2.4. **Certification Verification Sub-Agent** (`verify_certification_with_llm`)

**Mục đích**: Verify chứng chỉ thông qua đánh giá kiến thức thực hành và hiểu biết sâu (không chỉ học thuộc).

**Input Parameters**:
- `certification_name`: str (e.g., "AWS Solutions Architect", "PMP")
- `candidate_answer`: str
- `question_asked`: str
- `job_role`: str
- `llm`: LLM instance

**LLM Prompt Analysis Criteria**:
```
1. Practical application of certified concepts
2. Understanding of certification-specific terminology
3. Real-world use cases
4. Depth beyond memorization (hiểu sâu, không chỉ thuộc)
5. Currency of knowledge (kiến thức còn cập nhật không?)
```

**Output Structure** (`CertificationVerificationResult`):
```python
{
    "certification_name": str,
    "verification_status": "verified | partially_verified | unverified | inconsistent",
    "verification_score": float (0-10),
    "practical_knowledge_score": float (0-10),
    "questions_asked": List[str],
    "answers_summary": List[str],
    "concepts_verified": List[str],
    "concepts_weak": List[str],
    "recommendation": str,
    "notes": str
}
```

**Practical vs Theoretical**:
- **Practical knowledge score cao**: Candidate có thể áp dụng, giải thích use cases
- **Practical knowledge score thấp**: Chỉ biết lý thuyết, không biết áp dụng

---

#### 2.5. **Project Verification Sub-Agent** (`verify_project_with_llm`)

**Mục đích**: Verify dự án thông qua đánh giá vai trò cụ thể, độ sâu kỹ thuật, và phát hiện "project padding".

**Input Parameters**:
- `project`: Dict với {name, description, technologies, role}
- `candidate_answer`: str
- `question_asked`: str
- `job_role`: str
- `llm`: LLM instance

**LLM Prompt Analysis Criteria**:
```
1. Clarity về specific role và contributions
2. Technical depth trong claimed technologies
3. Understanding of project architecture và design decisions
4. Challenges faced và how they were solved
5. Red flags detection:
   - Vague answers về role
   - Lack of detail về implementation
   - Inconsistencies về technologies
   - Cannot explain architecture decisions
6. Evidence of hands-on work vs theoretical knowledge
```

**Output Structure** (`ProjectVerificationResult`):
```python
{
    "project_name": str,
    "technologies_claimed": List[str],
    "verification_status": "verified | partially_verified | unverified | inconsistent",
    "verification_score": float (0-10),
    "role_clarity_score": float (0-10),      # Rõ ràng về vai trò
    "technical_depth_score": float (0-10),   # Độ sâu kỹ thuật
    "questions_asked": List[str],
    "answers_summary": List[str],
    "technologies_verified": List[str],
    "technologies_weak": List[str],
    "challenges_discussed": List[str],
    "red_flags": List[str],
    "strengths": List[str],
    "recommendation": str,
    "notes": str
}
```

**Triple Scoring System**:
1. **verification_score**: Overall credibility
2. **role_clarity_score**: Rõ ràng về vai trò (0-10)
3. **technical_depth_score**: Độ sâu kỹ thuật (0-10)

**Red Flags for Projects**:
- "Cannot explain their specific contribution"
- "Vague about technical implementation"
- "Claims all technologies but shallow knowledge"
- "No challenges discussed (too perfect)"

---

#### 2.6. **Years of Experience Verification Sub-Agent** (`verify_years_of_experience_with_llm`)

**Mục đích**: Verify số năm kinh nghiệm thông qua đánh giá tổng thể maturity level từ toàn bộ interview.

**Trigger**: Chỉ chạy ở **finalize_cv_verification_node** (cuối interview)

**Input Parameters**:
- `claimed_years`: int
- `interview_history`: List[Dict] - Toàn bộ Q&A trong interview
- `job_role`: str
- `llm`: LLM instance

**LLM Prompt Analysis Criteria**:
```
1. Maturity indicators:
   - Problem-solving approach (junior vs senior)
   - Best practices awareness
   - Architectural thinking
   - Trade-off analysis ability
2. Depth of knowledge (surface vs deep)
3. Breadth of experience (exposure to different aspects)
4. Communication and articulation
5. Gaps unusual for claimed experience
6. Signs of inflated or deflated claims
```

**Input Processing**:
- Summarize last 10 Q&A pairs
- Include scores from evaluations
- Format: "Q1: ...", "A1: ...", "Score: X/10"

**Output Structure** (`YearsOfExperienceVerificationResult`):
```python
{
    "claimed_years": int,
    "verification_status": "verified | partially_verified | unverified | inconsistent",
    "estimated_actual_years": int,
    "verification_score": float (0-10),
    "questions_asked": List[str],  # All questions from interview
    "answers_summary": List[str],  # All answers (truncated)
    "maturity_indicators": List[str],
    "gaps_identified": List[str],
    "recommendation": str,
    "notes": str
}
```

**Maturity Indicators Examples**:
- **Junior (0-2 years)**: Basic syntax, follows tutorials, needs guidance
- **Mid (3-5 years)**: Independent work, design patterns, best practices
- **Senior (5+ years)**: Architecture decisions, mentoring, trade-offs

**Gaps Examples**:
- "Lacks architectural thinking expected for 5+ years"
- "No exposure to production issues"
- "Cannot discuss scalability considerations"

---

### CV Verification Flow (Chi tiết):

```
process_response_node
        ↓
cv_verification_node
        ↓
[1. Initialize or get existing cv_verification]
        ↓
[2. Extract question_text, question_topic, response]
        ↓
[3. Matching Phase - Check CV claims against question]
        ↓
    ┌─────────────────────────────────────────────────┐
    │  For each CV section (skills, exp, edu, etc.)   │
    │  Check if question targets that section         │
    └─────────────────────────────────────────────────┘
        ↓
[4. Call appropriate sub-agent(s)]
        ↓
    ┌───┴───┬───────┬────────┬──────────┬─────────┐
    ↓       ↓       ↓        ↓          ↓         ↓
 Skill   Work    Edu    Cert    Project  (Years - later)
  Sub    Exp                    Sub
 Agent   Sub                   Agent
         Agent
    │       │       │        │          │
    │ LLM   │ LLM   │ LLM    │ LLM      │ LLM
    │ Call  │ Call  │ Call   │ Call     │ Call
    ↓       ↓       ↓        ↓          ↓
[5. Receive verification results (JSON)]
        ↓
[6. Update or merge with existing verification]
        ↓
    ┌─────────────────────────────────────┐
    │ If item already verified:           │
    │  - Append new Q&A                   │
    │  - Average scores                   │
    │  - Extend evidence lists            │
    │ Else:                               │
    │  - Add new verification result      │
    └─────────────────────────────────────┘
        ↓
[7. Increment total_questions_asked]
        ↓
Return {"cv_verification": updated_cv_verification}
```

---

### Aggregation Phase (Cuối Interview):

```
finalize_cv_verification_node
        ↓
[1. Check if cv_info and cv_verification exist]
        ↓
[2. Call verify_years_of_experience_with_llm]
        │
        │ Input: claimed_years, interview_history, job_role
        │ Output: YearsOfExperienceVerificationResult
        ↓
[3. Add years_experience_verification to cv_verification]
        ↓
[4. Call aggregate_cv_verification_results]
        ↓
    ┌─────────────────────────────────────────────┐
    │ Aggregation Logic:                          │
    │                                             │
    │ A. Collect all verification scores:         │
    │    - Skills: verification_score             │
    │    - Work Exp: verification_score           │
    │    - Education: verification_score          │
    │    - Certifications: verification_score     │
    │    - Projects: verification_score           │
    │    - Years Exp: verification_score          │
    │                                             │
    │ B. Calculate overall_verification_score:    │
    │    = Average of all scores                  │
    │                                             │
    │ C. Determine overall_credibility:           │
    │    - >= 8: "verified"                       │
    │    - >= 6: "partially_verified"             │
    │    - >= 4: "unverified"                     │
    │    - < 4:  "inconsistent"                   │
    │                                             │
    │ D. Collect red_flags and strengths:         │
    │    - From work_experience_verification      │
    │    - From projects_verification             │
    │    - Deduplicate and take top 10            │
    │                                             │
    │ E. Count verified vs unverified:            │
    │    - verified: score >= 6                   │
    │    - unverified: score < 6                  │
    └─────────────────────────────────────────────┘
        ↓
[5. Update cv_verification with aggregated results]
        ↓
[6. Log summary]
        ↓
Return {"cv_verification": final_cv_verification}
```

---

### Verification Status Definitions:

| Status | Score Range | Meaning |
|--------|-------------|---------|
| **verified** | 8-10 | Strong evidence supporting CV claim, deep knowledge demonstrated |
| **partially_verified** | 6-7 | Some evidence, decent understanding, minor gaps |
| **unverified** | 4-5 | Weak evidence, surface-level knowledge, significant gaps |
| **inconsistent** | 0-3 | Red flags, contradictions, lack of expected knowledge |
| **not_verified** | N/A | Not yet assessed or verification failed |

---

### Error Handling:

Mỗi sub-agent có try-except block:
```python
try:
    # LLM call và JSON parsing
    result = parse_llm_response(llm_response)
    return VerificationResult(**result)
except Exception as e:
    logger.error(f"Error verifying {item}: {e}")
    return VerificationResult(
        verification_status='not_verified',
        notes=f"Verification failed: {str(e)}"
    )
```

---

### JSON Response Cleaning:

Tất cả sub-agents đều clean LLM response:
```python
# Remove markdown code blocks
if response_content.startswith("```json"):
    response_content = response_content[7:].strip()
if response_content.startswith("```"):
    response_content = response_content[3:].strip()
if response_content.endswith("```"):
    response_content = response_content[:-3:].strip()

result_data = json.loads(response_content)
```

---

## 3. STATE MANAGEMENT

### InterviewState (TypedDict):
```python
{
    # Basic Info
    "candidate_id": str,
    "job_role": str,
    "job_info": JobInfo,
    "cv_info": CVInfo,
    
    # Interview Progress
    "interview_status": str,  # "in_progress" | "completed" | "terminated"
    "questions_asked_count": int,
    "total_questions_planned": int,
    
    # Current Cycle
    "current_question": Dict,
    "candidate_response": str,
    "response_analysis": Dict,
    "response_evaluation": Dict,
    "feedback": str,
    
    # History & Scores
    "interview_history": List[Dict],
    "overall_score": float,
    
    # CV Verification
    "cv_verification": CVVerificationResults,
    
    # Error Handling
    "error_message": Optional[str]
}
```

---

## 4. YÊU CẦU VẼ BIỂU ĐỒ

### Loại biểu đồ đề xuất:
1. **Flowchart tổng quan** - Hiển thị main workflow với các nodes và edges
2. **Swimlane diagram** - Phân chia rõ Main Agent vs Sub-Agents
3. **Sequence diagram** - Hiển thị luồng thực thi theo thời gian
4. **Component diagram** - Hiển thị mối quan hệ giữa các components

### Công cụ có thể dùng:
- Mermaid.js (cho markdown)
- Draw.io / Lucidchart
- PlantUML
- Graphviz

### Màu sắc đề xuất:
- **Main workflow nodes**: Blue (#4A90E2)
- **CV verification nodes**: Orange (#F5A623)
- **Sub-agents**: Green (#7ED321)
- **Decision points**: Yellow (#F8E71C)
- **Start/End**: Gray (#9B9B9B)
- **Error paths**: Red (#D0021B)

### Chú thích cần có:
- Input/Output của mỗi node
- Điều kiện của conditional edges
- Loại LLM call (generate_question, analyze_response, verify_skill, etc.)
- State updates quan trọng

---

## 5. EXAMPLE MERMAID CODE (Tham khảo)

```mermaid
graph TD
    Start([START]) --> StartInterview[start_interview<br/>Init state]
    StartInterview --> GenerateQuestion[generate_question<br/>LLM: Generate Question]
    
    GenerateQuestion --> DecideSelect{decide_next_after_select}
    DecideSelect -->|Has Question| AskQuestion[ask_question<br/>Display Question]
    DecideSelect -->|Completed/Terminated| FinalReport[generate_final_report]
    
    AskQuestion --> ReceiveResponse[receive_response<br/>interrupt()]
    ReceiveResponse --> ProcessResponse[process_response<br/>LLM: Analyze & Evaluate]
    
    ProcessResponse --> CVVerification[cv_verification<br/>Sub-workflow]
    CVVerification --> GenerateFeedback[generate_feedback<br/>LLM: Generate Feedback]
    
    GenerateFeedback --> ProvideFeedback[provide_feedback<br/>Display Feedback]
    ProvideFeedback --> UpdateState[update_state<br/>Update History & Score]
    
    UpdateState --> DecideUpdate{decide_next_after_update}
    DecideUpdate -->|Continue| GenerateQuestion
    DecideUpdate -->|Done| FinalizeCVVerif[finalize_cv_verification<br/>Aggregate Results]
    
    FinalizeCVVerif --> FinalReport
    FinalReport --> End([END])
    
    style Start fill:#9B9B9B
    style End fill:#9B9B9B
    style GenerateQuestion fill:#4A90E2
    style CVVerification fill:#F5A623
    style DecideSelect fill:#F8E71C
    style DecideUpdate fill:#F8E71C
```

---

## 6. THÔNG TIN BỔ SUNG

### LLM Calls trong hệ thống:
1. `call_llm_generate_question()` - Tạo câu hỏi động
2. `call_llm_analyze_and_evaluate_response()` - Phân tích và đánh giá
3. `call_llm_generate_feedback()` - Tạo feedback
4. `call_llm_generate_final_report()` - Tạo báo cáo cuối
5. `verify_skill_with_llm()` - Verify skill
6. `verify_work_experience_with_llm()` - Verify work exp
7. `verify_education_with_llm()` - Verify education
8. `verify_certification_with_llm()` - Verify certification
9. `verify_project_with_llm()` - Verify project
10. `verify_years_of_experience_with_llm()` - Verify years exp
11. `aggregate_cv_verification_results()` - Aggregate CV results

### Key Features:
- ✅ Dynamic question generation (không dùng database)
- ✅ CV-aware interviewing (sử dụng CV info để tạo câu hỏi)
- ✅ Real-time CV verification (verify trong quá trình interview)
- ✅ Multi-dimensional scoring (skill, experience, education, etc.)
- ✅ Adaptive questioning (ưu tiên verify unverified claims)
- ✅ Comprehensive final report (bao gồm CV verification results)

---

## 7. OUTPUT MẪU

Vui lòng tạo:

1. **Main Workflow Diagram** - Hiển thị toàn bộ interview flow
2. **CV Verification Sub-workflow Diagram** - Chi tiết các sub-agents
3. **State Transition Diagram** - Hiển thị các trạng thái interview_status
4. **Data Flow Diagram** - Hiển thị luồng dữ liệu qua các nodes
5. **Component Interaction Diagram** - Mối quan hệ giữa nodes, sub-agents, và LLM

Mỗi diagram nên có:
- Tiêu đề rõ ràng
- Legend giải thích màu sắc và ký hiệu
- Annotations cho các điểm quan trọng
- Version và date

---

**Lưu ý**: Hệ thống này sử dụng LangGraph framework với TypedDict state management, interrupt() cho human-in-the-loop, và conditional edges cho dynamic routing.
