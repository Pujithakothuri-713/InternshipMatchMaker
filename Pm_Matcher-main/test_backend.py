#!/usr/bin/env python3
"""
Simple backend test with fixed AI integration
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

def test_ai_integration():
    """Test the fixed AI integration"""
    print("🤖 Testing AI Integration...")
    
    try:
        from utils.ai_integration import GroqAIManager
        
        # Create AI manager
        ai_manager = GroqAIManager()
        print("✅ AI Manager created successfully")
        
        # Test simple recommendation
        candidate_data = {
            "name": "Test Student",
            "skills": ["Python", "Data Analysis"],
            "location": "Mumbai",
            "category": "OC",
            "is_rural": False
        }
        
        internship_data = {
            "title": "Data Science Intern",
            "company": "Tech Corp",
            "location": "Mumbai",
            "required_skills": ["Python", "Machine Learning"],
            "description": "Work on data science projects"
        }
        
        match_scores = {
            "skill_similarity": 0.8,
            "location_match": 1.0,
            "qualification_match": 0.9,
            "overall_score": 0.85
        }
        
        print("🔄 Generating recommendation...")
        recommendation = ai_manager.generate_internship_recommendation(
            candidate_data, internship_data, match_scores
        )
        
        print("✅ AI Recommendation generated successfully!")
        print(f"   Recommendation: {recommendation.get('recommendation', 'N/A')[:100]}...")
        print(f"   Confidence: {recommendation.get('confidence_score', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Integration error: {e}")
        return False

def test_basic_backend():
    """Test basic backend components"""
    print("🚀 Testing Basic Backend Components...")
    
    try:
        # Test database models
        from database.models import Base, Candidate, Company, Internship
        from sqlalchemy import create_engine
        
        # Create test database
        engine = create_engine("sqlite:///test_backend.db", echo=False)
        Base.metadata.create_all(engine)
        print("✅ Database models working")
        
        # Test embeddings
        from utils.embeddings import EmbeddingManager
        embedding_manager = EmbeddingManager()
        
        test_embedding = embedding_manager.generate_skills_embedding(["Python programming"])
        if len(test_embedding) > 0:
            print("✅ Embeddings working")
        else:
            print("❌ Embeddings failed")
            return False
        
        # Test matching algorithm
        from utils.matching_algorithm import InternshipMatcher
        matcher = InternshipMatcher()
        print("✅ Matching algorithm initialized")
        
        # Clean up
        import os
        if os.path.exists("test_backend.db"):
            os.remove("test_backend.db")
        
        return True
        
    except Exception as e:
        print(f"❌ Backend component error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🎯 Backend Functionality Test")
    print("=" * 40)
    
    tests = [
        ("Backend Components", test_basic_backend),
        ("AI Integration", test_ai_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*15} {test_name} {'='*15}")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print(f"\n{'='*40}")
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ Backend is working! Ready to start the full application.")
        print("\n🚀 Next steps:")
        print("   1. Run: python backend/main.py")
        print("   2. Visit: http://localhost:8000/docs")
        print("   3. Run: streamlit run frontend/app.py")
    else:
        print("❌ Some backend components failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    main()
