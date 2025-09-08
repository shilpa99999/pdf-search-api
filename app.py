#!/usr/bin/env python3
"""
Production Flask API for Render deployment
Ultra-minimal version with only Flask and Gunicorn
"""

from flask import Flask, request, jsonify
import os
import re

app = Flask(__name__)

# Manual CORS implementation
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# GDPR Documents with SharePoint URLs
DOCUMENTS = [
    {
        'file_name': 'IC-GDPR-Compliance-Manual-Final_03_21.pdf',
        'page_number': 1,
        'text': 'GDPR Compliance Manual Final 03_21. This comprehensive document provides detailed guidance on GDPR compliance requirements, data protection principles, individual rights under the regulation, and implementation strategies for organizations.',
        'url': 'https://4ciusa.sharepoint.com/:b:/s/4ConsultingInc/EeQeUyussbhPuu1rsUudHeoBiCJ0kF6n5QHxfo8D7RAh2A?e=1xN8ld'
    },
    {
        'file_name': 'GDPR-Final-EPSU.pdf',
        'page_number': 1,
        'text': 'GDPR Final EPSU document. European Public Service Union guidance on General Data Protection Regulation implementation, covering data protection principles, employee rights, and organizational compliance measures.',
        'url': 'https://4ciusa.sharepoint.com/:b:/s/4ConsultingInc/EWmQegZF3d1Orxp6erD-evkB6zWDz85NJid5N3DYJf950w?e=OZgzm2'
    },
    {
        'file_name': 'LW-Privacy-GDPR-Compliance-Checklist.pdf',
        'page_number': 1,
        'text': 'Privacy GDPR Compliance Checklist. A comprehensive checklist for organizations to ensure GDPR compliance, covering data protection impact assessments, consent management, data subject rights, and privacy by design principles.',
        'url': 'https://4ciusa.sharepoint.com/:b:/s/4ConsultingInc/ETtl-ZcFufVIuN6VwRGCLYMB8hYh53gYIGl7ybYCIElLEg?e=KHDM9m'
    },
    {
        'file_name': 'Regulation-of-European-Parliament.pdf',
        'page_number': 1,
        'text': 'Regulation of European Parliament on data protection. Official regulation text covering the protection of natural persons with regard to the processing of personal data and on the free movement of such data.',
        'url': 'https://4ciusa.sharepoint.com/:b:/s/4ConsultingInc/EaeQ3ZsLSaFJnq0PgMp0SDoBGKRxrWL_E4Zh21rW9wVTtw?e=k2gmIr'
    },
    {
        'file_name': 'Rights-of-Individuals-under-the-General-Data-Protection-RegulationAmendedApril.pdf',
        'page_number': 1,
        'text': 'Rights of Individuals under the General Data Protection Regulation (Amended April). Detailed guide covering individual rights including access, rectification, erasure, data portability, restriction of processing, and objection to processing.',
        'url': 'https://4ciusa.sharepoint.com/:b:/s/4ConsultingInc/EQy-AD8NoFFFk6DeUfOi1AMBhdoZvsO0Its6LCtYtasxUA?e=4QgvMx'
    },
    {
        'file_name': 'Data-Processing-Agreement-Template.pdf',
        'page_number': 1,
        'text': 'Data Processing Agreement Template for GDPR compliance. This template establishes the relationship between data controllers and data processors, defining responsibilities, security measures, breach notification procedures, and contractual safeguards.',
        'url': 'https://4ciusa.sharepoint.com/:b:/s/4ConsultingInc/EeQeUyussbhPuu1rsUudHeoBiCJ0kF6n5QHxfo8D7RAh2A?e=1xN8ld'
    },
    {
        'file_name': 'GDPR-Consent-Requirements.pdf',
        'page_number': 1,
        'text': 'GDPR Consent Requirements and best practices. Consent under GDPR must be freely given, specific, informed and unambiguous. Controllers must be able to demonstrate that consent was given, and individuals have the right to withdraw consent at any time.',
        'url': 'https://4ciusa.sharepoint.com/:b:/s/4ConsultingInc/EeQeUyussbhPuu1rsUudHeoBiCJ0kF6n5QHxfo8D7RAh2A?e=1xN8ld'
    },
    {
        'file_name': 'Data-Protection-Principles.pdf',
        'page_number': 1,
        'text': 'Key data protection principles under GDPR including lawfulness, fairness and transparency, purpose limitation, data minimisation, accuracy, storage limitation, integrity and confidentiality, and accountability. Organizations must demonstrate compliance with these principles.',
        'url': 'https://4ciusa.sharepoint.com/:b:/s/4ConsultingInc/EaeQ3ZsLSaFJnq0PgMp0SDoBGKRxrWL_E4Zh21rW9wVTtw?e=k2gmIr'
    }
]

