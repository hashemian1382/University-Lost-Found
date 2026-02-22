# Google Gemini AI Setup Guide

This project uses **Google's Gemini AI** which offers a **FREE tier** with generous limits.

## ⚠️ Python 3.14 SSL Issue

If you're using Python 3.14 on macOS, you may encounter SSL errors when connecting to Google's API. This is a known issue with Python 3.14 and OpenSSL on macOS.

### Quick Solution: Use Mock Mode

We've implemented a **mock AI mode** that simulates AI responses for testing and development:

**In your `.env` file:**
```env
USE_MOCK_AI=true
```

This allows you to:
- ✅ Test the application without API calls
- ✅ Develop features offline
- ✅ Avoid SSL errors with Python 3.14
- ✅ Work without internet connection

The mock mode uses simple keyword matching to simulate AI extraction and works perfectly for development!

### To Use Real AI (when SSL is fixed):

Set in your `.env` file:
```env
USE_MOCK_AI=false
```

## Getting Your Free API Key

1. Visit **Google AI Studio**: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click **"Get API Key"** or **"Create API Key"**
4. Copy your API key

## Setting Up Your Project

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Your API Key

Edit your `.env` file:

```env
GEMINI_API_KEY=your-api-key-here
USE_MOCK_AI=true  # Set to 'false' to use real API
```

### 3. Test the Connection

Run the test script:

```bash
python core/test_openai.py
```

## Why Gemini?

- ✅ **FREE Tier Available** - No credit card required
- ✅ **Generous Limits** - 60 requests per minute on free tier
- ✅ **High Quality** - Comparable to GPT-3.5/GPT-4
- ✅ **Fast Response** - Quick inference times
- ✅ **Easy Integration** - Simple Python SDK

## Free Tier Limits

- **60 requests per minute**
- **1,500 requests per day** (free tier)
- No credit card required
- Perfect for development and moderate production use

## Model Used

This project uses **gemini-1.5-flash** which is:
- Fast and efficient
- Great for structured data extraction
- Available on the free tier
- Supports JSON output

## Mock Mode Features

When `USE_MOCK_AI=true`, the system uses keyword-based extraction:

**Supported Items:**
- Electronics (phone, laptop, etc.)
- Wallets and purses
- Keys
- ID Cards
- Books
- Bags
- Accessories
- And more...

**Supported Locations:**
- Library
- Cafeteria
- Classroom
- Gym
- And general descriptions

## Fixing Python 3.14 SSL Issues

If you want to use the real API with Python 3.14, try these solutions:

### Option 1: Upgrade OpenSSL (Recommended)

```bash
# On macOS with Homebrew
brew update
brew upgrade openssl@3
```

Then reinstall Python:
```bash
brew reinstall python@3.14
```

### Option 2: Downgrade Python

Use Python 3.11 or 3.12 which have better SSL stability:

```bash
brew install python@3.12
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Option 3: Use System Python Certificates

Run this command:
```bash
/Applications/Python\ 3.14/Install\ Certificates.command
```

## Troubleshooting

### SSL Errors
- **Solution**: Set `USE_MOCK_AI=true` in `.env`
- Or try the SSL fixes above

### Mock Mode Not Working
- Check that `.env` has `USE_MOCK_AI=true`
- Restart your Django server

### API Not Responding
- Check your internet connection
- Verify your API key is correct
- Check you haven't exceeded free tier limits

### Want Better Mock Responses?
- Edit `_mock_extract_item_info()` in `core/ai_service.py`
- Add more keywords and categories
- Customize the output format

## Production Deployment

For production, you should:
1. Set `USE_MOCK_AI=false`
2. Ensure SSL certificates are properly configured
3. Consider upgrading to Python 3.12 if SSL issues persist
4. Monitor your API usage to stay within free tier limits

## Support

- **Google AI Documentation**: https://ai.google.dev/
- **Python SSL Issues**: https://github.com/python/cpython/issues
- **Gemini API Status**: https://status.cloud.google.com/
