# 🤖 AI-Powered Interview Agent with LangGraph

An intelligent interview system that uses **Google Gemini AI** to dynamically generate interview questions and provide comprehensive assessments. Built with **LangGraph**, **FastAPI**, and **React**.

## ✨ Features

- 🎯 **Dynamic Question Generation** - AI creates personalized questions based on job context and previous answers
- 📊 **Real-time Scoring** - Immediate feedback and scoring for each answer
- 💬 **Chat-based Interface** - Modern messenger-style UI for natural conversation
- 📝 **Comprehensive Final Report** - Detailed assessment with strengths, weaknesses, and hiring recommendations
- ⚙️ **Customizable Interview Length** - Choose 3, 5, 10, or 20 questions
- 🔄 **Adaptive Difficulty** - Questions adjust based on candidate performance

## 🏗️ Architecture

```
Frontend (React + Material-UI)
    ↓
Backend API (FastAPI)
    ↓
LangGraph Workflow
    ↓
Google Gemini AI (Question Generation, Evaluation, Feedback)
```

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.10+** installed
- **Node.js 16+** and **npm** installed
- **MongoDB** instance (local or cloud)
- **Google API Key** for Gemini ([Get it here](https://aistudio.google.com/apikey))

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/nikhilcramakrishnan/interview-agent-langgraph.git
cd interview-agent-langgraph
```

### 2. Backend Setup

#### 2.1. Create Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

#### 2.2. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2.3. Configure Environment Variables

Create a file named `.env` in the `agent` directory:

```bash
# agent/.env
GOOGLE_API_KEY=your_google_gemini_api_key_here
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=interviewDB
NUM_QUESTIONS=5
```

**Get your Google API Key:**
1. Visit https://aistudio.google.com/apikey
2. Create a new API key
3. Copy and paste into `.env` file

#### 2.4. Setup MongoDB (Optional)

If you want to seed sample questions (note: the system now uses AI to generate questions dynamically):

```bash
# Start MongoDB locally or use MongoDB Atlas
# Then run the seed script:
python seed_database.py
```

### 3. Frontend Setup

#### 3.1. Navigate to Frontend Directory

```bash
cd frontend
```

#### 3.2. Install Dependencies

```bash
npm install
```

## 🎬 Running the Application

### Method 1: Run Both Servers Separately

**Terminal 1 - Backend:**
```bash
# From project root directory
python -m uvicorn agent.api:api --reload
#  D:/Shool/Document/DoAnTotNghiep/interview-agent-langgraph-main/.venv/Scripts/python.exe -m uvicorn agent.api:api --reload
```
✅ Backend will run on: `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
# From project root directory
cd frontend
npm start
```
✅ Frontend will run on: `http://localhost:3000`

### Method 2: Using Virtual Environment (Windows)

**Backend:**
```bash
# From project root directory
.venv\Scripts\python.exe -m uvicorn agent.api:api --reload
```

**Frontend:**
```bash
# From project root directory
cd frontend && npm start
```

### Method 3: Using Virtual Environment (macOS/Linux)

**Backend:**
```bash
# From project root directory
.venv/bin/python -m uvicorn agent.api:api --reload
```

**Frontend:**
```bash
# From project root directory
cd frontend && npm start
```

## 🧪 Testing the API

Test the backend API directly:

```bash
python test_api.py
```

This will:
- Start a test interview session
- Generate a question using AI
- Display the response

## 📱 Using the Application

### 1. Start an Interview

1. Open `http://localhost:3000` in your browser
2. Fill in the interview form:
   - **Job Role**: Select from dropdown (Software Engineer, Full Stack Java Engineer, etc.)
   - **Candidate ID**: Enter any ID (e.g., `TEST_001`)
   - **Job Info** (Optional but recommended):
     - Industry
     - Job Level (Junior, Mid-level, Senior, Lead)
     - Employment Type (Full-time, Part-time, Contract)
     - Salary Range
     - Job Description
   - **Number of Questions**: Choose 3, 5, 10, or 20
3. Click **"Start Interview"**

### 2. Answer Questions

- AI will generate the first question based on your job context
- Type your answer in the chat input box
- Press **Enter** or click **Send**
- Receive immediate feedback and score (X/10)
- Next question will be tailored based on your previous answer

### 3. Review Final Report

After completing all questions, you'll receive a comprehensive report including:
- **Executive Summary** - Overall impression
- **Strengths** - 3-5 key positive points with examples
- **Areas for Improvement** - 3-5 points for growth
- **Technical Assessment** - Depth of knowledge and problem-solving
- **Overall Score** - Total score and average
- **Hiring Recommendation** - Strongly Recommend / Recommend / Maybe / Not Recommend

## 🗂️ Project Structure

```
interview-agent-langgraph/
├── agent/                      # Backend code
│   ├── .env                    # Environment variables (create this)
│   ├── api.py                  # FastAPI endpoints
│   ├── config.py               # Configuration & LLM setup
│   ├── models.py               # Pydantic models
│   ├── graph.py                # LangGraph workflow definition
│   ├── nodes.py                # Workflow nodes
│   ├── llm_helpers.py          # AI functions (question gen, evaluation)
│   └── database.py             # MongoDB connection
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── Interview.js    # Main interview chat UI
│   │   │   └── StartForm.js    # Interview setup form
│   │   ├── api/
│   │   │   └── index.js        # API client
│   │   └── context/
│   │       └── InterviewContext.js  # State management
│   └── package.json
├── db/                         # Checkpoints database
├── requirements.txt            # Python dependencies
├── seed_database.py            # MongoDB seeding script
├── test_api.py                 # API testing script
├── check_db.py                 # Database checking script
└── README.md                   # This file
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GOOGLE_API_KEY` | Google Gemini API key | - | ✅ Yes |
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017/` | ✅ Yes |
| `MONGODB_DB_NAME` | Database name | `interviewDB` | ✅ Yes |
| `NUM_QUESTIONS` | Default number of questions | `5` | No |

### Interview Settings

You can customize the interview in `StartForm.js`:
- Default questions: Change `useState(5)` to desired number
- Job roles: Edit `jobRoles` array (line 55-60)
- Job levels: Edit `jobLevels` array

## ⚙️ How It Works

### Workflow Flow

```
1. START INTERVIEW
   ↓
2. GENERATE QUESTION (AI analyzes context and history)
   ↓
3. ASK QUESTION (Display to user)
   ↓
4. RECEIVE RESPONSE (User types answer)
   ↓
5. ANALYZE & EVALUATE (AI scores 0-10)
   ↓
6. GENERATE FEEDBACK (AI provides constructive feedback)
   ↓
7. UPDATE STATE (Save to history, increment score)
   ↓
8. DECISION:
   - More questions? → Go to step 2
   - All done? → Go to step 9
   ↓
9. GENERATE FINAL REPORT (Comprehensive assessment)
   ↓
10. END
```

### AI Question Generation Logic

**First Question:**
- Warm-up assessment of fundamental knowledge
- Relevant to job role and requirements
- Usually medium difficulty

**Subsequent Questions:**
- Analyzes previous answer in detail
- Explores topics candidate mentioned deeper
- Adjusts difficulty based on performance:
  - Increase difficulty if candidate is doing well
  - Decrease difficulty if candidate is struggling
- Identifies and probes knowledge gaps
- Context-aware and highly personalized

## 🐛 Troubleshooting

### Backend Issues

**Error: "GOOGLE_API_KEY not found"**
```bash
# Solution: Make sure .env file exists in agent/ directory
# Check the file name is exactly: .env (not .env.txt)
# Verify the variable name: GOOGLE_API_KEY (all caps)
```

**Error: "MongoDB connection failed"**
```bash
# Option 1: Check MongoDB is running locally
# Windows: Services → MongoDB Server
# macOS/Linux: sudo systemctl status mongod

# Option 2: Use MongoDB Atlas (cloud)
# Update MONGODB_URI in .env to your Atlas connection string
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
```

**Error: "Module not found" or Import errors**
```bash
# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall

# Or install specific missing package
pip install langgraph langchain-google-genai
```

**Error: "Port 8000 already in use"**
```bash
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9

# Or use different port:
uvicorn agent.api:api --reload --port 8001
```

### Frontend Issues

**Error: "Port 3000 already in use"**
```bash
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:3000 | xargs kill -9
```

**Error: "npm install fails"**
```bash
# Clear npm cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**Frontend can't connect to backend (CORS error)**
```bash
# 1. Verify backend is running on http://localhost:8000
# 2. Check API_BASE in frontend/src/api/index.js
# 3. Check browser console for exact error message
```

### Interview Issues

**Questions not generating**
```bash
# Check backend logs for errors
# Verify GOOGLE_API_KEY is correct
# Test API directly: python test_api.py
```

**"Connection object has no attribute 'is_alive'" error**
```bash
# This is a known issue with AsyncSqliteSaver
# Solution: Using MemorySaver (already implemented)
# Note: Interview state will be lost on server restart
```

## 🔄 API Endpoints

### POST `/interview/start`

Start a new interview session.

**Request Body:**
```json
{
  "job_role": "Software Engineer",
  "candidate_id": "TEST_001",
  "num_questions": 5,
  "job_info": {
    "industry": "Technology",
    "job_level": "Mid-level",
    "employment_type": "Full-time",
    "salary_range": "$100k - $150k",
    "job_description": "Python and React developer with microservices experience..."
  }
}
```

**Response:**
```json
{
  "session_id": "a5b1da92-53e5-49b8-b8db-a97197462200",
  "status": "in_progress",
  "current_question": {
    "id": "gen_abc123",
    "text": "Explain the difference between process and thread in operating systems.",
    "topic": "Operating Systems",
    "difficulty": "Medium",
    "rationale": "Starting with fundamental CS concepts relevant to the role."
  },
  "overall_score": 0,
  "feedback": null,
  "interview_history_summary": []
}
```

### POST `/interview/{session_id}/submit_answer`

Submit an answer to the current question.

**Request Body:**
```json
{
  "candidate_response": "A process is an independent execution unit with its own memory space, while a thread is a lightweight unit within a process that shares memory..."
}
```

**Response:**
```json
{
  "session_id": "a5b1da92-53e5-49b8-b8db-a97197462200",
  "status": "in_progress",
  "current_question": {
    "id": "gen_xyz789",
    "text": "You mentioned memory sharing. How would you design a thread-safe singleton pattern in Python?",
    "topic": "Concurrency & Design Patterns",
    "difficulty": "Hard"
  },
  "feedback": "Excellent answer! Score: 9/10. You clearly explained the key differences...",
  "overall_score": 9.0,
  "interview_history_summary": [
    {
      "question": {...},
      "response": "...",
      "evaluation": {...},
      "feedback": "..."
    }
  ]
}
```

## 📊 Database (Optional)

### MongoDB Collection: `questions`

```javascript
{
  "_id": ObjectId,
  "job_role": String,          // e.g., "Software Engineer"
  "text": String,              // Question text
  "topic": String,             // e.g., "Data Structures"
  "difficulty": String         // "Easy" | "Medium" | "Hard"
}
```

**Note:** This collection is now **optional**. The system generates questions dynamically using AI and doesn't require pre-populated questions.

If you want to seed sample questions:
```bash
python seed_database.py
python check_db.py  # Verify seeding
```

## 🎨 Customization

### Change AI Model

Edit `agent/config.py`:
```python
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",  # or "gemini-pro", "gemini-1.5-pro"
    google_api_key=google_api_key
)
```

### Modify Number of Questions

Edit `frontend/src/components/StartForm.js`:
```javascript
const [numQuestions, setNumQuestions] = useState(5);  // Change default here

// Or edit the dropdown options:
<MenuItem value={3}>3 Questions (Quick)</MenuItem>
<MenuItem value={5}>5 Questions (Standard)</MenuItem>
<MenuItem value={10}>10 Questions (Detailed)</MenuItem>
<MenuItem value={20}>20 Questions (Comprehensive)</MenuItem>
```

### Customize UI Theme

Edit `frontend/src/components/Interview.js`:
```javascript
// Primary color
bgcolor: '#1976d2',  // Change to your brand color

// Background
bgcolor: '#f0f2f5',  // Change chat background

// Chat bubble colors
bgcolor: '#1976d2',  // AI messages
bgcolor: '#e3f2fd',  // User messages
```

### Add More Job Roles

Edit `frontend/src/components/StartForm.js`:
```javascript
const jobRoles = [
  "Software Engineer",
  "Full Stack Java Engineer",
  "Data Scientist",
  "Product Manager",
  "DevOps Engineer",        // Add your roles here
  "Machine Learning Engineer",
  // ...
];
```

## 📝 Known Issues & Limitations

- ⚠️ **In-Memory Storage**: Currently using MemorySaver. Interview state is lost on server restart.
- 🔄 **AsyncSqliteSaver Issue**: Working on fixing persistent checkpoint storage.
- ⏱️ **Response Time**: First question generation may take 5-10 seconds (AI processing).
- 🌐 **Single Session**: No concurrent session management (one interview at a time per server).

## 🚧 Future Enhancements

- [ ] Fix AsyncSqliteSaver for persistent state storage
- [ ] Add PostgreSQL/SQLite as alternative to MongoDB
- [ ] Export final report as PDF
- [ ] Interview replay and review functionality
- [ ] Multi-language support (Vietnamese, Spanish, etc.)
- [ ] Voice-to-text for spoken answers
- [ ] Real-time analytics dashboard
- [ ] Interview scheduling and calendar integration
- [ ] Candidate authentication and session management
- [ ] Admin panel for managing interviews
- [ ] Email notifications with interview results

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph) by LangChain
- Powered by [Google Gemini AI](https://ai.google.dev/)
- UI components from [Material-UI](https://mui.com/)
- Based on the original [interview-agent-langgraph](https://github.com/nikhilcramakrishnan/interview-agent-langgraph) by @nikhilcramakrishnan

## 📚 Additional Documentation

- **Technical Deep Dive**: See `README_AI_INTERVIEW.md` for detailed architecture
- **API Documentation**: See the API Endpoints section above
- **Troubleshooting Guide**: See the Troubleshooting section above

## 📞 Support & Contact

For issues, questions, or contributions:
- **GitHub Issues**: [Create an issue](https://github.com/nikhilcramakrishnan/interview-agent-langgraph/issues)
- **Pull Requests**: [Submit a PR](https://github.com/nikhilcramakrishnan/interview-agent-langgraph/pulls)

---

**Made with ❤️ using Google Gemini AI and LangGraph**

*Last Updated: December 2024*
