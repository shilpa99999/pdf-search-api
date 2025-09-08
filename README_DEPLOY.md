# PDF Search API - Public Deployment

🚀 **Intelligent PDF search API with yellow highlighting, citations, and clickable URLs**

## 🌐 Live Demo

Once deployed, your API will be available at:
```
https://your-app-name.onrender.com
```

## ✨ Features

- 🔍 **Intelligent Search** - Semantic text matching across PDF documents
- 🟡 **Yellow Highlighting** - Query terms highlighted in results
- 🔗 **Clickable URLs** - Direct links to specific PDF pages
- 📄 **Citations** - Page numbers and document references
- 🌐 **CORS Enabled** - Ready for web integration
- ⚡ **Fast API** - Optimized for Power Automate and Copilot Studio

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API documentation |
| `/health` | GET | Health check |
| `/search` | GET/POST | Search documents |
| `/chat` | POST | Conversational search |

## 🔗 Integration Examples

### Power Automate (GET Request)
```
GET https://your-app-name.onrender.com/search?q=GDPR&max_results=5
```

### Copilot Studio (POST Request)
```json
POST https://your-app-name.onrender.com/chat
{
  "message": "What are individual rights under GDPR?"
}
```

## 📊 Response Format

```json
{
  "success": true,
  "query": "data protection",
  "total_results": 2,
  "results": [
    {
      "file_name": "GDPR-Manual.pdf",
      "page_number": 1,
      "highlighted_text": "Text with <mark>highlighted</mark> terms",
      "url": "https://example.com/document.pdf#page=1",
      "relevance_score": 0.95
    }
  ]
}
```

## 🚀 Quick Deploy

1. **Fork/Clone this repository**
2. **Deploy to Render:**
   - Connect your GitHub repo
   - Build Command: `chmod +x build.sh && ./build.sh`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 render_app:app`

## 📖 Documentation

- Full deployment guide: `DEPLOYMENT_GUIDE.md`
- API documentation available at your deployed URL

## 🎯 Ready for Production

✅ Power Automate integration  
✅ Copilot Studio compatibility  
✅ Public API access  
✅ CORS enabled  
✅ Error handling  
✅ Health monitoring  

---

**🌐 Deploy now and get your public PDF Search API URL for Power Automate and Copilot Studio integration!**
