#!/usr/bin/env python3
"""
Test available Groq models and update our configuration
"""

import os
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_available_models():
    """Test which Groq models are available"""
    print("🤖 Testing available Groq models...")
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ No GROQ_API_KEY found")
        return False
    
    try:
        from groq import Groq
        
        # Create HTTP client with SSL verification disabled
        http_client = httpx.Client(verify=False)
        
        # Create client
        client = Groq(
            api_key=api_key,
            http_client=http_client
        )
        
        # Test different Llama models
        models_to_test = [
            "llama3-8b-8192",
            "llama3-70b-8192", 
            "llama-3.1-8b-instant",
            "llama-3.1-70b-versatile",
            "llama-3.2-1b-preview",
            "llama-3.2-3b-preview",
            "mixtral-8x7b-32768",
            "gemma-7b-it"
        ]
        
        working_models = []
        
        for model in models_to_test:
            try:
                print(f"🔄 Testing model: {model}")
                
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": "Hello! Just say 'Hi' back."}
                    ],
                    max_tokens=5,
                    temperature=0.1
                )
                
                result = response.choices[0].message.content
                print(f"✅ {model} works! Response: '{result}'")
                working_models.append(model)
                break  # Found a working model, use it
                
            except Exception as e:
                print(f"❌ {model} failed: {str(e)[:100]}...")
                continue
        
        # Close the HTTP client
        http_client.close()
        
        if working_models:
            print(f"\n✅ Working models found: {working_models}")
            return working_models[0]  # Return the first working model
        else:
            print("\n❌ No working models found")
            return None
            
    except Exception as e:
        print(f"❌ Error testing models: {e}")
        return None

if __name__ == "__main__":
    working_model = test_available_models()
    if working_model:
        print(f"\n🎯 Recommended model to use: {working_model}")
    else:
        print("\n❌ Could not find a working model")
