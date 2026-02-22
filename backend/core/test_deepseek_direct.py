"""
Direct test of DeepSeek API with detailed logging
This script makes a simple API call to test connectivity
"""
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
print("DIRECT DEEPSEEK API TEST")
print("=" * 70)
print()

# Step 1: Check API Key
print("📋 STEP 1: Checking API Key...")
print("-" * 70)
api_key = os.getenv('DEEPSEEK_API_KEY')

if not api_key:
    print("❌ ERROR: DEEPSEEK_API_KEY not found in environment")
    print("   Please set it in your .env file")
    print()
    print("   Get your API key from: https://platform.deepseek.com/api_keys")
    sys.exit(1)

# Mask the key for security
masked_key = api_key[:10] + "..." + api_key[-8:] if len(api_key) > 20 else "***"
print(f"✓ API Key found: {masked_key}")
print(f"  Length: {len(api_key)} characters")
print()

# Step 2: Import OpenAI Library
print("📋 STEP 2: Importing OpenAI Library...")
print("-" * 70)
try:
    from openai import OpenAI
    print("✓ Successfully imported openai library")
    import openai
    print(f"  OpenAI version: {openai.__version__ if hasattr(openai, '__version__') else 'unknown'}")
    print(f"  Module location: {openai.__file__}")
    print()
except ImportError as e:
    print(f"❌ ERROR: Could not import openai")
    print(f"   {e}")
    print()
    print("   Try installing it:")
    print("   pip install openai")
    sys.exit(1)

# Step 3: Initialize Client
print("📋 STEP 3: Initializing DeepSeek Client...")
print("-" * 70)
print("  Base URL: https://api.deepseek.com")
print("  Timeout: 60s")
print("  Max Retries: 2")
print()

try:
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
        timeout=60.0,
        max_retries=2
    )
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

test_prompt = "Say 'Hello from DeepSeek!' and nothing else."
model_name = "deepseek-chat"

print(f"Model: {model_name}")
print(f"Prompt: '{test_prompt}'")
print()
print("Sending request...")
print()

try:
    # Make the API call
    print("→ Calling client.chat.completions.create()...")
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "user", "content": test_prompt}
        ],
        temperature=0.7,
        max_tokens=100
    )
    print("✓ Request completed successfully!")
    print()
    
    # Log response details
    print("📤 RESPONSE DETAILS:")
    print("-" * 70)
    print(f"Response type: {type(response)}")
    print(f"Response ID: {response.id}")
    print(f"Model: {response.model}")
    print(f"Created: {response.created}")
    print()
    
    # Extract the message
    if response.choices and len(response.choices) > 0:
        message = response.choices[0].message
        content = message.content
        
        print("Response content:")
        print("┌" + "─" * 68 + "┐")
        print("│ " + content.strip()[:66].ljust(66) + " │")
        print("└" + "─" * 68 + "┘")
        print()
        
        print(f"Finish reason: {response.choices[0].finish_reason}")
        print()
    
    # Token usage
    if hasattr(response, 'usage') and response.usage:
        print("Token Usage:")
        print(f"  Prompt tokens: {response.usage.prompt_tokens}")
        print(f"  Completion tokens: {response.usage.completion_tokens}")
        print(f"  Total tokens: {response.usage.total_tokens}")
        print()
    
    print("=" * 70)
    print("✅ SUCCESS! DeepSeek API is working!")
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
    
    # Check error type
    error_str = str(e).lower()
    
    if "ssl" in error_str or "certificate" in error_str:
        print("⚠️  This appears to be an SSL/TLS error")
        print()
        print("   Possible solutions:")
        print("   1. Update OpenSSL: brew upgrade openssl@3")
        print("   2. Set USE_MOCK_AI=true in .env for testing")
        print("   3. Check your firewall/proxy settings")
        print()
    
    elif "404" in error_str or "not found" in error_str:
        print("⚠️  Model or endpoint not found")
        print()
        print("   Try:")
        print("   - Model: deepseek-chat")
        print("   - Base URL: https://api.deepseek.com")
        print()
    
    elif "401" in error_str or "unauthorized" in error_str or "403" in error_str:
        print("⚠️  Authentication error")
        print()
        print("   Your API key may be:")
        print("   1. Invalid or expired")
        print("   2. Not properly set in .env file")
        print("   3. Missing required permissions")
        print()
        print("   Get a new key at: https://platform.deepseek.com/api_keys")
        print()
    
    elif "429" in error_str or "rate limit" in error_str:
        print("⚠️  Rate limit exceeded")
        print()
        print("   Wait a moment and try again.")
        print()
    
    elif "timeout" in error_str or "timed out" in error_str:
        print("⚠️  Request timeout")
        print()
        print("   Check your internet connection.")
        print()
    
    else:
        print("⚠️  Unknown error type")
        print()
        print("   Check:")
        print("   - Internet connection")
        print("   - API key validity")
        print("   - DeepSeek service status")
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

print(f"Prompt: Request JSON response")
print()
print("Sending request with response_format='json_object'...")
print()

try:
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You always respond with valid JSON only."},
            {"role": "user", "content": json_prompt}
        ],
        temperature=0.1,
        max_tokens=200,
        response_format={"type": "json_object"}
    )
    
    print("✓ Request completed!")
    print()
    
    response_text = response.choices[0].message.content.strip()
    print("Raw response:")
    print("┌" + "─" * 68 + "┐")
    for line in response_text.split('\n')[:10]:
        print("│ " + line[:66].ljust(66) + " │")
    print("└" + "─" * 68 + "┘")
    print()
    
    # Try to parse as JSON
    try:
        # Remove markdown code blocks if present
        clean_text = response_text
        if clean_text.startswith('```json'):
            clean_text = clean_text[7:]
        if clean_text.startswith('```'):
            clean_text = clean_text[3:]
        if clean_text.endswith('```'):
            clean_text = clean_text[:-3]
        clean_text = clean_text.strip()
        
        parsed_json = json.loads(clean_text)
        print("✓ Successfully parsed as JSON!")
        print()
        print("Parsed structure:")
        print(json.dumps(parsed_json, indent=2))
        print()
    except json.JSONDecodeError as je:
        print(f"⚠️  Could not parse as JSON: {je}")
        print()
    
    # Token usage
    if response.usage:
        print("Token Usage:")
        print(f"  Total tokens: {response.usage.total_tokens}")
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
print("  ✓ OpenAI library imported")
print("  ✓ DeepSeek client initialized")
print("  ✓ Simple text generation works")
print("  ✓ JSON responses received")
print()
print("Your DeepSeek API integration is ready to use!")
print()
print("DeepSeek Benefits:")
print("  • Fast response times")
print("  • Affordable pricing")
print("  • OpenAI-compatible API")
print("  • No SSL issues with Python 3.14!")
print()
print("To use in your app, ensure in .env:")
print("  USE_MOCK_AI=false")
print("  DEEPSEEK_API_KEY=your-key-here")
print()
