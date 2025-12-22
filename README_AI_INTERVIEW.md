# AI-Powered Interview System - Dynamic Question Generation

## 🎯 Overview
System này sử dụng AI (Google Gemini) để tự động tạo câu hỏi phỏng vấn động dựa trên context và câu trả lời trước đó.

## ✨ Features Mới

### 1. **Dynamic Question Generation**
- ❌ **KHÔNG còn** sử dụng database câu hỏi cố định
- ✅ AI tự động **tạo câu hỏi mới** cho từng phỏng vấn
- 🎯 Câu hỏi dựa trên:
  - Job role & requirements
  - Industry, level, employment type
  - Job description
  - Câu trả lời trước đó của ứng viên
  - Performance của ứng viên

### 2. **Customizable Interview Length**
- Người dùng chọn số câu hỏi: **3, 5, 10, hoặc 20**
- Default: 5 câu hỏi

### 3. **Adaptive Questioning**
- **Câu hỏi đầu tiên**: Warm-up, đánh giá kiến thức cơ bản
- **Câu hỏi tiếp theo**:
  - Khám phá sâu topics ứng viên đề cập
  - Tăng độ khó nếu ứng viên trả lời tốt
  - Điều chỉnh độ khó nếu ứng viên gặp khó khăn
  - Follow-up dựa trên gaps trong câu trả lời

### 4. **Comprehensive Final Report**
Sau khi hoàn thành tất cả câu hỏi, AI tự động tạo báo cáo tổng kết bao gồm:
- ✅ Executive Summary
- ✅ Strengths (3-5 điểm mạnh)
- ✅ Areas for Improvement (3-5 điểm yếu)
- ✅ Technical Assessment
- ✅ Overall Recommendation
  - Hiring recommendation (Strongly Recommend / Recommend / Maybe / Not Recommend)
  - Score: X/Y (average: Z/10)
- ✅ Additional Notes

## 🚀 How It Works

### Flow:
```
1. User fills Start Form
   ↓
2. AI generates Question #1 (warm-up)
   ↓
3. User answers
   ↓
4. AI analyzes answer & scores
   ↓
5. AI generates Question #2 (based on Answer #1)
   ↓
6. Repeat steps 3-5 until all questions done
   ↓
7. AI generates Final Report
```

### Question Generation Logic:

**First Question:**
- Fundamental knowledge assessment
- Relevant to job role & requirements
- Medium difficulty

**Subsequent Questions:**
- Analyze previous answer
- Identify strengths/weaknesses
- Generate follow-up that:
  - Explores mentioned topics deeper
  - Probes expertise areas
  - Addresses gaps/misconceptions
  - Adjusts difficulty based on performance

## 📊 Example Interview Session

**Job:** Full Stack Java Engineer  
**Level:** Mid-level  
**Questions:** 5

**Q1 (Gen by AI):** "Explain the difference between ArrayList and LinkedList in Java and when you would use each."  
**A1:** [Candidate answers...]  
**Score:** 7/10  

**Q2 (Gen by AI based on A1):** "You mentioned performance considerations. Can you design a solution for a high-throughput data processing system using Java collections?"  
**A2:** [Candidate answers...]  
**Score:** 8/10  

...

**Final Report:**
```
Executive Summary:
The candidate demonstrated strong fundamental knowledge...

Strengths:
- Deep understanding of Java collections
- Good system design thinking
- Clear communication

Areas for Improvement:
- Concurrency handling needs improvement
- Limited knowledge of advanced Spring features

Overall Recommendation: RECOMMEND
Score: 38/50 (7.6/10 average)
```

## 🔧 Technical Details

### Frontend Changes:
- `StartForm.js`: Added dropdown to select num_questions (3, 5, 10, 20)
- `api/index.js`: Send num_questions to backend

### Backend Changes:
- `api.py`: Accept num_questions parameter
- `llm_helpers.py`: 
  - `call_llm_generate_question()`: Generate dynamic questions
  - `call_llm_generate_final_report()`: Create comprehensive final report
- `nodes.py`:
  - Updated `select_question_node`: Use AI generation instead of DB
  - Updated `start_interview_node`: No longer fetch from DB
  - Added `generate_final_report_node`: Generate final report
- `graph.py`: Added final_report node to workflow

### Workflow:
```
start_interview → select_question → ask_question → receive_response 
→ process_response → generate_feedback → provide_feedback → update_state
→ [loop back to select_question OR go to generate_final_report]
→ generate_final_report → END
```

## 💾 Database Note

**MongoDB `questions` collection is NO LONGER USED for question selection**
- The collection still exists but is not queried during interviews
- AI generates all questions dynamically
- Can be removed or used for other purposes

## 🎨 User Experience

### Start Form:
```
Job Role: [Select: Software Engineer, Full Stack Java Engineer, ...]
Candidate ID: [Input]
Industry: [Optional Input]
Job Level: [Select: Junior, Mid-level, Senior, ...]
Employment Type: [Select: Full-time, Part-time, ...]
Salary Range: [Optional Input]
Job Description: [Optional TextArea]
Number of Questions: [Select: 3 (Quick), 5 (Standard), 10 (Detailed), 20 (Comprehensive)]
```

### Interview Chat:
- AI asks question
- User types answer
- System shows "typing..." while processing
- Immediate feedback after each answer
- Score displayed (X/10)
- Next question adapts based on answer

### Completion:
- Final comprehensive report displayed
- Overall score shown
- Detailed assessment available

## 📋 Configuration

### Number of Questions:
- 3: Quick screening (10-15 mins)
- 5: Standard interview (20-30 mins) **[DEFAULT]**
- 10: Detailed assessment (40-60 mins)
- 20: Comprehensive evaluation (1-2 hours)

### LLM Model:
- Currently using: `gemini-2.0-flash-exp`
- Configured in: `agent/config.py`

## 🐛 Known Issues

- ❌ AsyncSqliteSaver connection issue → Using MemorySaver temporarily
  - Conversation state will be lost on server restart
  - TODO: Fix AsyncSqliteSaver initialization

## 🔮 Future Enhancements

1. Fix AsyncSqliteSaver for persistent checkpointing
2. Add question categories/topics tracking
3. Export final report as PDF
4. Interview replay/review functionality
5. Multi-language support
6. Voice-to-text for answers

## 📝 Notes

- All questions are generated in real-time by AI
- Each interview is unique and personalized
- Context-aware questioning improves assessment quality
- Final report provides actionable insights for hiring decisions
