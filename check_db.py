"""Quick script to check MongoDB questions"""
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / "agent" / ".env"
load_dotenv(env_path)

mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
database_name = os.getenv("MONGODB_DB_NAME", "interviewDB")

client = MongoClient(mongodb_uri)
db = client[database_name]

print("\n📊 Questions by Job Role:")
print("-" * 50)
stats = db.questions.aggregate([
    {"$group": {"_id": "$job_role", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
])

total = 0
for stat in stats:
    count = stat['count']
    total += count
    print(f"  • {stat['_id']:30s} : {count:2d} questions")

print("-" * 50)
print(f"  ✅ Total: {total} questions in database")
print()

# Show sample question
sample = db.questions.find_one()
if sample:
    print("📝 Sample Question:")
    print(f"  Job Role: {sample.get('job_role')}")
    print(f"  Topic: {sample.get('topic')}")
    print(f"  Difficulty: {sample.get('difficulty')}")
    print(f"  Question: {sample.get('text')[:80]}...")

client.close()
