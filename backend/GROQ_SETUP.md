# Groq AI Setup Guide

This project uses **Groq** - the world's fastest AI inference with a **TRULY FREE TIER**!

## 🎉 Why Groq?

- ✅ **100% FREE** - No credit card required!
- ✅ **BLAZING FAST** - Fastest AI inference in the market
- ✅ **Generous Limits** - 30 req/min, 14,400 tokens/min free
- ✅ **No SSL Issues** - Works perfectly with Python 3.14!
- ✅ **OpenAI Compatible** - Easy integration
- ✅ **High Quality** - Powered by Meta's Llama models

## Getting Started (5 Minutes!)

### 1. Get Your FREE API Key

1. Visit: **https://console.groq.com**
2. Sign up (free, instant, no credit card!)
3. Go to: **https://console.groq.com/keys**
4. Click **"Create API Key"**
5. Copy your API key

### 2. Add API Key to Your Project

Edit `backend/.env` file:

```env
GROQ_API_KEY=gsk_your-api-key-here
USE_MOCK_AI=false
```

### 3. Test It!

```bash
cd backend

# Quick test (Django integration)
python core/test_openai.py

# Detailed test with logging
python core/test_groq_direct.py
```

That's it! You're done! 🎉

## Features

### Model Used
- **llama-3.3-70b-versatile** (default)
- 70 billion parameters
- Excellent at complex tasks
- JSON mode support
- SUPER FAST inference

### Alternative Models
You can also use:
- `llama-3.1-70b-versatile` - Previous version
- `mixtral-8x7b-32768` - Good for longer contexts
- `gemma-7b-it` - Smaller, faster model

To change model, edit `ai_service.py` line 31.

## Free Tier Limits

Groq's free tier is incredibly generous:

- **30 requests per minute**
- **14,400 tokens per minute**
- **Unlimited requests per day!**
- No credit card required
- Perfect for development and production!

For comparison:
- OpenAI GPT-3.5: Paid only, quota issues
- DeepSeek: Requires payment
- Gemini: SSL issues with Python 3.14
- Groq: FREE, FAST, WORKS! ✨

## Speed Comparison

Groq is the **fastest AI inference** on the market:

| Provider | Speed (tokens/sec) |
|----------|-------------------|
| Groq | 🚀 500-800 |
| OpenAI | 40-60 |
| DeepSeek | 50-100 |
| Gemini | 60-80 |

**Groq is 10-15x FASTER than competitors!**

## Code Structure

### Main Service
`backend/core/ai_service.py`

```python
class ChatBotService:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv('GROQ_API_KEY'),
            base_url="https://api.groq.com/openai/v1"
        )
        self.model_name = 'llama-3.3-70b-versatile'
```

### Configuration
`backend/.env`

```env
GROQ_API_KEY=your-key-here
USE_MOCK_AI=false  # Set to true for offline testing
```

## API Response Format

Example extraction:

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
    "description": "Blue iPhone 13",
    "location_description": "Near the library",
    "latitude": null,
    "longitude": null,
    "tags": ["Electronics"]
  }
}
```

## Troubleshooting

### API Key Issues

**Error: "GROQ_API_KEY environment variable is not set"**

Solution:
```bash
# Check .env file exists
ls backend/.env

# Verify key is set
cat backend/.env | grep GROQ

# Restart Django server after updating .env
```

### Authentication Errors

**Error: "401 Unauthorized"**

Solutions:
1. Verify API key is correct in `.env`
2. Make sure you copied the entire key
3. Get a new key at: https://console.groq.com/keys
4. Ensure no extra spaces in `.env`

### Rate Limits

**Error: "429 Rate Limit Exceeded"**

You've hit the free tier limit:
- **30 requests per minute** for free tier

Solutions:
1. Wait 1 minute before retrying
2. Implement request throttling in your app
3. Upgrade to paid tier for higher limits (optional)

The free tier resets every minute, so brief pauses work fine!

### Connection Issues

**Error: Network/timeout errors**

Solutions:
1. Check internet connection
2. Verify firewall isn't blocking HTTPS
3. Try the direct test: `python core/test_groq_direct.py`
4. Check Groq status: https://status.groq.com

### SSL Issues (Rare with Python 3.14)

Groq works great with Python 3.14, but if you encounter SSL issues:

```bash
# Update OpenSSL
brew upgrade openssl@3

