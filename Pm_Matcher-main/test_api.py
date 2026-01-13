#!/usr/bin/env python3
"""
Test the running backend API
"""

import requests
import json
import time

def test_backend_api():
    """Test the backend API endpoints"""
    base_url = "http://localhost:8001"
    
    print("🧪 Testing Backend API Endpoints")
    print("=" * 40)
    
    # Wait a moment for server to start
    time.sleep(3)
    
    tests = [
        ("Health Check", "GET", "/health", None),
        ("Root Endpoint", "GET", "/", None),
        ("Test AI Integration", "GET", "/test-ai", None),
        ("Create Candidate", "POST", "/candidates/", {
            "name": "John Doe",
            "email": "john@example.com",
            "skills": ["Python", "Data Science"],
            "location": "Mumbai",
            "social_category": "OC",
            "area_type": "URBAN"
        }),
        ("Get Candidates", "GET", "/candidates/", None),
        ("Create Internship", "POST", "/internships/", {
            "title": "Data Science Intern",
            "company_name": "TechCorp",
            "description": "Work on machine learning projects",
            "required_skills": ["Python", "Machine Learning"],
            "location": "Mumbai",
            "duration_months": 6,
            "stipend": 15000
        }),
        ("Get Internships", "GET", "/internships/", None),
        ("Match Request", "POST", "/match/", {
            "candidate_skills": ["Python", "Data Science"],
            "candidate_location": "Mumbai",
            "candidate_category": "OC",
            "internship_title": "Data Science Intern",
            "internship_skills": ["Python", "Machine Learning"],
            "internship_location": "Mumbai"
        })
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, method, endpoint, data in tests:
        print(f"\n🔄 Testing: {test_name}")
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            elif method == "POST":
                response = requests.post(f"{base_url}{endpoint}", json=data, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {test_name}: Status {response.status_code}")
                result = response.json()
                
                # Show some key info from response
                if "message" in result:
                    print(f"   Message: {result['message']}")
                elif "status" in result:
                    print(f"   Status: {result['status']}")
                elif "ai_recommendation" in result:
                    ai_rec = result["ai_recommendation"]
                    print(f"   AI Recommendation: {ai_rec.get('recommendation', 'N/A')[:50]}...")
                    print(f"   Confidence: {ai_rec.get('confidence_score', 'N/A')}")
                
                passed += 1
            else:
                print(f"❌ {test_name}: Status {response.status_code}")
                print(f"   Error: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {test_name}: Connection error - {e}")
        except Exception as e:
            print(f"❌ {test_name}: Error - {e}")
    
    print(f"\n{'='*40}")
    print(f"🎯 API Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ Backend is fully working!")
        print("\n🚀 Next steps:")
        print("   1. Backend API: http://localhost:8000/docs")
        print("   2. Start frontend: streamlit run frontend/app.py")
    else:
        print("❌ Some API tests failed.")
    
    return passed == total

if __name__ == "__main__":
    test_backend_api()
