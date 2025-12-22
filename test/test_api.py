import requests
import json
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Test the interview API
url = "http://localhost:8000/interview/start"

payload = {
    "job_role": "Software Engineer",
    "candidate_id": "test_candidate_123",
    "job_info": {
        "industry": "Technology",
        "job_level": "Mid-level",
        "employment_type": "Full-time",
        "salary_range": "$100k - $150k",
        "job_description": "Looking for a software engineer with experience in Python and React"
    }
}

print("Testing Interview API...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print("-" * 60)

try:
    response = requests.post(url, json=payload, timeout=60)
    print(f"Status Code: {response.status_code}")
    
    data = response.json()
    
    if data.get('status') == 'error':
        print(f"\nERROR: {data.get('error_message', 'Unknown error')}")
    elif data.get('current_question'):
        print("\nSUCCESS! Generated question:")
        print(f"  Text: {data['current_question']['text']}")
        print(f"  Topic: {data['current_question'].get('topic', 'N/A')}")
        print(f"  Difficulty: {data['current_question'].get('difficulty', 'N/A')}")
        print(f"  Session ID: {data.get('session_id', 'N/A')}")
    else:
        print("\nFAILED: No question generated")
        print(f"Full response: {json.dumps(data, indent=2)}")
            
except requests.exceptions.Timeout:
    print("Request timed out (>60s)")
except Exception as e:
    print(f"Error: {e}")