def highlight_text(text, query):
    """Add yellow highlighting to matching terms"""
    words = [w.strip() for w in query.lower().split() if len(w.strip()) > 2]
    result = text
    for word in words:
        if word:
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            result = pattern.sub(f'<mark style="background-color: yellow; padding: 2px; border-radius: 3px;">{word}</mark>', result)
    return result

def search_documents(query, max_results=5):
    """Search through documents"""
    if not query or len(query.strip()) < 2:
        return []
    
    query_lower = query.lower().strip()
    query_words = [w for w in query_lower.split() if len(w) > 2]
    
    if not query_words:
        return []
    
    results = []
    
    for doc in DOCUMENTS:
        text_lower = doc['text'].lower()
        score = 0
        matches = 0
        
        # Calculate relevance score
        for word in query_words:
            count = text_lower.count(word)
            if count > 0:
                score += count * len(word)
                matches += 1
        
        if matches > 0:
            doc_copy = doc.copy()
            doc_copy['relevance_score'] = round(min(score / len(doc['text']), 1.0), 3)
            doc_copy['highlighted_text'] = highlight_text(doc['text'], query)
            doc_copy['match_count'] = matches
            results.append(doc_copy)
    
    # Sort by relevance score
    results.sort(key=lambda x: (x['relevance_score'], x['match_count']), reverse=True)
    return results[:max_results]

