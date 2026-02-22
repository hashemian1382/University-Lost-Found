# DeepSeek AI Setup Guide

This project now uses **DeepSeek AI** - a fast, affordable, and powerful AI API.

## Why DeepSeek?

- ✅ **Affordable** - Very competitive pricing
- ✅ **Fast** - Quick response times
- ✅ **Compatible** - OpenAI-compatible API
- ✅ **No SSL Issues** - Works perfectly with Python 3.14!
- ✅ **High Quality** - Excellent performance on various tasks
- ✅ **Easy Integration** - Simple setup with OpenAI library

## Getting Started

### 1. Get Your API Key

1. Visit: **https://platform.deepseek.com**
2. Sign up or log in
3. Navigate to **API Keys** section: https://platform.deepseek.com/api_keys
4. Click **"Create API Key"**
5. Copy your API key

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This will install the OpenAI library which DeepSeek uses.

### 3. Configure Your API Key

Edit your `.env` file in the `backend/` directory:

```env
DEEPSEEK_API_KEY=sk-your-api-key-here
USE_MOCK_AI=false
```

### 4. Test the Integration

#### Quick Test (Django Integration)
```bash
cd backend
python core/test_openai.py
```

#### Detailed Test (Direct API)
```bash
cd backend
python core/test_deepseek_direct.py
```

The detailed test provides extensive logging and troubleshooting information.

## Features

### Model Used
- **deepseek-chat** - Main conversational model
- Fast inference
- Excellent at structured data extraction
- JSON mode support

### API Capabilities
- Text generation
- JSON-structured responses
- Chat conversations
- System prompts
- Temperature control
- Token usage tracking

## Mock Mode (Optional)

For testing without API calls, enable mock mode:

```env
USE_MOCK_AI=true
```

Mock mode:
- Works offline
- No API costs
- Great for development
- Uses keyword-based extraction

## Pricing

DeepSeek offers very competitive pricing:
- Generally cheaper than OpenAI
- Pay-as-you-go model
- No subscription required
- Check latest pricing at: https://platform.deepseek.com/pricing

## Usage Limits

- Generous rate limits
- Scales with your usage
- No hard daily caps on paid tier
- Check your dashboard for current limits

## Code Structure

### Main Service
`backend/core/ai_service.py` - ChatBotService class

Key features:
- Automatic retry logic
- Error handling
- Mock mode support
- JSON response parsing
- Data validation

### Test Files
- `core/test_openai.py` - Integration test with Django
- `core/test_deepseek_direct.py` - Direct API test with detailed logging

## Configuration Options

In your `.env` file:

```env
# Required
DEEPSEEK_API_KEY=your-api-key-here

# Optional - set to 'true' for testing without API
USE_MOCK_AI=false
```

## Troubleshooting

### API Key Issues

**Error: "DEEPSEEK_API_KEY environment variable is not set"**

Solution:
1. Check `.env` file exists in `backend/` directory
2. Verify the key is set: `DEEPSEEK_API_KEY=sk-...`
3. Restart your Django server after updating `.env`

### Authentication Errors

**Error: "401 Unauthorized" or "403 Forbidden"**

Solutions:
1. Verify your API key is correct
2. Check it hasn't expired
3. Ensure you have credit/valid payment method
4. Get a new key at: https://platform.deepseek.com/api_keys

### Connection Errors

**Error: Network/timeout errors**

Solutions:
1. Check your internet connection
2. Verify firewall isn't blocking HTTPS
3. Try the direct test: `python core/test_deepseek_direct.py`
4. Enable mock mode temporarily: `USE_MOCK_AI=true`

### Rate Limits

**Error: "429 Too Many Requests"**

Solutions:
1. Wait a moment before retrying
2. Check your rate limits in DeepSeek dashboard
3. Consider upgrading your plan if needed

### SSL Issues (Python 3.14)

Good news: DeepSeek works great with Python 3.14! The OpenAI library handles SSL properly.

If you do encounter SSL issues:
1. Update OpenSSL: `brew upgrade openssl@3`
2. Reinstall openai: `pip install --upgrade openai`
3. Check certificates: `pip install --upgrade certifi`

## API Response Format

The service extracts structured data from natural language:

**Input:**
```
"I lost my blue iPhone 13 near the library"
```

**Output:**
```json
{
  "success": true,
  "data": {
    "type": "LOST",
    "title": "iPhone 13 - Blue",
    "description": "iPhone 13 in blue color",
    "location_description": "Near the library",
    "latitude": null,
    "longitude": null,
    "tags": ["Electronics"]
  }
}
```

## Customization

### Adjust Temperature
In `ai_service.py`, change `temperature` value:
- Lower (0.1-0.3): More focused, deterministic
- Higher (0.7-1.0): More creative, varied

### Modify System Prompt
Edit `_create_system_prompt()` method to:
- Add more instructions
- Change output format
- Add new fields
- Customize behavior

### Add New Tags
Update `self.available_tags` list in `__init__()` method

## Production Deployment

For production:

1. **Secure Your API Key**
   - Use environment variables (not hardcoded)
   - Rotate keys regularly
   - Never commit to git

2. **Monitor Usage**
   - Track API calls
   - Set up alerts
   - Monitor token usage

3. **Handle Errors Gracefully**
   - Implement fallbacks
   - Log errors properly
   - Show user-friendly messages

4. **Optimize Costs**
   - Cache common responses
   - Use appropriate temperature
   - Limit max_tokens when possible

## Support & Resources

- **DeepSeek Platform**: https://platform.deepseek.com
- **API Documentation**: https://platform.deepseek.com/docs
- **Pricing**: https://platform.deepseek.com/pricing
- **Status Page**: Check for service updates

## Comparison with Other Providers

### DeepSeek vs OpenAI
- ✅ More affordable
- ✅ Faster response times
- ✅ OpenAI-compatible
- ✅ Good performance
- ⚠️  Newer platform

### DeepSeek vs Gemini
- ✅ Works with Python 3.14 (no SSL issues!)
- ✅ OpenAI-compatible API
- ✅ Simpler integration
- ✅ Better pricing

## Next Steps

1. ✅ Get your API key from DeepSeek
2. ✅ Add it to your `.env` file
3. ✅ Run the test: `python core/test_deepseek_direct.py`
4. ✅ Start building with AI powered features!

Your Lost & Found app now has intelligent item extraction powered by DeepSeek AI! 🚀
