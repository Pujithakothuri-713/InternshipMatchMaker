#!/usr/bin/env python3
"""
Simple backend test without problematic imports
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
        import traceback
        traceback.print_exc()
        return False

def test_core_components():
    """Test core components without matching algorithm"""
    print("🚀 Testing Core Components...")
    
    try:
        # Test database models
        from database.models import Base, Candidate, Company, Internship
        from sqlalchemy import create_engine
        
        # Create test database
        engine = create_engine("sqlite:///test_core.db", echo=False)
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
        
        # Test basic FastAPI imports
        from fastapi import FastAPI
        from pydantic import BaseModel
        print("✅ FastAPI components working")
        
        # Clean up
        import os
        if os.path.exists("test_core.db"):
            os.remove("test_core.db")
        
        return True
        
    except Exception as e:
        print(f"❌ Core component error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run simplified tests"""
    print("🎯 Simplified Backend Test")
    print("=" * 40)
    
    tests = [
        ("Core Components", test_core_components),
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
        print("✅ Core backend is working! Let's start the backend server.")
        print("\n🚀 Ready to test:")
        print("   1. Starting backend server...")
        return True
    else:
        print("❌ Some core components failed.")
        return False
    
    return passed == total

if __name__ == "__main__":
    if main():
        print("\n🔥 Starting backend server for testing...")
        
        # Start the backend server
        import subprocess
        import time
        
        try:
            print("Starting FastAPI backend...")
            # Change to backend directory and run the server
            server_process = subprocess.Popen(
                ["python", "main.py"],
                cwd="backend",
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            print("✅ Backend server started!")
            print("📍 API Documentation: http://localhost:8000/docs")
            print("📍 Health Check: http://localhost:8000/health")
            print("\n⏳ Server is running... Press Ctrl+C to stop")
            
            # Monitor the server output
            for line in server_process.stdout:
                print(line.strip())
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            server_process.terminate()
            print("✅ Server stopped")
            
        except Exception as e:
            print(f"❌ Server error: {e}")