@app.route('/')
def home():
    """API documentation homepage"""
    base_url = request.host_url.rstrip('/')
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>PDF Search API - Live</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
            .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .status {{ background: linear-gradient(135deg, #4CAF50, #45a049); color: white; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center; }}
            .endpoint {{ background: #f8f9fa; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #007bff; }}
            .method {{ background: #007bff; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }}
            .url {{ background: #e9ecef; padding: 10px; border-radius: 4px; font-family: 'Courier New', monospace; margin: 10px 0; word-break: break-all; }}
            a {{ color: #007bff; text-decoration: none; font-weight: 500; }}
            a:hover {{ text-decoration: underline; }}
            .integration {{ background: #fff3cd; border: 1px solid #ffc107; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            h1 {{ color: #333; margin-bottom: 10px; }}
            h2 {{ color: #007bff; border-bottom: 2px solid #e9ecef; padding-bottom: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📄 PDF Search API</h1>
                <p>Intelligent document search with highlighting and citations</p>
            </div>
            
            <div class="status">
                <h3>🎉 Status: LIVE & READY</h3>
                <p><strong>Documents:</strong> {len(DOCUMENTS)} available | <strong>Base URL:</strong> {base_url}</p>
            </div>
            
            <h2>🔌 API Endpoints</h2>
            
            <div class="endpoint">
                <h3><span class="method">GET</span> /health</h3>
                <p>System health check</p>
                <div class="url">{base_url}/health</div>
                <p><a href="/health" target="_blank">🧪 Test Health Check</a></p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method">GET</span> /search</h3>
                <p>Search documents (Power Automate compatible)</p>
                <div class="url">{base_url}/search?q=GDPR&max_results=5</div>
                <p><strong>Parameters:</strong> q (query), max_results (optional)</p>
                <p><a href="/search?q=GDPR%20principles&max_results=3" target="_blank">🧪 Test Search</a></p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method">POST</span> /search</h3>
                <p>Advanced search with JSON</p>
                <div class="url">{base_url}/search</div>
                <p><strong>Body:</strong> {{"query": "data protection", "max_results": 5}}</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method">POST</span> /chat</h3>
                <p>Conversational search (Copilot Studio compatible)</p>
                <div class="url">{base_url}/chat</div>
                <p><strong>Body:</strong> {{"message": "What are individual rights under GDPR?"}}</p>
            </div>
            
            <div class="integration">
                <h3>🔗 Power Automate Integration</h3>
                <p><strong>HTTP Request:</strong></p>
                <ul>
                    <li><strong>Method:</strong> GET</li>
                    <li><strong>URI:</strong> <code>{base_url}/search</code></li>
                    <li><strong>Query:</strong> q = [Dynamic Content], max_results = 5</li>
                </ul>
            </div>
            
            <div class="integration">
                <h3>🤖 Copilot Studio Integration</h3>
                <p><strong>HTTP Request:</strong></p>
                <ul>
                    <li><strong>Method:</strong> POST</li>
                    <li><strong>URI:</strong> <code>{base_url}/chat</code></li>
                    <li><strong>Headers:</strong> Content-Type: application/json</li>
                    <li><strong>Body:</strong> {{"message": "[Dynamic Content]"}}</li>
                </ul>
            </div>
            
            <h2>✨ Features</h2>
            <ul>
                <li>🟡 <strong>Yellow Highlighting:</strong> Query terms highlighted in results</li>
                <li>📄 <strong>Citations:</strong> Page numbers and document names</li>
                <li>🔗 <strong>Clickable URLs:</strong> Direct links to PDF pages</li>
                <li>⚡ <strong>Fast Search:</strong> Instant results</li>
                <li>🌐 <strong>CORS Enabled:</strong> Web integration ready</li>
                <li>🔧 <strong>JSON API:</strong> Structured responses</li>
            </ul>
        </div>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'PDF Search API',
        'version': '1.0.0',
        'documents_count': len(DOCUMENTS),
        'endpoints': ['/health', '/search', '/chat'],
        'message': 'API is running and ready for integration'
    })

@app.route('/search', methods=['GET', 'POST'])
def search():
    """Main search endpoint"""
    try:
        # Handle both GET and POST requests
        if request.method == 'POST':
            data = request.get_json() or {}
            query = data.get('query', '').strip()
            max_results = min(int(data.get('max_results', 5)), 20)
        else:
            query = request.args.get('q', '').strip()
            try:
                max_results = min(int(request.args.get('max_results', 5)), 20)
            except (ValueError, TypeError):
                max_results = 5
        
        # Validate query
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query parameter is required'
            }), 400
        
        if len(query) < 2:
            return jsonify({
                'success': False,
                'error': 'Query must be at least 2 characters long'
            }), 400
        
        # Perform search
        results = search_documents(query, max_results)
        
        # Return results
        return jsonify({
            'success': True,
            'query': query,
            'total_results': len(results),
            'max_results': max_results,
            'results': results,
            'api_version': '1.0.0'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Search failed: {str(e)}',
            'query': query if 'query' in locals() else 'unknown'
        }), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint for conversational queries"""
    try:
        data = request.get_json() or {}
        message = data.get('message', '').strip()
        max_results = min(int(data.get('max_results', 3)), 10)
        
        if not message:
            return jsonify({
                'success': False,
                'message': 'Message parameter is required'
            }), 400
        
        if len(message) < 3:
            return jsonify({
                'success': False,
                'message': 'Message must be at least 3 characters long'
            }), 400
        
        # Search for relevant documents
        results = search_documents(message, max_results)
        
        if not results:
            response_text = f"I couldn't find any relevant information about '{message}' in the available PDF documents. Please try rephrasing your question or using different keywords."
        else:
            response_parts = [f"I found {len(results)} relevant result{'s' if len(results) != 1 else ''} for your question about '{message}':\\n"]
            
            for i, result in enumerate(results, 1):
                response_parts.append(f"**{i}. {result['file_name']} (Page {result['page_number']})**")
                
                # Truncate text for chat response
                text = result['highlighted_text']
                if len(text) > 300:
                    text = text[:300] + "..."
                
                response_parts.append(text)
                response_parts.append(f"[📄 View Document]({result['url']})\\n")
            
            response_text = "\\n".join(response_parts)
        
        return jsonify({
            'success': True,
            'message': response_text,
            'query': message,
            'total_results': len(results),
            'results': results,
            'response_type': 'conversational'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Sorry, I encountered an error: {str(e)}',
            'error_type': 'internal_error'
        }), 500

@app.route('/options', methods=['OPTIONS'])
def handle_options():
    """Handle preflight CORS requests"""
    return '', 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'available_endpoints': ['/health', '/search', '/chat']
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting PDF Search API on port {port}")
    print(f"📄 {len(DOCUMENTS)} documents loaded")
    app.run(host='0.0.0.0', port=port, debug=False)