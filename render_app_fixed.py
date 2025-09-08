#!/usr/bin/env python3
"""
Fixed Flask API for Render deployment
Simplified to avoid common deployment issues
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import re
import json
from typing import List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global variables to store documents
DOCUMENTS = [
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
    },
    {
        'file_name': 'Individual-Rights-GDPR.pdf',
        'file_path': 'demo/Individual-Rights.pdf',
        'page_number': 1,
        'paragraph_index': 0,
        'text': 'Individual rights under GDPR include the right of access, right to rectification, right to erasure (right to be forgotten), right to restrict processing, right to data portability, right to object, and rights related to automated decision making and profiling.',
        'url': 'https://example.com/individual-rights.pdf#page=1'
    }
]

def highlight_text(text: str, query: str) -> str:
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

def search_documents(query: str, top_k: int = 5) -> List[Dict]:
    """Simple text search through documents"""
    query_lower = query.lower()
    query_terms = [term for term in query_lower.split() if len(term) > 2]
    
    if not query_terms:
        return []
    
    results = []
    
    for doc in DOCUMENTS:
        text_lower = doc['text'].lower()
        
        # Calculate relevance score
        score = 0
        matches = 0
        
        for term in query_terms:
            count = text_lower.count(term)
            if count > 0:
                score += count * len(term) * 2
                matches += 1
        
        if matches > 1:
            score *= (1 + matches * 0.2)
        
        if score > 0:
            doc_copy = doc.copy()
            doc_copy['relevance_score'] = min(score / len(doc['text']), 1.0)
            doc_copy['highlighted_text'] = highlight_text(doc['text'], query)
            doc_copy['match_count'] = matches
            results.append(doc_copy)
    
    # Sort by relevance score
    results.sort(key=lambda x: (x['relevance_score'], x['match_count']), reverse=True)
    return results[:top_k]

@app.route('/')
def home():
    """Home page with API documentation"""
    base_url = request.host_url.rstrip('/')
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>PDF Search API</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f7fa; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
            .status {{ background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .endpoint {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }}
            .method {{ color: #007acc; font-weight: bold; }}
            a {{ color: #007acc; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📄 PDF Search API</h1>
            <div class="status">
                <h3>✅ Status: Online</h3>
                <p>Documents: {len(DOCUMENTS)} available</p>
                <p>Base URL: {base_url}</p>
            </div>
            
            <h2>🔌 API Endpoints</h2>
            
            <div class="endpoint">
                <h3><span class="method">GET</span> /health</h3>
                <p><a href="/health">Test Health Check</a></p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method">GET</span> /search</h3>
                <p>Power Automate Compatible</p>
                <p><a href="/search?q=GDPR&max_results=3">Test: Search for "GDPR"</a></p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method">POST</span> /chat</h3>
                <p>Copilot Studio Compatible</p>
            </div>
            
            <h2>🔗 Integration URLs</h2>
            <p><strong>Power Automate:</strong> {base_url}/search?q=[query]&max_results=5</p>
            <p><strong>Copilot Studio:</strong> {base_url}/chat (POST)</p>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'PDF Search API',
        'documents_count': len(DOCUMENTS),
        'version': '1.0.0'
    })

@app.route('/search', methods=['GET', 'POST'])
def search():
    """Search endpoint"""
    try:
        if request.method == 'POST':
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No JSON data'}), 400
            query = data.get('query', '')
            max_results = data.get('max_results', 5)
        else:
            query = request.args.get('q', '').strip()
            max_results = int(request.args.get('max_results', 5))
        
        if not query:
            return jsonify({'success': False, 'error': 'Query required'}), 400
        
        results = search_documents(query, max_results)
        
        return jsonify({
            'success': True,
            'query': query,
            'total_results': len(results),
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint for Copilot Studio"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No JSON data'}), 400
        
        message = data.get('message', '').strip()
        if not message:
            return jsonify({'success': False, 'message': 'Message required'}), 400
        
        results = search_documents(message, 3)
        
        if not results:
            return jsonify({
                'success': True,
                'message': f"No relevant information found for '{message}'. Try different keywords.",
                'results': []
            })
        
        # Format response
        response_text = f"Found {len(results)} results for '{message}':\\n\\n"
        for i, result in enumerate(results, 1):
            response_text += f"**{i}. {result['file_name']} (Page {result['page_number']})**\\n"
            response_text += f"{result['highlighted_text'][:300]}...\\n"
            response_text += f"[View Document]({result['url']})\\n\\n"
        
        return jsonify({
            'success': True,
            'message': response_text,
            'query': message,
            'total_results': len(results),
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting PDF Search API on port {port}")
    app.run(host='0.0.0.0', port=port)
