#!/usr/bin/env python3
"""
Simple test script to verify basic functionality before starting the full backend
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_environment():
    """Test environment setup"""
    print("🔧 Testing Environment Setup...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        print(f"✅ GROQ_API_KEY found: {groq_key[:20]}...")
    else:
        print("❌ GROQ_API_KEY not found in environment")
        return False
    
    return True

def test_groq_connection():
    """Test Groq API connection"""
    print("\n🤖 Testing Groq API Connection...")
    
    try:
        from groq import Groq
        import os
        
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # Simple test
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "user", "content": "Say 'Hello from Groq!' and nothing else."}
            ],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✅ Groq API working! Response: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Groq API error: {e}")
        return False

def test_database():
    """Test database creation"""
    print("\n🗄️ Testing Database Setup...")
    
    try:
        # Import required modules
        from sqlalchemy import create_engine, text
        
        # Create a simple test database
        engine = create_engine("sqlite:///test_internship_matcher.db", echo=False)
        
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test"))
            test_value = result.fetchone()[0]
            
        if test_value == 1:
            print("✅ Database connection working!")
            
            # Clean up test database
            import os
            if os.path.exists("test_internship_matcher.db"):
                os.remove("test_internship_matcher.db")
            
            return True
        else:
            print("❌ Database test failed")
            return False
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_basic_imports():
    """Test if we can import our modules"""
    print("\n📦 Testing Module Imports...")
    
    try:
        # Test basic FastAPI
        from fastapi import FastAPI
        print("✅ FastAPI import successful")
        
        # Test SQLAlchemy
        from sqlalchemy import create_engine
        print("✅ SQLAlchemy import successful")
        
        # Test Pydantic
        from pydantic import BaseModel
        print("✅ Pydantic import successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def create_minimal_backend():
    """Create and test a minimal FastAPI backend"""
    print("\n🚀 Testing Minimal FastAPI Backend...")
    
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel
        import uvicorn
        import threading
        import time
        import requests
        
        # Create minimal app
        app = FastAPI(title="Test Internship Matcher API")
        
        class HealthResponse(BaseModel):
            status: str
            message: str
        
        @app.get("/health", response_model=HealthResponse)
        def health_check():
            return HealthResponse(status="ok", message="Backend is working!")
        
        @app.get("/test-groq")
        def test_groq():
            try:
                from groq import Groq
                import os
                
                client = Groq(api_key=os.getenv("GROQ_API_KEY"))
                response = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[{"role": "user", "content": "Hello!"}],
                    max_tokens=20
                )
                
                return {
                    "status": "success",
                    "response": response.choices[0].message.content
                }
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        # Start server in a separate thread
        def run_server():
            uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait for server to start
        time.sleep(3)
        
        # Test the endpoints
        try:
            # Test health endpoint
            response = requests.get("http://127.0.0.1:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Health endpoint working!")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                return False
            
            # Test Groq endpoint
            response = requests.get("http://127.0.0.1:8000/test-groq", timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    print("✅ Groq integration working!")
                    print(f"   AI Response: {result.get('response')}")
                else:
                    print(f"❌ Groq integration failed: {result.get('message')}")
                    return False
            else:
                print(f"❌ Groq endpoint failed: {response.status_code}")
                return False
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Backend test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🎯 Internship Matcher - Basic Functionality Test")
    print("=" * 50)
    
    tests = [
        ("Environment Setup", test_environment),
        ("Basic Imports", test_basic_imports),
        ("Database Connection", test_database),
        ("Groq API", test_groq_connection),
        ("Minimal Backend", create_minimal_backend),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print(f"\n{'='*50}")
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! The backend should work properly.")
        print("\n🚀 Next steps:")
        print("   1. Run: python backend/main.py")
        print("   2. Visit: http://localhost:8000/docs")
        print("   3. Run: streamlit run frontend/app.py")
    else:
        print("❌ Some tests failed. Please fix the issues before proceeding.")
    
    return passed == total

if __name__ == "__main__":
    # Install missing packages if needed
    missing_packages = []
    
    try:
        import requests
    except ImportError:
        missing_packages.append("requests")
    
    if missing_packages:
        print(f"Installing missing packages: {missing_packages}")
        import subprocess
        import sys
        for package in missing_packages:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    main()
