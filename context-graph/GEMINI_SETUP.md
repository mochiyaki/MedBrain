# Google Gemini 3.5 Flash Setup Guide

The Context Graph Explorer now uses **Google Gemini 3.5 Flash** - Google's latest, fastest, and most affordable AI model for agents.

## 🚀 What is Gemini 3.5 Flash?

**Gemini 3.5 Flash** is Google's latest frontier model released May 2026. Key highlights:

| Feature | Details |
|---------|---------|
| **Speed** | 4x faster than other frontier models |
| **Cost** | $1.50 per million input tokens (~80% cheaper than GPT-4) |
| **Performance** | Outperforms Gemini 3.1 Pro on coding & agent tasks |
| **Availability** | Free tier available, no credit card required |
| **Model ID** | `gemini-3.5-flash` |

### Benchmarks
- Terminal-Bench 2.1: 76.2% (coding/agents)
- MCP Atlas: 83.6% (multi-turn reasoning)
- CharXiv Reasoning: 84.2% (multimodal understanding)

## 📋 Getting Your API Key

### Step 1: Go to Google AI Studio
Visit: https://aistudio.google.com/apikey

### Step 2: Click "Get API Key"
- First time? Click "Create API key in new project"
- Existing project? Click "Create API key"

### Step 3: Copy Your Key
- Your API key appears instantly
- Keep it private and secure

### Step 4: Add to .env
```bash
GOOGLE_API_KEY=your_api_key_here
```

## 💰 Pricing

| Model | Input | Output |
|-------|-------|--------|
| Gemini 3.5 Flash | $0.075/1M tokens | $0.30/1M tokens |
| GPT-3.5-turbo | $0.50/1M tokens | $1.50/1M tokens |
| GPT-4 | $3.00/1M tokens | $6.00/1M tokens |

**Cost Example**: 100,000 queries with 1,000 tokens each
- Gemini 3.5 Flash: ~$7.50
- GPT-3.5-turbo: ~$50
- GPT-4: ~$300

## 🔧 Configuration

### Default Setup
The app uses `gemini-3.5-flash` by default. No changes needed.

### Switch Models
Edit `langchain_agent.py`:

```python
# Line 13 - Change the model parameter
class ContextGraphAgent:
    def __init__(self, neo4j_connector, llm_api_key, model="gemini-3.5-pro"):
        # Now uses Gemini 3.5 Pro instead
```

Available models:
- `gemini-3.5-flash` ⭐ Recommended (latest, fastest, cheapest)
- `gemini-3.5-pro` (coming soon, more capable)
- `gemini-pro` (previous version)
- `gemini-pro-vision` (with image understanding)

## 🎯 Use Cases Perfect for Gemini 3.5 Flash

✅ **Graph Queries** - Fast node and relationship lookups  
✅ **Code Generation** - Generates Cypher queries efficiently  
✅ **Agents** - Excellent at tool calling and multi-step reasoning  
✅ **Long Contexts** - Handles large conversation histories  
✅ **Cost-Sensitive** - Best price-to-performance ratio

## 🆘 Troubleshooting

### "GOOGLE_API_KEY not found"
```bash
# Check .env file exists
cat .env

# Verify the key is set
echo $GOOGLE_API_KEY

# If empty, update .env with your actual key
```

### "API Error: Resource exhausted"
- Quota limits exceeded
- Check usage at: https://aistudio.google.com/
- Wait a few hours or upgrade plan

### "Invalid API Key"
- Check for typos in GOOGLE_API_KEY
- Ensure key copied completely
- Regenerate at: https://aistudio.google.com/apikey

### Model Not Found
- Use exact model name: `gemini-3.5-flash`
- Check available models: https://ai.google.dev/models

## 📊 Comparing LLM Providers

| Aspect | Gemini | OpenAI | Claude |
|--------|--------|--------|--------|
| **Cost** | $$ | $$$ | $$$ |
| **Speed** | ⚡⚡⚡ Fastest | ⚡⚡ | ⚡ |
| **Agents** | ⭐⭐⭐ Best | ⭐⭐⭐ | ⭐⭐ |
| **Coding** | ⭐⭐⭐ Excellent | ⭐⭐⭐ | ⭐⭐⭐ |
| **Setup** | Free | Free (paid) | Paid |

## 🔗 Useful Links

- [Get API Key](https://aistudio.google.com/apikey)
- [Gemini API Docs](https://ai.google.dev/)
- [Model Cards](https://ai.google.dev/models)
- [Pricing](https://ai.google.dev/pricing)
- [LangChain Gemini](https://python.langchain.com/docs/integrations/chat/google_generative_ai)

## 🚨 Safety & Privacy

- API keys are transmitted securely over HTTPS
- Keys stored locally in `.env` (add to `.gitignore`)
- Never commit API keys to version control
- Use environment variables in production
- Google stores minimal data for abuse prevention

## 📝 Migration from OpenAI to Gemini

If you had OpenAI set up before:

### Changes Made
✅ `requirements.txt` - Replaced `openai` with `google-generativeai`  
✅ `langchain_agent.py` - Changed from `OpenAI` to `ChatGoogleGenerativeAI`  
✅ `.env.example` - Changed from `OPENAI_API_KEY` to `GOOGLE_API_KEY`  
✅ `app.py` - Updated environment variable names  
✅ All documentation updated with Gemini info

### Simple Migration Steps
1. Get Gemini API key from https://aistudio.google.com/apikey
2. Update `.env`: `GOOGLE_API_KEY=your_key`
3. Run: `pip install -r requirements.txt` (installs new dependencies)
4. Done! The app automatically uses Gemini 3.5 Flash

## 🎓 Learning Resources

- [Gemini 3.5 Announcement](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-5/)
- [API Tutorial](https://ai.google.dev/tutorials)
- [Tool Use Guide](https://ai.google.dev/docs/function_calling)
- [Safety Guidelines](https://ai.google.dev/safety_intro)

---

**Status**: ✅ Gemini 3.5 Flash Integration Complete  
**Updated**: 2026-05-23  
**Model**: gemini-3.5-flash (fastest, most affordable)
