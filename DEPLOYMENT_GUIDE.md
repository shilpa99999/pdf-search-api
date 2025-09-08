# 🚀 Render Deployment Guide - PDF Search API

## Quick Deployment Steps

### 1. Prepare Your Repository

1. **Upload to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - PDF Search API for Render"
   git branch -M main
   git remote add origin https://github.com/yourusername/pdf-search-api.git
   git push -u origin main
   ```

### 2. Deploy to Render

1. **Go to Render.com:**
   - Visit [render.com](https://render.com)
   - Sign up/Login with GitHub

2. **Create New Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your `pdf-search-api` repository

3. **Configure Deployment:**
   - **Name:** `pdf-search-api` (or your preferred name)
   - **Environment:** `Python 3`
   - **Build Command:** `chmod +x build.sh && ./build.sh`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 render_app:app`
   - **Plan:** Free (or paid for better performance)

4. **Environment Variables (Optional):**
   - `DEBUG=false`
   - `FLASK_ENV=production`

5. **Deploy:**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)

### 3. Your API Endpoints

Once deployed, your API will be available at:
```
https://your-app-name.onrender.com
```

**Key Endpoints:**
- **Documentation:** `https://your-app-name.onrender.com/`
- **Health Check:** `https://your-app-name.onrender.com/health`
- **Search (GET):** `https://your-app-name.onrender.com/search?q=GDPR&max_results=3`
- **Search (POST):** `https://your-app-name.onrender.com/search`
- **Chat:** `https://your-app-name.onrender.com/chat`

## 🔗 Power Automate Integration

### HTTP Request Action Setup:

1. **Add HTTP Request Action**
2. **Method:** `GET`
3. **URI:** `https://your-app-name.onrender.com/search`
4. **Queries:**
   - `q`: `[Dynamic content - user query]`
   - `max_results`: `5`

### Parse JSON Schema:
```json
{
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "query": {"type": "string"},
        "total_results": {"type": "integer"},
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "file_name": {"type": "string"},
                    "page_number": {"type": "integer"},
                    "highlighted_text": {"type": "string"},
                    "url": {"type": "string"},
                    "relevance_score": {"type": "number"}
                }
            }
        }
    }
}
```

## 🤖 Copilot Studio Integration

### HTTP Request Action Setup:

1. **Add HTTP Request Action**
2. **Method:** `POST`
3. **URI:** `https://your-app-name.onrender.com/chat`
4. **Headers:**
   - `Content-Type`: `application/json`
5. **Body:**
   ```json
   {
     "message": "[Dynamic content - user message]"
   }
   ```

### Response Handling:
The `/chat` endpoint returns a formatted message ready for display in Copilot Studio.

## 🧪 Testing Your Deployment

### Test Health Endpoint:
```bash
curl https://your-app-name.onrender.com/health
```

### Test Search Endpoint:
```bash
curl "https://your-app-name.onrender.com/search?q=data%20protection&max_results=2"
```

### Test Chat Endpoint:
```bash
curl -X POST https://your-app-name.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are GDPR principles?"}'
```

## 📊 Expected Response Format

### Search Response:
```json
{
  "success": true,
  "query": "data protection",
  "total_results": 2,
  "results": [
    {
      "file_name": "GDPR-Manual.pdf",
      "page_number": 1,
      "text": "Original text content...",
      "highlighted_text": "Text with <mark>highlighted</mark> terms",
      "url": "https://example.com/document.pdf#page=1",
      "relevance_score": 0.95
    }
  ]
}
```

### Chat Response:
```json
{
  "success": true,
  "message": "I found 2 relevant results for your question...",
  "query": "What are GDPR principles?",
  "total_results": 2,
  "results": [...]
}
```

## 🔧 Troubleshooting

### Common Issues:

1. **Build Fails:**
   - Check `requirements_render.txt` is present
   - Ensure `build.sh` has execute permissions

2. **App Doesn't Start:**
   - Verify `render_app.py` exists
   - Check logs in Render dashboard

3. **API Returns Demo Data:**
   - Normal behavior if `pdf_search_data.pkl` not uploaded
   - App will work with embedded demo data

### Performance Notes:

- **Free Tier:** App sleeps after 15 minutes of inactivity
- **Paid Tier:** Always-on with better performance
- **Cold Start:** First request may take 10-30 seconds

## 🎯 Power Automate Flow Example

1. **Trigger:** When user asks question in Copilot Studio
2. **HTTP Request:** GET to your search endpoint
3. **Parse JSON:** Extract results
4. **Compose:** Format response for user
5. **Return:** Send formatted answer back to Copilot Studio

## ✅ Deployment Checklist

- [ ] Repository uploaded to GitHub
- [ ] Render account created
- [ ] Web service configured
- [ ] Deployment successful
- [ ] Health endpoint returns 200
- [ ] Search endpoint tested
- [ ] Chat endpoint tested
- [ ] Power Automate integration configured
- [ ] Copilot Studio integration tested

## 🌐 Your Public API

Once deployed, your PDF Search API will be publicly available and ready for:
- ✅ Power Automate HTTP requests
- ✅ Copilot Studio integration
- ✅ Direct API calls
- ✅ Web interface access

**Your API URL:** `https://your-app-name.onrender.com`

---

🎉 **Ready for Production!** Your PDF Search API is now publicly available for Power Automate and Copilot Studio integration.
