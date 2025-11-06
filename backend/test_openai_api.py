"""Test script for checking OpenAI API connectivity and functionality.

This script verifies that:
1. OpenAI API key is configured
2. The API key is valid
3. The configured model is accessible
4. A simple API call works
"""

import os
import sys
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai import OpenAIError

# Load environment variables
load_dotenv()

def check_environment_variables():
    """Check if required environment variables are set."""
    required_vars = ['OPENAI_API_KEY', 'OPENAI_MODEL', 'OPENAI_MAX_TOKENS']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("[ERROR] Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set the required environment variables in your .env file.")
        return False
    
    print("[OK] All required environment variables are set")
    return True

def print_configuration():
    """Print current OpenAI configuration."""
    api_key = os.getenv('OPENAI_API_KEY', '')
    model = os.getenv('OPENAI_MODEL', '')
    max_tokens = os.getenv('OPENAI_MAX_TOKENS', '')
    
    # Mask API key for security
    masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
    
    print("\n[CONFIG] Current Configuration:")
    print(f"  API Key: {masked_key}")
    print(f"  Model: {model}")
    print(f"  Max Tokens: {max_tokens}")
    print()

async def test_openai_api():
    """Test OpenAI API with a simple request."""
    api_key = os.getenv('OPENAI_API_KEY')
    model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '500'))
    
    try:
        print("[TEST] Testing OpenAI API connection...")
        client = AsyncOpenAI(api_key=api_key)
        
        # Test 1: Simple completion
        print("  Test 1: Simple API call...")
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": "Say 'Hello, OpenAI API is working!' and nothing else."
                }
            ],
            max_tokens=50,
            temperature=0.7
        )
        
        if response and response.choices:
            content = response.choices[0].message.content
            print(f"  [OK] API call successful!")
            print(f"  Response: {content}")
        else:
            print("  [ERROR] API call returned empty response")
            return False
        
        # Test 2: JSON mode (if supported)
        json_mode_models = ["gpt-3.5-turbo-1106", "gpt-4-turbo-preview", "gpt-4-0125-preview", "gpt-4o", "gpt-4o-mini"]
        supports_json_mode = any(model_name in model.lower() for model_name in json_mode_models)
        
        if supports_json_mode:
            print("\n  Test 2: JSON mode support...")
            try:
                response = await client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant. Respond with valid JSON only."
                        },
                        {
                            "role": "user",
                            "content": 'Return JSON: {"status": "ok", "message": "JSON mode works"}'
                        }
                    ],
                    max_tokens=100,
                    temperature=0.7,
                    response_format={"type": "json_object"}
                )
                
                if response and response.choices:
                    content = response.choices[0].message.content
                    print(f"  [OK] JSON mode works!")
                    print(f"  Response: {content}")
                else:
                    print("  [WARNING] JSON mode test returned empty response")
            except Exception as json_error:
                print(f"  [WARNING] JSON mode not working: {json_error}")
        else:
            print(f"\n  [INFO] Model {model} may not support JSON mode (this is OK)")
        
        # Test 3: Email generation simulation
        print("\n  Test 3: Email generation simulation...")
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional real estate agent assistant."
                },
                {
                    "role": "user",
                    "content": """Generate a short follow-up email. Return JSON:
{
  "subject": "Brief subject line",
  "body": "Email body text"
}"""
                }
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        if response and response.choices:
            content = response.choices[0].message.content
            print(f"  [OK] Email generation test successful!")
            print(f"  Response preview: {content[:200]}...")
        else:
            print("  [ERROR] Email generation test returned empty response")
            return False
        
        print("\n[SUCCESS] All tests passed! OpenAI API is working correctly.")
        return True
        
    except OpenAIError as e:
        error_type = type(e).__name__
        error_msg = str(e)
        print(f"\n[ERROR] OpenAI API Error ({error_type}): {error_msg}")
        
        if "authentication" in error_msg.lower() or "401" in error_msg or "invalid" in error_msg.lower():
            print("\n[TIP] This looks like an authentication error.")
            print("      Please check that your OPENAI_API_KEY is correct.")
        elif "rate_limit" in error_msg.lower() or "429" in error_msg:
            print("\n[TIP] You've hit the rate limit.")
            print("      Please wait a moment and try again.")
        elif "model" in error_msg.lower() or "not found" in error_msg.lower():
            print(f"\n[TIP] The model '{model}' may not be available.")
            print("      Please check that the model name is correct and you have access to it.")
        elif "insufficient_quota" in error_msg.lower():
            print("\n[TIP] You've exceeded your OpenAI API quota.")
            print("      Please check your OpenAI account billing.")
        
        return False
        
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        print(f"\n[ERROR] Unexpected error ({error_type}): {error_msg}")
        print("\n[TIP] Please check your internet connection and try again.")
        return False

async def main():
    """Main test function."""
    print("=" * 60)
    print("OpenAI API Test Script")
    print("=" * 60)
    print()
    
    # Check environment variables
    if not check_environment_variables():
        sys.exit(1)
    
    # Print configuration
    print_configuration()
    
    # Test API
    success = await test_openai_api()
    
    print()
    print("=" * 60)
    if success:
        print("[SUCCESS] Test Result: PASSED")
        print("Your OpenAI API is configured correctly and working!")
    else:
        print("[FAILED] Test Result: FAILED")
        print("Please fix the issues above and try again.")
    print("=" * 60)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

