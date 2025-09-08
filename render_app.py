#!/usr/bin/env python3
"""
Production Flask API for PDF Search System - Render Deployment
Optimized for cloud deployment with minimal dependencies
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pickle
import os
import re
import json
from typing import List, Dict
import logging
import gzip
import base64

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class ProductionPDFSearchAPI:
    def __init__(self):
        self.documents = []
        self.loaded = False
        
    def load_search_data(self, data_file='pdf_search_data.pkl'):
        """Load search data with error handling for production"""
        try:
            if os.path.exists(data_file):
                with open(data_file, 'rb') as f:
                    data = pickle.load(f)
                
                self.documents = data.get('documents', [])
                self.loaded = len(self.documents) > 0
                
                if self.loaded:
                    logger.info(f"✅ Loaded {len(self.documents)} documents successfully")
                else:
                    logger.warning("⚠️ No documents found in data file")
                
                return self.loaded
            else:
                # Try to load from embedded data if file doesn't exist
                return self.load_embedded_data()
                
        except Exception as e:
            logger.error(f"❌ Error loading search data: {str(e)}")
            return self.load_embedded_data()
    
    def load_embedded_data(self):
        """Load minimal embedded data for demo purposes"""
        logger.info("Loading embedded demo data...")
        
        # Create sample documents for demonstration
        self.documents = [
            {
                'file_name': 'GDPR-Compliance-Manual.pdf',
                'file_path': 'demo/GDPR-Compliance-Manual.pdf',
                'page_number': 1,
                'paragraph_index': 0,
                'text': 'General Data Protection Regulation (GDPR) Compliance Manual. This document provides comprehensive guidance on GDPR compliance requirements, data protection principles, and individual rights under the regulation.',
                'url': 'https://example.com/gdpr-manual.pdf#page=1'
            },
            {
                'file_name': 'Data-Protection-Rights.pdf',
                'file_path': 'demo/Data-Protection-Rights.pdf',
                'page_number': 1,
                'paragraph_index': 0,
                'text': 'Rights of Individuals under the General Data Protection Regulation. Data subjects have various rights including the right to access, rectify, erase, restrict processing, data portability, and object to processing of their personal data.',
                'url': 'https://example.com/data-rights.pdf#page=1'
            },
            {
                'file_name': 'GDPR-Principles.pdf',
                'file_path': 'demo/GDPR-Principles.pdf',
                'page_number': 2,
                'paragraph_index': 1,
                'text': 'Key principles under GDPR include lawfulness, fairness and transparency, purpose limitation, data minimisation, accuracy, storage limitation, integrity and confidentiality, and accountability. Organizations must demonstrate compliance with these principles.',
                'url': 'https://example.com/gdpr-principles.pdf#page=2'
            },
            {
                'file_name': 'Data-Processing-Agreement.pdf',
                'file_path': 'demo/Data-Processing-Agreement.pdf',
                'page_number': 3,
                'paragraph_index': 0,
                'text': 'Data Processing Agreement template for GDPR compliance. This agreement establishes the relationship between data controllers and data processors, defining responsibilities, security measures, and breach notification procedures.',
                'url': 'https://example.com/dpa-template.pdf#page=3'
            },
            {
                'file_name': 'Breach-Notification-Procedures.pdf',
                'file_path': 'demo/Breach-Notification.pdf',
                'page_number': 1,
                'paragraph_index': 2,
                'text': 'Personal data breach notification requirements under GDPR. Organizations must notify supervisory authorities within 72 hours of becoming aware of a breach, and inform data subjects when the breach poses high risks to their rights and freedoms.',
                'url': 'https://example.com/breach-notification.pdf#page=1'
            }
        ]
        
        self.loaded = True
        logger.info(f"✅ Loaded {len(self.documents)} demo documents")
        return True
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Enhanced text search for production"""
        if not self.loaded:
            return []
        
        try:
            query_lower = query.lower()
            query_terms = [term for term in query_lower.split() if len(term) > 2]
            
            if not query_terms:
                return []
            
            results = []
            
            for doc in self.documents:
                text_lower = doc['text'].lower()
                
                # Calculate relevance score
                score = 0
                matches = 0
                
                for term in query_terms:
                    count = text_lower.count(term)
                    if count > 0:
                        score += count * len(term) * 2  # Weight by term length
                        matches += 1
                
                # Bonus for multiple term matches
                if matches > 1:
                    score *= (1 + matches * 0.2)
                
                if score > 0:
                    doc_copy = doc.copy()
                    doc_copy['relevance_score'] = min(score / len(doc['text']), 1.0)
                    doc_copy['highlighted_text'] = self.highlight_text(doc['text'], query)
                    doc_copy['match_count'] = matches
                    results.append(doc_copy)
            
            # Sort by relevance score and match count
            results.sort(key=lambda x: (x['relevance_score'], x['match_count']), reverse=True)
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return []
    
    def highlight_text(self, text: str, query: str) -> str:
        """Highlight query terms in text"""
        query_terms = [term for term in query.lower().split() if len(term) > 2]
        highlighted_text = text
        
        for term in query_terms:
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            highlighted_text = pattern.sub(
                f'<mark style="background-color: yellow; padding: 2px; border-radius: 3px;">{term}</mark>',
                highlighted_text
            )
        
        return highlighted_text

