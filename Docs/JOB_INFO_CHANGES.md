# Job Information Integration - Changes Summary

## Overview
Agent hiện nay có thể nhận các thông tin công việc chi tiết và sử dụng chúng để sinh ra câu hỏi phỏng vấn phù hợp hơn.

## Job Information Fields
Agent nhận các tham số sau:
- **Industry**: Ngành công nghiệp (e.g., Technology, Finance, Healthcare)
- **Job Level**: Cấp bậc công việc (Junior, Mid-level, Senior, Lead, Manager)
- **Employment Type**: Loại hình công việc (Full-time, Part-time, Contract, Freelance, Internship)
- **Salary Range**: Mức lương (e.g., $100k - $150k)
- **Job Description**: Mô tả công việc chi tiết

## Changes Made

### Backend (agent/)

#### 1. **models.py**
- Thêm class `JobInformation` để định nghĩa các tham số công việc
- Cập nhật `InterviewState` để chứa `job_info` field

```python
class JobInformation(BaseModel):
    industry: Optional[str] = None
    job_level: Optional[str] = None
    employment_type: Optional[str] = None
    salary_range: Optional[str] = None
    job_description: Optional[str] = None
```

#### 2. **api.py**
- Cập nhật `StartInterviewRequest` để nhận `job_info`
- Import `JobInformation` từ models
- Modify `start_interview()` endpoint để pass `job_info` đến `InterviewState`

#### 3. **nodes.py**
- Cập nhật `select_question_node()` để truyền `job_info` tới LLM function
- Cập nhật `process_response_node()` để truyền `job_info` tới LLM function
- Cập nhật `generate_feedback_node()` để truyền `job_info` tới LLM function

#### 4. **llm_helpers.py**
- Thêm import `JobInformation` từ models
- Cập nhật `call_llm_select_question()`:
  - Nhận parameter `job_info`
  - Format job info và include trong prompt
  - LLM xem xét job requirements khi chọn câu hỏi

- Cập nhật `call_llm_analyze_and_evaluate_response()`:
  - Nhận parameter `job_info`
  - Include job info trong prompt
  - LLM xem xét job requirements khi đánh giá responses

- Cập nhật `call_llm_generate_feedback()`:
  - Nhận parameter `job_info`
  - Include job info trong prompt
  - Feedback liên hệ tới job requirements

### Frontend (frontend/src/)

#### 1. **components/StartForm.js**
- Thêm 5 fields mới cho Job Information:
  - Industry (text input)
  - Job Level (dropdown select)
  - Employment Type (dropdown select)
  - Salary Range (text input)
  - Job Description (multiline textarea)
  
- Cập nhật `handleStart()` để collect job info và pass tới API
- Thêm helper text giải thích các fields là optional

#### 2. **api/index.js**
- Cập nhật hàm `startInterview()`:
  - Thêm parameter `jobInfo` (optional, default = {})
  - Pass `job_info` object trong request body

## How It Works

1. **User fills form** → StartForm collects job information
2. **Submit request** → Frontend sends request với job_info parameter
3. **Backend receives** → InterviewState chứa job_info
4. **Question Selection** → LLM chọn câu hỏi dựa trên:
   - Job role
   - Job level (difficulty adjustment)
   - Industry (topic relevance)
   - Job description (specific skills needed)
5. **Response Evaluation** → LLM đánh giá response dựa trên job requirements
6. **Feedback Generation** → Feedback liên hệ tới job requirements

## Example Request

```json
{
  "job_role": "Software Engineer",
  "candidate_id": "candidate-123",
  "job_info": {
    "industry": "Technology",
    "job_level": "Senior",
    "employment_type": "Full-time",
    "salary_range": "$120k - $180k",
    "job_description": "Looking for experienced backend engineer with 5+ years in Python and cloud technologies..."
  }
}
```

## Testing

Để test các thay đổi:

1. **Start backend**: `uvicorn agent.api:api --reload`
2. **Start frontend**: `npm start` (từ folder frontend/)
3. **Fill form** với job information
4. **Observe**: 
   - Câu hỏi sẽ phù hợp hơn với job description
   - Feedback sẽ liên hệ tới job requirements
   - Evaluation sẽ xem xét job level

## Notes

- Job information là **optional** - nếu không cung cấp, agent vẫn hoạt động bình thường
- Tất cả fields đều flexible - có thể extend thêm fields khác
- LLM prompts được cấu trúc để tận dụng tối đa job information
