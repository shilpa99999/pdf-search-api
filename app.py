#!/usr/bin/env python3
"""
Flask API for PDF Search System
Provides REST endpoints for searching PDF documents with highlighting and citations
Compatible with Power Automate and Copilot Studio integration
"""

from flask import Flask, request, jsonify, render_template_string, render_template
from flask_cors import CORS
import pickle
import os
import re
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

class PDFSearchAPI:
    def __init__(self):
        self.documents = []
        self.embeddings = None
        self.index = None
        self.model = None
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.loaded = False
        
    def load_search_data(self, data_file='pdf_search_data.pkl'):
        """Load pre-trained search data"""
        try:
            if os.path.exists(data_file):
                with open(data_file, 'rb') as f:
                    data = pickle.load(f)
                
                self.documents = data['documents']
                self.embeddings = data['embeddings']
                self.tfidf_vectorizer = data['tfidf_vectorizer']
                self.tfidf_matrix = data['tfidf_matrix']
                
                # Initialize model and FAISS index
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                
                # Recreate FAISS index
                if self.embeddings is not None:
                    dimension = self.embeddings.shape[1]
                    self.index = faiss.IndexFlatIP(dimension)
                    faiss.normalize_L2(self.embeddings)
                    self.index.add(self.embeddings)
                
                self.loaded = True
                logger.info(f"Loaded {len(self.documents)} documents successfully")
                return True
            else:
                logger.error(f"Data file {data_file} not found")
                return False
        except Exception as e:
            logger.error(f"Error loading search data: {str(e)}")
            return False
    
    def search(self, query: str, top_k: int = 5, hybrid_weight: float = 0.7) -> List[Dict]:
        """Search for relevant documents using hybrid approach"""
        if not self.loaded or self.embeddings is None:
            return []
        
        try:
            # Semantic search using embeddings
            query_embedding = self.model.encode([query])
            faiss.normalize_L2(query_embedding)
            
            semantic_scores, semantic_indices = self.index.search(query_embedding, min(top_k * 2, len(self.documents)))
            semantic_scores = semantic_scores[0]
            semantic_indices = semantic_indices[0]
            
            # Keyword search using TF-IDF
            query_tfidf = self.tfidf_vectorizer.transform([query])
            keyword_scores = cosine_similarity(query_tfidf, self.tfidf_matrix)[0]
            
            # Combine scores (hybrid approach)
            final_scores = {}
            
            # Add semantic scores
            for i, idx in enumerate(semantic_indices):
                if idx < len(self.documents):
                    final_scores[idx] = hybrid_weight * semantic_scores[i]
            
            # Add keyword scores
            for idx, score in enumerate(keyword_scores):
                if idx in final_scores:
                    final_scores[idx] += (1 - hybrid_weight) * score
                else:
                    final_scores[idx] = (1 - hybrid_weight) * score
            
            # Sort by combined score
            sorted_results = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
            
            # Prepare results with highlighting
            results = []
            for idx, score in sorted_results:
                doc = self.documents[idx].copy()
                doc['relevance_score'] = float(score)
                doc['highlighted_text'] = self.highlight_text(doc['text'], query)
                results.append(doc)
            
            return results
            
        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            return []
    
    def highlight_text(self, text: str, query: str) -> str:
        """Highlight query terms in text"""
        query_terms = query.lower().split()
        highlighted_text = text
        
        for term in query_terms:
            if len(term) > 2:  # Only highlight meaningful terms
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                highlighted_text = pattern.sub(
                    f'<mark style="background-color: yellow; padding: 2px;">{term}</mark>',
                    highlighted_text
                )
        
        return highlighted_text

# Initialize the search system
search_system = PDFSearchAPI()

@app.route('/chat-ui')
def chat_ui():
    """Web chat interface"""
    return render_template('chat.html')