# Initialize the search system
search_system = ProductionPDFSearchAPI()

@app.route('/')
def home():
    """Home page with API documentation"""
    status = "✅ Ready" if search_system.loaded else "❌ Not Ready"
    doc_count = len(search_system.documents) if search_system.loaded else 0
    base_url = request.host_url.rstrip('/')
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>PDF Search API - Public Deployment</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }}
            .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .status {{ padding: 20px; background: #e8f5e8; border: 1px solid #4caf50; border-radius: 8px; margin: 20px 0; }}
            .endpoint {{ background: #f8f9fa; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #007acc; }}
            .method {{ color: #007acc; font-weight: bold; font-size: 14px; }}
            .url {{ background: #e9ecef; padding: 8px 12px; border-radius: 4px; font-family: monospace; margin: 10px 0; word-break: break-all; }}
            pre {{ background: #f1f3f4; padding: 15px; border-radius: 6px; overflow-x: auto; font-size: 13px; }}
            a {{ color: #007acc; text-decoration: none; font-weight: 500; }}
            a:hover {{ text-decoration: underline; }}
            .integration {{ background: #fff3cd; border: 1px solid #ffc107; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .feature {{ display: inline-block; background: #e3f2fd; padding: 8px 12px; margin: 4px; border-radius: 20px; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📄 PDF Search API</h1>
                <p>Public API for intelligent PDF document search with highlighting and citations</p>
            </div>
            
            <div class="status">
                <h3>🚀 System Status</h3>
                <p><strong>Status:</strong> {status}</p>
                <p><strong>Documents Available:</strong> {doc_count}</p>
                <p><strong>Base URL:</strong> <code>{base_url}</code></p>
            </div>
            
            <h2>✨ Features</h2>
            <div>
                <span class="feature">🔍 Intelligent Search</span>
                <span class="feature">🟡 Yellow Highlighting</span>
                <span class="feature">🔗 Clickable URLs</span>
                <span class="feature">📄 Citations</span>
                <span class="feature">🌐 CORS Enabled</span>
                <span class="feature">⚡ Fast Response</span>
            </div>
            
            <h2>🔌 API Endpoints</h2>
            
            <div class="endpoint">
                <h3><span class="method">GET</span> /health</h3>
                <p>Check API health and status</p>
                <div class="url">{base_url}/health</div>
                <p><a href="/health" target="_blank">🧪 Test Health Endpoint</a></p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method">GET</span> /search</h3>
                <p>Search documents (Power Automate compatible)</p>
                <div class="url">{base_url}/search?q=GDPR&max_results=3</div>
                <p><strong>Parameters:</strong></p>
                <ul>
                    <li><code>q</code> - Search query (required)</li>
                    <li><code>max_results</code> - Number of results (optional, default: 5)</li>
                </ul>
                <p><a href="/search?q=data%20protection&max_results=2" target="_blank">🧪 Test Search</a></p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method">POST</span> /search</h3>
                <p>Advanced search with JSON payload</p>
                <div class="url">{base_url}/search</div>
                <pre>{{"query": "individual rights", "max_results": 3}}</pre>
            </div>
            
            <div class="endpoint">
                <h3><span class="method">POST</span> /chat</h3>
                <p>Conversational search (Copilot Studio compatible)</p>
                <div class="url">{base_url}/chat</div>
                <pre>{{"message": "What are the key principles of GDPR?"}}</pre>
            </div>
            
            <div class="integration">
                <h3>🔗 Power Automate Integration</h3>
                <p><strong>HTTP Request Action:</strong></p>
                <ul>
                    <li><strong>Method:</strong> GET</li>
                    <li><strong>URI:</strong> <code>{base_url}/search</code></li>
                    <li><strong>Queries:</strong> q = [your search term], max_results = 5</li>
                </ul>
                <p>Use the "Parse JSON" action to process the response.</p>
            </div>
            
            <div class="integration">
                <h3>🤖 Copilot Studio Integration</h3>
                <p><strong>HTTP Request Action:</strong></p>
                <ul>
                    <li><strong>Method:</strong> POST</li>
                    <li><strong>URI:</strong> <code>{base_url}/chat</code></li>
                    <li><strong>Headers:</strong> Content-Type: application/json</li>
                    <li><strong>Body:</strong> {{"message": "user's question"}}</li>
                </ul>
                <p>The response includes formatted text ready for display in Copilot Studio.</p>
            </div>
            
            <h2>📊 Response Format</h2>
            <pre>{{
  "success": true,
  "query": "data protection",
  "total_results": 2,
  "results": [
    {{
      "file_name": "GDPR-Manual.pdf",
      "page_number": 1,
      "text": "Original text...",
      "highlighted_text": "Text with <mark>highlights</mark>",
      "url": "https://example.com/document.pdf#page=1",
      "relevance_score": 0.95
    }}
  ]
}}</pre>
            
            <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666;">
                <p>🚀 Ready for Power Automate and Copilot Studio integration!</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'service': 'PDF Search API',
        'version': '1.0.0',
        'loaded': search_system.loaded,
        'documents_count': len(search_system.documents) if search_system.loaded else 0,
        'endpoints': ['/health', '/search', '/chat'],
        'message': 'PDF Search API is running and ready for integration'
    })

@app.route('/search', methods=['GET', 'POST'])
def search_documents():
    """Search PDF documents - Power Automate compatible"""
    try:
        if not search_system.loaded:
            return jsonify({
                'success': False,
                'error': 'Search system not loaded. Using demo data.',
                'service_status': 'degraded'
            }), 503
        
        # Handle both GET and POST requests
        if request.method == 'POST':
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'Invalid JSON payload. Expected: {"query": "search term", "max_results": 5}'
                }), 400
            
            query = data.get('query', '')
            max_results = min(data.get('max_results', 5), 20)  # Limit to 20 results
            
        else:  # GET request
            query = request.args.get('q', '').strip()
            try:
                max_results = min(int(request.args.get('max_results', 5)), 20)
            except ValueError:
                max_results = 5
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query parameter is required. Use "q" for GET or "query" for POST requests.'
            }), 400
        
        if len(query) < 2:
            return jsonify({
                'success': False,
                'error': 'Query must be at least 2 characters long.'
            }), 400
        
        # Perform search
        results = search_system.search(query, top_k=max_results)
        
        # Format response
        response = {
            'success': True,
            'query': query,
            'total_results': len(results),
            'max_results': max_results,
            'results': results,
            'search_method': 'enhanced_text_matching',
            'api_version': '1.0.0'
        }
        
        logger.info(f"Search query: '{query}' - Found {len(results)} results")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Internal search error: {str(e)}',
            'query': query if 'query' in locals() else 'unknown'
        }), 500

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    """Conversational search endpoint - Copilot Studio compatible"""
    try:
        if not search_system.loaded:
            return jsonify({
                'success': False,
                'message': 'Search system not loaded. Using demo data for responses.',
                'service_status': 'degraded'
            }), 503
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Invalid request. Please send JSON with "message" field.'
            }), 400
        
        user_message = data.get('message', data.get('query', '')).strip()
        max_results = min(data.get('max_results', 3), 10)  # Limit for chat responses
        
        if not user_message:
            return jsonify({
                'success': False,
                'message': 'Please provide a message or question to search for.'
            }), 400
        
        if len(user_message) < 3:
            return jsonify({
                'success': False,
                'message': 'Please provide a more specific question (at least 3 characters).'
            }), 400
        
        # Perform search
        results = search_system.search(user_message, top_k=max_results)
        
        if not results:
            return jsonify({
                'success': True,
                'message': f"I couldn't find any relevant information about '{user_message}' in the available PDF documents. Please try rephrasing your question or using different keywords.",
                'query': user_message,
                'total_results': 0,
                'results': []
            })
        
        # Create conversational response
        response_parts = [f"I found {len(results)} relevant result{'s' if len(results) != 1 else ''} for your question about '{user_message}':\\n"]
        
        for i, result in enumerate(results, 1):
            response_parts.append(f"**{i}. {result['file_name']} (Page {result['page_number']})**")
            
            # Truncate long text for chat response
            text = result['highlighted_text']
            if len(text) > 400:
                text = text[:400] + "..."
            
            response_parts.append(text)
            response_parts.append(f"[📄 View Document]({result['url']})\\n")
        
        conversational_response = "\\n".join(response_parts)
        
        logger.info(f"Chat query: '{user_message}' - Generated response with {len(results)} results")
        
        return jsonify({
            'success': True,
            'message': conversational_response,
            'query': user_message,
            'total_results': len(results),
            'results': results,
            'response_type': 'conversational',
            'api_version': '1.0.0'
        })
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Sorry, I encountered an error while processing your request: {str(e)}',
            'error_type': 'internal_error'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'available_endpoints': ['/health', '/search', '/chat'],
        'documentation': request.host_url
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'Please try again later or contact support'
    }), 500

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 'Method not allowed',
        'message': 'Check the API documentation for correct HTTP methods'
    }), 405

def initialize_app():
    """Initialize the application"""
    try:
        success = search_system.load_search_data()
        if success:
            logger.info("🚀 PDF Search API initialized successfully")
        else:
            logger.warning("⚠️ PDF Search API started with demo data")
        return success
    except Exception as e:
        logger.error(f"❌ Initialization error: {str(e)}")
        return False

# Health check for deployment platforms
@app.route('/ping')
def ping():
    return jsonify({'status': 'ok', 'service': 'pdf-search-api'})

if __name__ == '__main__':
    initialize_app()
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"🚀 Starting PDF Search API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
else:
    # For production WSGI servers
    initialize_app()
