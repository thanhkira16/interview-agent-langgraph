import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from langchain_google_genai import ChatGoogleGenerativeAI
from pathlib import Path

# Load .env from agent directory
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)
mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
database_name = os.getenv("MONGODB_DB_NAME", "interviewDB")

client = None
db = None


try:
    client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
    client.admin.command('ismaster') # Check connection
    db = client[database_name]
    print(f"MongoDB connection successful! Connected to database: {database_name}")
except ConnectionFailure as e:
    print(f"MongoDB connection failed: {e}")
    print("Please ensure MongoDB is running and accessible.")
    client = None
    db = None
except Exception as e:
    print(f"An unexpected error occurred during MongoDB connection: {e}")
    client = None
    db = None

# Initialize Google Gemini LLM
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError(
        "GOOGLE_API_KEY not found in environment variables!\n"
        "Please create a .env file in the 'agent' directory with:\n"
        "GOOGLE_API_KEY=your_actual_api_key\n"
        "Get your API key from: https://aistudio.google.com/apikey"
    )

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    google_api_key=google_api_key
)

TOTAL_QUESTIONS_PLANNED = int(os.getenv("NUM_QUESTIONS", "5"))