@app.route('/')
def home():
    """Home page with API documentation"""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PDF Search API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .method { color: #007acc; font-weight: bold; }
            pre { background: #eee; padding: 10px; border-radius: 3px; overflow-x: auto; }
            h1 { color: #333; }
            h2 { color: #007acc; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📄 PDF Search API</h1>
            <p>RESTful API for searching PDF documents with highlighting and citations.</p>
            <p><strong>Status:</strong> {{ status }}</p>
            <p><strong>Documents Loaded:</strong> {{ doc_count }}</p>
            
            <h2>Endpoints</h2>
            
            <div class="endpoint">
                <h3><span class="method">GET</span> /</h3>
                <p>API documentation and status</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method">GET</span> /chat-ui</h3>
                <p>Interactive web chat interface</p>
                <p><a href="/chat-ui" style="color: #007acc; font-weight: bold;">🚀 Launch Chat Interface</a></p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method">POST</span> /search</h3>
                <p>Search PDF documents</p>
                <h4>Request Body:</h4>
                <pre>{
    "query": "your search query",
    "max_results": 5,
    "include_highlights": true
}</pre>
                <h4>Response:</h4>
                <pre>{
    "success": true,
    "query": "search query",
    "total_results": 3,
    "results": [
        {
            "file_name": "document.pdf",
            "page_number": 1,
            "text": "original text",
            "highlighted_text": "text with <mark>highlights</mark>",
            "url": "file:///path/to/document.pdf#page=1",
            "relevance_score": 0.95
        }
    ]
}</pre>
            </div>
            
            <div class="endpoint">
                <h3><span class="method">GET</span> /search?q=query&max_results=5</h3>
                <p>Search via GET request (for Power Automate compatibility)</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method">GET</span> /health</h3>
                <p>Health check endpoint</p>
            </div>
            
            <h2>Power Automate Integration</h2>
            <p>This API is designed to work with Power Automate. Use the search endpoints to query PDF documents and get structured responses with clickable URLs.</p>
            
            <h2>Copilot Studio Integration</h2>
            <p>The API provides formatted responses suitable for Copilot Studio, including highlighted text and direct links to PDF pages.</p>
        </div>
    </body>
    </html>
    """
    
    status = "✅ Ready" if search_system.loaded else "❌ Not Ready (Run Jupyter notebook first)"
    doc_count = len(search_system.documents) if search_system.loaded else 0
    
    return render_template_string(html_template, status=status, doc_count=doc_count)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'loaded': search_system.loaded,
        'documents_count': len(search_system.documents) if search_system.loaded else 0
    })

@app.route('/search', methods=['POST', 'GET'])
def search_documents():
    """Search PDF documents"""
    try:
        if not search_system.loaded:
            return jsonify({
                'success': False,
                'error': 'Search system not loaded. Please run the Jupyter notebook first to process PDFs.'
            }), 500
        
        # Handle both POST and GET requests
        if request.method == 'POST':
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
            
            query = data.get('query', '')
            max_results = data.get('max_results', 5)
            include_highlights = data.get('include_highlights', True)
        else:  # GET request
            query = request.args.get('q', '')
            max_results = int(request.args.get('max_results', 5))
            include_highlights = request.args.get('include_highlights', 'true').lower() == 'true'
        
        if not query:
            return jsonify({'success': False, 'error': 'Query parameter is required'}), 400
        
        # Perform search
        results = search_system.search(query, top_k=max_results)
        
        # Format results for API response
        formatted_results = []
        for result in results:
            formatted_result = {
                'file_name': result['file_name'],
                'page_number': result['page_number'],
                'text': result['text'],
                'url': result['url'],
                'relevance_score': result['relevance_score']
            }
            
            if include_highlights:
                formatted_result['highlighted_text'] = result['highlighted_text']
            
            formatted_results.append(formatted_result)
        
        response = {
            'success': True,
            'query': query,
            'total_results': len(formatted_results),
            'results': formatted_results
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Search failed: {str(e)}'
        }), 500

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    """Chat-style endpoint for conversational queries (Copilot Studio compatible)"""
    try:
        if not search_system.loaded:
            return jsonify({
                'success': False,
                'message': 'Search system not loaded. Please run the Jupyter notebook first to process PDFs.'
            }), 500
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No JSON data provided'}), 400
        
        query = data.get('message', data.get('query', ''))
        max_results = data.get('max_results', 3)
        
        if not query:
            return jsonify({'success': False, 'message': 'Message is required'}), 400
        
        # Perform search
        results = search_system.search(query, top_k=max_results)
        
        if not results:
            return jsonify({
                'success': True,
                'message': f"I couldn't find any relevant information about '{query}' in the available PDF documents. Please try rephrasing your question or using different keywords.",
                'results': []
            })
        
        # Create a conversational response
        response_parts = [f"I found {len(results)} relevant results for your query about '{query}':\n"]
        
        for i, result in enumerate(results, 1):
            response_parts.append(f"**{i}. {result['file_name']} (Page {result['page_number']})**")
            response_parts.append(result['highlighted_text'])
            response_parts.append(f"[📄 Open PDF at Page {result['page_number']}]({result['url']})\n")
        
        conversational_response = "\n".join(response_parts)
        
        return jsonify({
            'success': True,
            'message': conversational_response,
            'query': query,
            'total_results': len(results),
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Sorry, I encountered an error while searching: {str(e)}'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

def initialize_app():
    """Initialize the application by loading search data"""
    success = search_system.load_search_data()
    if success:
        logger.info("PDF Search API initialized successfully")
    else:
        logger.warning("PDF Search API started but search data not loaded. Run the Jupyter notebook first.")

if __name__ == '__main__':
    initialize_app()
    
    # Run the Flask app
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"""
    🚀 PDF Search API Starting...
    
    📍 Local URL: http://localhost:{port}
    📖 API Documentation: http://localhost:{port}
    🔍 Search Endpoint: http://localhost:{port}/search
    💬 Chat Endpoint: http://localhost:{port}/chat
    
    For Power Automate integration, use the search endpoint with GET or POST requests.
    For Copilot Studio, use the chat endpoint for conversational responses.
    """)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
