"""
Test script to verify OpenAI API connection
Run this script to test if your API key is configured correctly
"""
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lost_found_project.settings')

import django
django.setup()

from core.ai_service import ChatBotService


def test_openai_connection():
    """Test OpenAI API connection and functionality"""
    
    print("=" * 60)
    print("OpenAI API Connection Test")
    print("=" * 60)
    print()
    
    # Check if API key is set
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ FAILED: OPENAI_API_KEY environment variable is not set")
        print()
        print("Please set your API key in the .env file:")
        print("OPENAI_API_KEY=sk-your-api-key-here")
        return False
    
    # Mask API key for security
    masked_key = api_key[:7] + "..." + api_key[-4:] if len(api_key) > 11 else "***"
    print(f"✓ API Key found: {masked_key}")
    print()
    
    # Test 1: Initialize service
    print("Test 1: Initializing ChatBotService...")
    try:
        service = ChatBotService()
        print("✓ Service initialized successfully")
        print()
    except Exception as e:
        print(f"❌ FAILED: Could not initialize service")
        print(f"   Error: {e}")
        return False
    
    # Test 2: Simple extraction test
    print("Test 2: Testing item extraction...")
    test_description = "I lost my blue iPhone 13 near the library yesterday. It has a cracked screen."
    
    try:
        print(f"   Input: '{test_description}'")
        print("   Processing...")
        
        result = service.extract_item_info(test_description)
        
        if not result['success']:
            print(f"❌ FAILED: Extraction failed")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return False
        
        print("✓ Extraction successful!")
        print()
        print("Extracted Information:")
        print("-" * 60)
        
        data = result['data']
        print(f"Type:        {data['type']}")
        print(f"Title:       {data['title']}")
        print(f"Description: {data['description']}")
        print(f"Location:    {data['location_description']}")
        print(f"Coordinates: {data['latitude']}, {data['longitude']}")
        print(f"Tags:        {', '.join(data['tags'])}")
        print()
        
    except Exception as e:
        print(f"❌ FAILED: Error during extraction")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Another test with found item
    print("Test 3: Testing with a 'found' item...")
    test_description_2 = "I found a black wallet in the cafeteria. It contains some credit cards."
    
    try:
        print(f"   Input: '{test_description_2}'")
        print("   Processing...")
        
        result = service.extract_item_info(test_description_2)
        
        if not result['success']:
            print(f"❌ FAILED: Extraction failed")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return False
        
        data = result['data']
        print(f"✓ Type detected: {data['type']}")
        print(f"✓ Tags assigned: {', '.join(data['tags'])}")
        print()
        
    except Exception as e:
        print(f"❌ FAILED: Error during second test")
        print(f"   Error: {e}")
        return False
    
    # All tests passed
    print("=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print()
    print("Your OpenAI API is configured correctly and working!")
    print("You can now use the chatbot feature in your application.")
    print()
    return True


if __name__ == "__main__":
    try:
        success = test_openai_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
