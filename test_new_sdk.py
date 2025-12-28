"""
Quick test to verify the new Google GenAI SDK works
"""
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key found: {api_key[:20]}...")

try:
    client = genai.Client(api_key=api_key)
    print("✅ Client initialized successfully!")
    
    response = client.models.generate_content(
        model='models/gemini-flash-latest',
        contents='Say "Hello! I am working!" in one sentence.'
    )
    
    print(f"✅ Response: {response.text}")
    print("\n🎉 Everything is working! The backend should work now.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    if "429" in str(e) or "quota" in str(e).lower():
        print("\n⚠️  Quota exceeded - wait 30-60 minutes and try again")
    else:
        print("\n❌ There's an issue with the API key or connection")
