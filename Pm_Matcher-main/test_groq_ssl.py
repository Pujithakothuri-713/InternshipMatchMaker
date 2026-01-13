#!/usr/bin/env python3
"""
Groq API test with SSL handling
"""

import os
import ssl
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_groq_with_ssl_fix():
    """Test Groq API with SSL certificate verification disabled"""
    print("🤖 Testing Groq API with SSL fix...")
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ No GROQ_API_KEY found")
        return False
    
    print(f"✅ API Key loaded: {api_key[:20]}...")
    
    try:
        from groq import Groq
        print("✅ Groq module imported successfully")
        
        # Create HTTP client with SSL verification disabled
        http_client = httpx.Client(verify=False)
        
        # Create client with custom HTTP client
        client = Groq(
            api_key=api_key,
            http_client=http_client
        )
        print("✅ Groq client created with SSL bypass")
        
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
        
        # Close the HTTP client
        http_client.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Groq API error: {type(e).__name__}: {e}")
        return False

def test_network_connectivity():
    """Test basic network connectivity to Groq"""
    print("\n🌐 Testing network connectivity...")
    
    try:
        import requests
        from urllib3.exceptions import InsecureRequestWarning
        import urllib3
        
        # Disable SSL warnings for this test
        urllib3.disable_warnings(InsecureRequestWarning)
        
        # Test basic connectivity
        response = requests.get("https://api.groq.com", verify=False, timeout=10)
        print(f"✅ Network connectivity OK. Status: {response.status_code}")
        return True
        
    except Exception as e:
        print(f"❌ Network connectivity failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Groq API SSL Debug Test")
    print("=" * 40)
    
    # Test network first
    if test_network_connectivity():
        # Test Groq API
        test_groq_with_ssl_fix()
    else:
        print("❌ Network connectivity failed, skipping API test")
