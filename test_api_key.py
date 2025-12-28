"""
Quick test to verify which API key is being used and if it works
"""
import os
from dotenv import load_dotenv
from google import genai

# Force reload .env
load_dotenv(override=True)

api_key = os.getenv("GEMINI_API_KEY")
print(f"✅ API Key loaded: {api_key[:20]}...")
print(f"   Full key starts with: {api_key[:15]}")

try:
    client = genai.Client(api_key=api_key)
    print("✅ Client initialized")
    
    # Try a simple request
    response = client.models.generate_content(
        model='models/gemini-flash-latest',
        contents='Say "Hello! API key is working!" in one short sentence.'
    )
    
    print(f"✅ Response: {response.text}")
    print("\n🎉 API KEY IS WORKING!")
    
except Exception as e:
    error_msg = str(e)
    print(f"❌ Error: {error_msg}")
    
    if "429" in error_msg or "quota" in error_msg.lower():
        print("\n⚠️  QUOTA EXCEEDED!")
        print("This API key has also reached its limit.")
        print("\nSolutions:")
        print("1. Wait 30-60 minutes")
        print("2. Get a new API key from: https://aistudio.google.com/apikey")
        print("3. Check your usage at: https://aistudio.google.com/apikey")
    else:
        print(f"\n❌ Different error: {error_msg}")
