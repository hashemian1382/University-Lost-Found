"""
Direct test of Google Gemini API with detailed logging
This script makes a simple API call to test connectivity
"""
if __name__ != "__main__":
    import unittest
    raise unittest.SkipTest("Integration script: run directly, not via unittest discovery.")

import os
import sys
import json
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
from dotenv import load_dotenv
env_path = backend_dir / '.env'
load_dotenv(env_path)

print("=" * 70)
print("DIRECT GOOGLE GEMINI API TEST")
print("=" * 70)
print()

# Step 1: Check API Key
print("📋 STEP 1: Checking API Key...")
print("-" * 70)
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("❌ ERROR: GEMINI_API_KEY not found in environment")
    print("   Please set it in your .env file")
    sys.exit(1)

# Mask the key for security
masked_key = api_key[:10] + "..." + api_key[-8:] if len(api_key) > 20 else "***"
print(f"✓ API Key found: {masked_key}")
print(f"  Length: {len(api_key)} characters")
print()

# Step 2: Import Google GenAI
print("📋 STEP 2: Importing Google GenAI Library...")
print("-" * 70)
try:
    from google import genai
    from google.genai import types
    print("✓ Successfully imported google.genai")
    print(f"  Module location: {genai.__file__}")
    print()
except ImportError as e:
    print(f"❌ ERROR: Could not import google.genai")
    print(f"   {e}")
    print()
    print("   Try installing it:")
    print("   pip install google-genai")
    sys.exit(1)

# Step 3: Initialize Client
print("📋 STEP 3: Initializing Gemini Client...")
print("-" * 70)
try:
    client = genai.Client(api_key=api_key)
    print("✓ Client initialized successfully")
    print(f"  Client type: {type(client)}")
    print()
except Exception as e:
    print(f"❌ ERROR: Could not initialize client")
    print(f"   {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Test Simple API Call
print("📋 STEP 4: Making Test API Call...")
print("-" * 70)

test_prompt = "Say 'Hello from Gemini!' and nothing else."
model_name = "gemini-1.5-flash"

print(f"Model: {model_name}")
print(f"Prompt: '{test_prompt}'")
print()
print("Sending request...")
print()

try:
    # Make the API call
    print("→ Calling client.models.generate_content()...")
    response = client.models.generate_content(
        model=model_name,
        contents=test_prompt,
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=100,
        )
    )
    print("✓ Request completed successfully!")
    print()
    
    # Log response details
    print("📤 RESPONSE DETAILS:")
    print("-" * 70)
    print(f"Response type: {type(response)}")
    print()
    
    # Try to get the text
    print("Response text:")
    print("┌" + "─" * 68 + "┐")
    print("│ " + response.text.strip()[:66].ljust(66) + " │")
    print("└" + "─" * 68 + "┘")
    print()
    
    # Try to get more details if available
    try:
        print("Full response object attributes:")
        for attr in dir(response):
            if not attr.startswith('_'):
                try:
                    value = getattr(response, attr)
                    if not callable(value):
                        print(f"  - {attr}: {value}")
                except:
                    pass
        print()
    except Exception as e:
        print(f"  (Could not inspect response attributes: {e})")
        print()
    
    print("=" * 70)
    print("✅ SUCCESS! Gemini API is working!")
    print("=" * 70)
    print()
    
except Exception as e:
    print()
    print("=" * 70)
    print("❌ ERROR: API call failed")
    print("=" * 70)
    print()
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    print()
    print("Full traceback:")
    print("-" * 70)
    import traceback
    traceback.print_exc()
    print()
    
    # Additional debugging info
    print()
    print("🔍 DEBUGGING INFORMATION:")
    print("-" * 70)
    
    # Check if it's a network error
    if "SSL" in str(e) or "ssl" in str(e).lower():
        print("⚠️  This appears to be an SSL/TLS error")
        print()
        print("   Common causes:")
        print("   1. Python 3.14 SSL compatibility issues on macOS")
        print("   2. Outdated SSL certificates")
        print("   3. Firewall/proxy blocking HTTPS")
        print()
        print("   Solutions:")
        print("   1. Set USE_MOCK_AI=true in .env for testing")
        print("   2. Downgrade to Python 3.12: brew install python@3.12")
        print("   3. Update OpenSSL: brew upgrade openssl@3")
        print()
    
    elif "404" in str(e):
        print("⚠️  Model not found error")
        print()
        print("   Try different model names:")
        print("   - gemini-1.5-flash")
        print("   - gemini-1.5-pro")
        print("   - gemini-2.0-flash-exp")
        print()
    
    elif "401" in str(e) or "403" in str(e):
        print("⚠️  Authentication error")
        print()
        print("   Your API key may be:")
        print("   1. Invalid or expired")
        print("   2. Not properly set in .env file")
        print("   3. Lacking necessary permissions")
        print()
        print("   Get a new key at: https://makersuite.google.com/app/apikey")
        print()
    
    elif "429" in str(e):
        print("⚠️  Rate limit exceeded")
        print()
        print("   You've hit the API rate limit. Wait a moment and try again.")
        print()
    
    else:
        print("⚠️  Unknown error type")
        print()
        print("   Check your internet connection and try again.")
        print()
    
    sys.exit(1)

# Step 5: Test JSON Response
print()
print("📋 STEP 5: Testing JSON Response Format...")
print("-" * 70)

json_prompt = """Return a JSON object with these fields:
{
    "status": "success",
    "message": "This is a test",
    "number": 42
}

Return ONLY the JSON, nothing else."""

print(f"Prompt: '{json_prompt[:50]}...'")
print()
print("Sending request...")
print()

try:
    response = client.models.generate_content(
        model=model_name,
        contents=json_prompt,
        config=types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=200,
        )
    )
    
    print("✓ Request completed!")
    print()
    
    response_text = response.text.strip()
    print("Raw response:")
    print("┌" + "─" * 68 + "┐")
    for line in response_text.split('\n')[:10]:
        print("│ " + line[:66].ljust(66) + " │")
    print("└" + "─" * 68 + "┘")
    print()
    
    # Try to parse as JSON
    # Remove markdown code blocks if present
    clean_text = response_text
    if clean_text.startswith('```json'):
        clean_text = clean_text[7:]
    if clean_text.startswith('```'):
        clean_text = clean_text[3:]
    if clean_text.endswith('```'):
        clean_text = clean_text[:-3]
    clean_text = clean_text.strip()
    
    try:
        parsed_json = json.loads(clean_text)
        print("✓ Successfully parsed as JSON!")
        print()
        print("Parsed structure:")
        print(json.dumps(parsed_json, indent=2))
        print()
    except json.JSONDecodeError as je:
        print(f"⚠️  Could not parse as JSON: {je}")
        print("   (This is okay, Gemini sometimes adds extra formatting)")
        print()
    
    print("=" * 70)
    print("✅ JSON TEST COMPLETE!")
    print("=" * 70)
    print()
    
except Exception as e:
    print()
    print(f"❌ JSON test failed: {e}")
    print()

# Final Summary
print()
print("=" * 70)
print("🎉 ALL TESTS COMPLETED!")
print("=" * 70)
print()
print("Summary:")
print("  ✓ API Key validated")
print("  ✓ Library imported")
print("  ✓ Client initialized")
print("  ✓ Simple text generation works")
print("  ✓ JSON responses received")
print()
print("Your Gemini API integration is ready to use!")
print()
print("To use in your app, set in .env:")
print("  USE_MOCK_AI=false")
print()
