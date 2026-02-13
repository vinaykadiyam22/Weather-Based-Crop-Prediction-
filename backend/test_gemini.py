"""
Test script to verify Gemini API connectivity.
Run: python test_gemini.py
"""
import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY", "")
print(f"API Key loaded: {'Yes' if API_KEY else 'No'}")
print(f"Key length: {len(API_KEY) if API_KEY else 0}")
print()

if not API_KEY:
    print("ERROR: GEMINI_API_KEY not found in .env")
    exit(1)

try:
    import google.generativeai as genai
    genai.configure(api_key=API_KEY)
    
    # List available models
    print("Available models for your API key:")
    models = list(genai.list_models())
    for m in models:
        if "generateContent" in (m.supported_generation_methods or []):
            print(f"  - {m.name}")
    print()
    
    # Try models (order: prefer models with quota)
    models_to_try = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-2.0-flash", "gemini-pro-latest"]
    
    for model_name in models_to_try:
        print(f"Trying model: {model_name}...")
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say hello in one word.")
            print(f"  SUCCESS: {response.text.strip()}")
            print(f"\nWorking model: {model_name}")
            exit(0)
        except Exception as e:
            print(f"  FAILED: {e}")
    
    print("\nAll models failed. Check your API key at https://aistudio.google.com/apikey")
    
except ImportError as e:
    print(f"ERROR: {e}")
    print("Run: pip install google-generativeai")
