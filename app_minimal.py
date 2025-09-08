#!/usr/bin/env python3
"""
Ultra-minimal Flask API for Render deployment
Zero external dependencies beyond Flask basics
"""

from flask import Flask, request, jsonify
import os
import re
import json

app = Flask(__name__)

# Enable CORS manually without flask-cors dependency
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Sample documents data
DOCUMENTS = [
    {
        'file_name': 'GDPR-Compliance-Manual.pdf',
        'page_number': 1,
        'text': 'General Data Protection Regulation (GDPR) Compliance Manual. This document provides comprehensive guidance on GDPR compliance requirements, data protection principles, and individual rights under the regulation.',
        'url': 'https://example.com/gdpr-manual.pdf#page=1'
    },
    {
        'file_name': 'Data-Protection-Rights.pdf',
        'page_number': 1,
        'text': 'Rights of Individuals under the General Data Protection Regulation. Data subjects have various rights including the right to access, rectify, erase, restrict processing, data portability, and object to processing of their personal data.',
        'url': 'https://example.com/data-rights.pdf#page=1'
    },
    {
        'file_name': 'GDPR-Principles.pdf',
        'page_number': 2,
        'text': 'Key principles under GDPR include lawfulness, fairness and transparency, purpose limitation, data minimisation, accuracy, storage limitation, integrity and confidentiality, and accountability. Organizations must demonstrate compliance with these principles.',
        'url': 'https://example.com/gdpr-principles.pdf#page=2'
    },
    {
        'file_name': 'Data-Processing-Agreement.pdf',
        'page_number': 3,
        'text': 'Data Processing Agreement template for GDPR compliance. This agreement establishes the relationship between data controllers and data processors, defining responsibilities, security measures, and breach notification procedures.',
        'url': 'https://example.com/dpa-template.pdf#page=3'
    },
    {
        'file_name': 'Breach-Notification-Procedures.pdf',
        'page_number': 1,
        'text': 'Personal data breach notification requirements under GDPR. Organizations must notify supervisory authorities within 72 hours of becoming aware of a breach, and inform data subjects when the breach poses high risks to their rights and freedoms.',
        'url': 'https://example.com/breach-notification.pdf#page=1'
    },
    {
        'file_name': 'Individual-Rights-GDPR.pdf',
        'page_number': 1,
        'text': 'Individual rights under GDPR include the right of access, right to rectification, right to erasure (right to be forgotten), right to restrict processing, right to data portability, right to object, and rights related to automated decision making and profiling.',
        'url': 'https://example.com/individual-rights.pdf#page=1'
    }
]

def highlight_text(text, query):
    """Simple text highlighting"""
    words = query.lower().split()
    result = text
    for word in words:
        if len(word) > 2:
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            result = pattern.sub(f'<mark style="background-color: yellow; padding: 2px;">{word}</mark>', result)
    return result

def search_documents(query, max_results=5):
    """Simple document search"""
    query_lower = query.lower()
    results = []
    
    for doc in DOCUMENTS:
        if any(word in doc['text'].lower() for word in query_lower.split() if len(word) > 2):
            doc_copy = doc.copy()
            doc_copy['relevance_score'] = 0.8  # Fixed score for demo
            doc_copy['highlighted_text'] = highlight_text(doc['text'], query)
            results.append(doc_copy)
    
    return results[:max_results]

@app.route('/')
def home():
    """API documentation"""
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>PDF Search API</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f7fa; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
            .status {{ background: #d4edda; padding: 15px; border-radius: 5px; margin: 20px 0; border: 1px solid #c3e6cb; }}
            .endpoint {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff; }}
            a {{ color: #007bff; text-decoration: none; }}
            .method {{ color: #007bff; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📄 PDF Search API</h1>
            <div class="status">
                <h3>✅ Status: Online & Ready</h3>
                <p><strong>Documents:</strong> {len(DOCUMENTS)} available</p>
                <p><strong>Base URL:</strong> {request.host_url}</p>
            </div>
            
            <h2>🔌 API Endpoints</h2>
            
            <div class="endpoint">
                <h3><span class="method">GET</span> /health</h3>
                <p>Health check endpoint</p>
                <p><a href="/health">🧪 Test Health Check</a></p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method">GET</span> /search</h3>
                <p>Search documents (Power Automate compatible)</p>
                <p><strong>Usage:</strong> /search?q=GDPR&max_results=5</p>
                <p><a href="/search?q=GDPR&max_results=3">🧪 Test Search</a></p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method">POST</span> /chat</h3>
                <p>Conversational search (Copilot Studio compatible)</p>
                <p><strong>Body:</strong> {{"message": "What are GDPR principles?"}}</p>
            </div>
            
            <h2>🔗 Integration Examples</h2>
            <div class="endpoint">
                <h4>Power Automate</h4>
                <p><code>GET {request.host_url}search?q=[query]&max_results=5</code></p>
            </div>
            
            <div class="endpoint">
                <h4>Copilot Studio</h4>
                <p><code>POST {request.host_url}chat</code></p>
                <p><code>{{"message": "[user question]"}}</code></p>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'PDF Search API',
        'documents_count': len(DOCUMENTS),
        'version': '1.0.0',
        'endpoints': ['/health', '/search', '/chat']
    })

@app.route('/search', methods=['GET', 'POST'])
def search():
    """Search endpoint"""
    try:
        if request.method == 'POST':
            data = request.get_json() or {}
            query = data.get('query', '')
            max_results = data.get('max_results', 5)
        else:
            query = request.args.get('q', '').strip()
            max_results = int(request.args.get('max_results', 5))
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query parameter required'
            }), 400
        
        results = search_documents(query, max_results)
        
        return jsonify({
            'success': True,
            'query': query,
            'total_results': len(results),
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint"""
    try:
        data = request.get_json() or {}
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({
                'success': False,
                'message': 'Message parameter required'
            }), 400
        
        results = search_documents(message, 3)
        
        if not results:
            response_text = f"No relevant information found for '{message}'. Try different keywords."
        else:
            response_parts = [f"Found {len(results)} results for '{message}':\\n"]
            for i, result in enumerate(results, 1):
                response_parts.append(f"**{i}. {result['file_name']} (Page {result['page_number']})**")
                response_parts.append(result['highlighted_text'][:300] + "...")
                response_parts.append(f"[View Document]({result['url']})\\n")
            response_text = "\\n".join(response_parts)
        
        return jsonify({
            'success': True,
            'message': response_text,
            'query': message,
            'total_results': len(results),
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/options', methods=['OPTIONS'])
def handle_options():
    """Handle preflight requests"""
    return '', 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting PDF Search API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
