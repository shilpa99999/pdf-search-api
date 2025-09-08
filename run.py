#!/usr/bin/env python3
"""
Simple startup script for PDF Search System
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import flask
        import sentence_transformers
        import faiss
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_data_file():
    """Check if PDF search data exists"""
    if os.path.exists('pdf_search_data.pkl'):
        print("✅ PDF search data found")
        return True
    else:
        print("❌ PDF search data not found")
        print("Please run the Jupyter notebook first: jupyter notebook pdf_search_system.ipynb")
        return False

def main():
    print("🚀 PDF Search System Startup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check data file
    if not check_data_file():
        print("\n💡 To get started:")
        print("1. Run: jupyter notebook pdf_search_system.ipynb")
        print("2. Execute all cells to process your PDFs")
        print("3. Then run this script again")
        sys.exit(1)
    
    print("\n🌐 Starting Flask API server...")
    print("📍 API Documentation: http://localhost:5000")
    print("💬 Chat Interface: http://localhost:5000/chat-ui")
    print("\n" + "=" * 40)
    
    # Start the Flask app
    os.environ['FLASK_APP'] = 'app.py'
    subprocess.run([sys.executable, 'app.py'])

if __name__ == "__main__":
    main()
