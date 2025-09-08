# PDF Search System

A comprehensive PDF document search system with intelligent highlighting, citations, and web interface. Perfect for Power Automate and Copilot Studio integration.

## 🚀 Features

- **Intelligent PDF Search**: Hybrid semantic + keyword search across all PDF documents
- **Yellow Highlighting**: Query terms highlighted in search results
- **Clickable URLs**: Direct links to specific PDF pages
- **Citations**: Page numbers and document references
- **Web Chat Interface**: Modern, responsive chat UI
- **REST API**: Compatible with Power Automate and Copilot Studio
- **Real-time Processing**: Fast search with FAISS indexing

## 📋 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Process PDFs (Run Jupyter Notebook)

Open and run `pdf_search_system.ipynb` to:
- Import all PDF files from your directory
- Extract text and create search indices
- Save processed data for the API

```bash
jupyter notebook pdf_search_system.ipynb
```

**Important**: Run all cells in the notebook first to process your PDFs and create the search index.

### 3. Start the Flask API

```bash
python app.py
```

The API will be available at:
- **API Documentation**: http://localhost:5000
- **Chat Interface**: http://localhost:5000/chat-ui
- **Search Endpoint**: http://localhost:5000/search

## 🔍 Usage Examples

### Web Chat Interface

1. Open http://localhost:5000/chat-ui
2. Type your question: "What are individual rights under GDPR?"
3. Get highlighted results with clickable PDF links

### API Usage

#### Search via POST

```bash
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "data protection rights",
    "max_results": 5,
    "include_highlights": true
  }'
```

#### Search via GET (Power Automate compatible)

```bash
curl "http://localhost:5000/search?q=GDPR%20compliance&max_results=3"
```

#### Chat Endpoint (Copilot Studio compatible)

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about data processing agreements"
  }'
```

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API documentation |
| `/chat-ui` | GET | Web chat interface |
| `/search` | POST/GET | Search PDF documents |
| `/chat` | POST | Conversational search |
| `/health` | GET | Health check |

## 📊 Response Format

```json
{
  "success": true,
  "query": "data protection",
  "total_results": 3,
  "results": [
    {
      "file_name": "GDPR-Manual.pdf",
      "page_number": 15,
      "text": "Original text content...",
      "highlighted_text": "Text with <mark>highlighted</mark> terms",
      "url": "file:///path/to/GDPR-Manual.pdf#page=15",
      "relevance_score": 0.95
    }
  ]
}
```

## 🔗 Power Automate Integration

1. **HTTP Request Action**: Use the `/search` endpoint
2. **Method**: GET or POST
3. **URL**: `http://your-server:5000/search`
4. **Parameters**: 
   - `q`: Your search query
   - `max_results`: Number of results (optional)

Example Power Automate flow:
```
HTTP Request → Parse JSON → Compose Response
```

## 🤖 Copilot Studio Integration

1. **HTTP Request**: Use the `/chat` endpoint
2. **Method**: POST
3. **Body**: `{"message": "user query"}`
4. **Response**: Formatted conversational response with citations

## 📁 File Structure

```
pdf-search-system/
├── pdf_search_system.ipynb    # Jupyter notebook for PDF processing
├── app.py                     # Flask API server
├── requirements.txt           # Python dependencies
├── README.md                 # This file
├── static/
│   ├── style.css             # Chat interface styles
│   └── script.js             # Chat interface JavaScript
├── templates/
│   └── chat.html             # Chat interface HTML
└── *.pdf                     # Your PDF documents
```

## 🛠️ Customization

### Adding More PDF Sources

Place PDF files anywhere in your directory structure. The system automatically discovers all `.pdf` files recursively.

### Adjusting Search Parameters

In the Jupyter notebook, modify:
- `hybrid_weight`: Balance between semantic (0.7) and keyword (0.3) search
- `top_k`: Number of results to return
- `max_features`: TF-IDF vocabulary size

### Styling the Chat Interface

Edit `static/style.css` to customize the appearance of the web chat interface.

## 🚀 Production Deployment

### Using Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Environment Variables

- `PORT`: Server port (default: 5000)
- `DEBUG`: Enable debug mode (default: False)

### Making API Publicly Available

For Power Automate access, deploy to:
- **Heroku**: `git push heroku main`
- **AWS/Azure**: Use container deployment
- **ngrok**: For testing: `ngrok http 5000`

## 📝 Notes

- **PDF URLs**: Generated URLs use `file://` protocol for local files
- **Security**: API has CORS enabled for web integration
- **Performance**: FAISS indexing provides sub-second search times
- **Memory**: Large PDF collections may require more RAM for embeddings

## 🔍 Supported PDF Types

- Text-based PDFs (searchable)
- Scanned PDFs with OCR text layer
- Multi-page documents
- Password-protected PDFs (with manual unlock)

## 📞 Support

For issues or questions:
1. Check that all PDFs were processed successfully in the Jupyter notebook
2. Verify the Flask API shows "Ready" status at http://localhost:5000
3. Ensure all dependencies are installed correctly

---

**Ready to search your PDF documents intelligently!** 🎉
