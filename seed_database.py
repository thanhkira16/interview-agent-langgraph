"""
Script to seed MongoDB with sample interview questions
Run this script to populate the interviewDB database with sample questions
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent / "agent" / ".env"
load_dotenv(env_path)

mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
database_name = os.getenv("MONGODB_DB_NAME", "interviewDB")

# Sample questions data
SAMPLE_QUESTIONS = [
    # Software Engineer Questions
    {
        "job_role": "Software Engineer",
        "text": "What is the difference between a process and a thread?",
        "topic": "Operating Systems",
        "difficulty": "Medium"
    },
    {
        "job_role": "Software Engineer",
        "text": "Explain the concept of Big O notation and why it's important.",
        "topic": "Data Structures & Algorithms",
        "difficulty": "Easy"
    },
    {
        "job_role": "Software Engineer",
        "text": "What are the SOLID principles in object-oriented programming?",
        "topic": "Design Patterns",
        "difficulty": "Medium"
    },
    {
        "job_role": "Software Engineer",
        "text": "How would you design a URL shortening service like bit.ly?",
        "topic": "System Design",
        "difficulty": "Hard"
    },
    {
        "job_role": "Software Engineer",
        "text": "Explain the difference between SQL and NoSQL databases. When would you use each?",
        "topic": "Databases",
        "difficulty": "Medium"
    },
    {
        "job_role": "Software Engineer",
        "text": "What is a race condition and how can you prevent it?",
        "topic": "Concurrency",
        "difficulty": "Hard"
    },
    {
        "job_role": "Software Engineer",
        "text": "Describe your experience with version control systems like Git.",
        "topic": "Tools & Practices",
        "difficulty": "Easy"
    },
    {
        "job_role": "Software Engineer",
        "text": "How do you approach debugging a production issue?",
        "topic": "Behavioral",
        "difficulty": "Medium"
    },
    
    # Full Stack Java Engineer Questions
    {
        "job_role": "Full Stack Java Engineer",
        "text": "Explain the difference between ArrayList and LinkedList in Java.",
        "topic": "Java Fundamentals",
        "difficulty": "Easy"
    },
    {
        "job_role": "Full Stack Java Engineer",
        "text": "What is Spring Boot and what are its main advantages?",
        "topic": "Java Frameworks",
        "difficulty": "Medium"
    },
    {
        "job_role": "Full Stack Java Engineer",
        "text": "Explain the concept of dependency injection in Spring.",
        "topic": "Java Frameworks",
        "difficulty": "Medium"
    },
    {
        "job_role": "Full Stack Java Engineer",
        "text": "What is the difference between React hooks and class components?",
        "topic": "Frontend Development",
        "difficulty": "Medium"
    },
    {
        "job_role": "Full Stack Java Engineer",
        "text": "How would you implement microservices architecture in a Java application?",
        "topic": "System Architecture",
        "difficulty": "Hard"
    },
    {
        "job_role": "Full Stack Java Engineer",
        "text": "Explain Java memory management and garbage collection.",
        "topic": "Java Fundamentals",
        "difficulty": "Hard"
    },
    {
        "job_role": "Full Stack Java Engineer",
        "text": "What is REST API and what are the best practices for designing one?",
        "topic": "Backend Development",
        "difficulty": "Medium"
    },
    {
        "job_role": "Full Stack Java Engineer",
        "text": "How do you handle state management in React applications?",
        "topic": "Frontend Development",
        "difficulty": "Medium"
    },
    {
        "job_role": "Full Stack Java Engineer",
        "text": "Explain the difference between SQL JOIN types.",
        "topic": "Databases",
        "difficulty": "Medium"
    },
    
    # Data Scientist Questions
    {
        "job_role": "Data Scientist",
        "text": "Explain the bias-variance tradeoff in machine learning.",
        "topic": "Machine Learning",
        "difficulty": "Medium"
    },
    {
        "job_role": "Data Scientist",
        "text": "What is the difference between supervised and unsupervised learning?",
        "topic": "Machine Learning",
        "difficulty": "Easy"
    },
    {
        "job_role": "Data Scientist",
        "text": "How would you handle missing data in a dataset?",
        "topic": "Data Preprocessing",
        "difficulty": "Medium"
    },
    {
        "job_role": "Data Scientist",
        "text": "Explain the concept of overfitting and how to prevent it.",
        "topic": "Machine Learning",
        "difficulty": "Medium"
    },
    {
        "job_role": "Data Scientist",
        "text": "What is cross-validation and why is it important?",
        "topic": "Model Evaluation",
        "difficulty": "Medium"
    },
    {
        "job_role": "Data Scientist",
        "text": "Describe a time when you had to present complex data insights to non-technical stakeholders.",
        "topic": "Behavioral",
        "difficulty": "Medium"
    },
    {
        "job_role": "Data Scientist",
        "text": "What is the difference between precision and recall?",
        "topic": "Machine Learning Metrics",
        "difficulty": "Easy"
    },
    {
        "job_role": "Data Scientist",
        "text": "Explain how a random forest algorithm works.",
        "topic": "Machine Learning Algorithms",
        "difficulty": "Hard"
    },
    
    # Product Manager Questions
    {
        "job_role": "Product Manager",
        "text": "How do you prioritize features for a product roadmap?",
        "topic": "Product Strategy",
        "difficulty": "Medium"
    },
    {
        "job_role": "Product Manager",
        "text": "Describe your experience with Agile/Scrum methodologies.",
        "topic": "Project Management",
        "difficulty": "Easy"
    },
    {
        "job_role": "Product Manager",
        "text": "How do you measure product success?",
        "topic": "Product Metrics",
        "difficulty": "Medium"
    },
    {
        "job_role": "Product Manager",
        "text": "Tell me about a time when you had to make a difficult product decision.",
        "topic": "Behavioral",
        "difficulty": "Medium"
    },
    {
        "job_role": "Product Manager",
        "text": "How do you conduct user research and gather customer feedback?",
        "topic": "User Research",
        "difficulty": "Medium"
    },
    {
        "job_role": "Product Manager",
        "text": "What frameworks do you use for product strategy?",
        "topic": "Product Strategy",
        "difficulty": "Medium"
    },
    {
        "job_role": "Product Manager",
        "text": "How do you work with engineering teams to deliver features?",
        "topic": "Collaboration",
        "difficulty": "Easy"
    },
    {
        "job_role": "Product Manager",
        "text": "Design a feature for improving user engagement on a social media platform.",
        "topic": "Product Design",
        "difficulty": "Hard"
    },
    
    # Computer Vision Engineer Questions
    {
        "job_role": "Computer Vision Engineer",
        "text": "Explain the difference between object detection and image segmentation.",
        "topic": "Computer Vision Fundamentals",
        "difficulty": "Medium"
    },
    {
        "job_role": "Computer Vision Engineer",
        "text": "What is a Convolutional Neural Network (CNN) and how does it work?",
        "topic": "Deep Learning",
        "difficulty": "Medium"
    },
    {
        "job_role": "Computer Vision Engineer",
        "text": "Explain the concept of transfer learning in computer vision.",
        "topic": "Deep Learning",
        "difficulty": "Medium"
    },
    {
        "job_role": "Computer Vision Engineer",
        "text": "What are common image augmentation techniques and why are they important?",
        "topic": "Data Preprocessing",
        "difficulty": "Easy"
    },
    {
        "job_role": "Computer Vision Engineer",
        "text": "How would you approach building a real-time face recognition system?",
        "topic": "System Design",
        "difficulty": "Hard"
    },
    {
        "job_role": "Computer Vision Engineer",
        "text": "Explain the difference between R-CNN, Fast R-CNN, and Faster R-CNN.",
        "topic": "Object Detection",
        "difficulty": "Hard"
    },
    {
        "job_role": "Computer Vision Engineer",
        "text": "What is YOLO and how does it differ from traditional object detection methods?",
        "topic": "Object Detection",
        "difficulty": "Medium"
    },
    {
        "job_role": "Computer Vision Engineer",
        "text": "How do you evaluate the performance of a computer vision model?",
        "topic": "Model Evaluation",
        "difficulty": "Medium"
    },
]


def seed_database():
    """Seed MongoDB with sample interview questions"""
    try:
        # Connect to MongoDB
        print(f"Connecting to MongoDB at {mongodb_uri}...")
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ismaster')
        print(f"✅ Connected to MongoDB successfully!")
        
        # Get database and collection
        db = client[database_name]
        questions_collection = db.questions
        
        # Check if collection already has data
        existing_count = questions_collection.count_documents({})
        if existing_count > 0:
            print(f"\n⚠️  Warning: Collection 'questions' already has {existing_count} documents.")
            response = input("Do you want to clear existing data and reseed? (yes/no): ")
            if response.lower() in ['yes', 'y']:
                questions_collection.delete_many({})
                print("✅ Cleared existing data.")
            else:
                print("❌ Seeding cancelled. Existing data preserved.")
                return
        
        # Insert sample questions
        print(f"\n📝 Inserting {len(SAMPLE_QUESTIONS)} sample questions...")
        result = questions_collection.insert_many(SAMPLE_QUESTIONS)
        
        print(f"✅ Successfully inserted {len(result.inserted_ids)} questions!")
        
        # Show statistics
        print("\n📊 Database Statistics:")
        pipeline = [
            {"$group": {"_id": "$job_role", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        stats = list(questions_collection.aggregate(pipeline))
        
        for stat in stats:
            print(f"  - {stat['_id']}: {stat['count']} questions")
        
        print(f"\n🎉 Database seeding completed successfully!")
        print(f"Database: {database_name}")
        print(f"Collection: questions")
        print(f"Total documents: {questions_collection.count_documents({})}")
        
    except ConnectionFailure as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("Please ensure MongoDB is running and accessible.")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
    finally:
        if 'client' in locals():
            client.close()
            print("\n👋 MongoDB connection closed.")


if __name__ == "__main__":
    print("=" * 60)
    print("MongoDB Interview Questions Seeder")
    print("=" * 60)
    seed_database()
