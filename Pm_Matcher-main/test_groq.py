#!/usr/bin/env python3
"""
Simple Groq API test
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_groq():
    """Test Groq API with debug info"""
    print("🤖 Testing Groq API...")
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ No GROQ_API_KEY found")
        return False
    
    print(f"✅ API Key loaded: {api_key[:20]}...")
    
    try:
        from groq import Groq
        print("✅ Groq module imported successfully")
        
        # Create client
        client = Groq(api_key=api_key)
        print("✅ Groq client created")
        
        # Test simple request
        print("🔄 Making API request...")
        
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "user", "content": "Hello! Just say 'Hi' back."}
            ],
            max_tokens=5,
            temperature=0.1
        )
        
        result = response.choices[0].message.content
        print(f"✅ Groq API successful! Response: '{result}'")
        return True
        
    except Exception as e:
        print(f"❌ Groq API error: {type(e).__name__}: {e}")
        
        # Additional debug info
        import traceback
        print("Full error traceback:")
        traceback.print_exc()
        
        return False

if __name__ == "__main__":
    test_groq()