# Update certifi
pip install --upgrade certifi

# Reinstall openai
pip install --upgrade openai
```

## Mock Mode (Optional)

For testing without API calls:

```env
USE_MOCK_AI=true
```

Mock mode:
- Works offline
- No API calls
- Free forever
- Keyword-based extraction
- Great for development

## Performance Tips

### 1. Optimize Temperature

```python
temperature=0.1  # More focused, deterministic
temperature=0.7  # Balanced (recommended)
temperature=1.0  # More creative, varied
```

### 2. Limit Tokens

```python
max_tokens=500  # Faster, cheaper
max_tokens=2000  # More detailed
```

### 3. Cache Common Queries

Store frequent responses to avoid API calls.

### 4. Batch Processing

Process multiple items in one request when possible.

## Production Deployment

### Security Best Practices

1. **Never commit API keys**
   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   ```

2. **Use environment variables**
   - Set `GROQ_API_KEY` in production environment
   - Don't hardcode in source code

3. **Rotate keys regularly**
   - Generate new keys monthly
   - Delete old keys from console

### Monitoring

1. **Track usage**
   - Monitor requests per minute
   - Log errors and failures
   - Set up alerts for rate limits

2. **Implement fallbacks**
   - Enable mock mode as fallback
   - Show user-friendly error messages
   - Retry failed requests

### Scaling

Free tier is often sufficient for:
- Development
- Small apps (< 30 users/min)
- Personal projects
- MVPs and demos

Need more? Groq's paid tier offers:
- Higher rate limits
- Priority support
- Volume discounts
- Enterprise features

## Upgrading to Paid Tier (Optional)

If you need more capacity:

1. Visit: https://console.groq.com/settings/billing
2. Add payment method
3. Choose plan based on needs
4. Benefits:
   - Higher rate limits
   - More requests per day
   - Priority processing
   - SLA guarantees

**But for most apps, FREE tier is plenty!**

## Comparison: Why Groq Wins

| Feature | Groq | OpenAI | DeepSeek | Gemini |
|---------|------|--------|----------|--------|
| **Free Tier** | ✅ Generous | ❌ No | ⚠️ Limited | ⚠️ Limited |
| **Speed** | ⚡ 500-800 tok/s | 🐌 40-60 tok/s | 🐌 50-100 tok/s | 🐌 60-80 tok/s |
| **Python 3.14** | ✅ Works | ✅ Works | ✅ Works | ❌ SSL Errors |
| **No Credit Card** | ✅ Yes | ❌ No | ❌ No | ✅ Yes |
| **Rate Limits** | 30/min free | Quota issues | Pay required | 60/min free |
| **Quality** | 🌟 Excellent | 🌟 Excellent | 🌟 Very Good | 🌟 Excellent |

**Verdict: Groq is the clear winner for free, fast, reliable AI! 🏆**

## Additional Resources

- **Groq Console**: https://console.groq.com
- **Documentation**: https://console.groq.com/docs
- **API Reference**: https://console.groq.com/docs/api-reference
- **Status Page**: https://status.groq.com
- **Community**: https://discord.gg/groq

## Examples

### Custom System Prompt

```python
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
)
```

### JSON Mode

```python
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[...],
    response_format={"type": "json_object"}
)
```

### Streaming Responses

```python
stream = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[...],
    stream=True
)

for chunk in stream:
    print(chunk.choices[0].delta.content, end="")
```

## Success Stories

Groq powers thousands of applications:
- Chatbots and assistants
- Content generation
- Data extraction (like this project!)
- Code generation
- Translation services

## Next Steps

1. ✅ Get your FREE API key: https://console.groq.com/keys
2. ✅ Add it to `.env` file
3. ✅ Run: `python core/test_groq_direct.py`
4. ✅ Start building amazing AI features!

Your Lost & Found app now has **BLAZING FAST** AI powered by Groq! 🚀

---

**Questions?** Check the Groq docs or join their Discord community!
