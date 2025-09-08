#!/usr/bin/env python3
"""
PDF Processing Script - Extracts text from PDFs and creates search indices
This script replicates the functionality of the Jupyter notebook
"""

import os
import glob
import pickle
import re
from typing import List, Dict
import pandas as pd

try:
    import fitz  # pymupdf
    print("✅ PyMuPDF imported successfully")
except ImportError:
    print("❌ PyMuPDF not available, trying PyPDF2...")
    import PyPDF2
    fitz = None

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    ML_AVAILABLE = True
    print("✅ Machine learning packages available")
except ImportError:
    ML_AVAILABLE = False
    print("⚠️ Machine learning packages not available - using basic search")

class PDFSearchSystem:
    def __init__(self, pdf_directory="."):
        self.pdf_directory = pdf_directory
        self.documents = []
        self.embeddings = None
        self.index = None
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        
        self.ML_AVAILABLE = ML_AVAILABLE
        if self.ML_AVAILABLE:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                self.tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
                print("✅ ML models initialized")
            except Exception as e:
                print(f"⚠️ ML model initialization failed: {e}")
                self.ML_AVAILABLE = False
        
    def extract_text_from_pdf_pymupdf(self, pdf_path: str) -> List[Dict]:
        """Extract text using PyMuPDF"""
        documents = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                if text.strip():
                    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
                    
                    for i, paragraph in enumerate(paragraphs):
                        if len(paragraph) > 50:
                            documents.append({
                                'file_name': os.path.basename(pdf_path),
                                'file_path': pdf_path,
                                'page_number': page_num + 1,
                                'paragraph_index': i,
                                'text': paragraph,
                                'url': self.generate_pdf_url(pdf_path, page_num + 1)
                            })
            
            doc.close()
            
        except Exception as e:
            print(f"Error processing {pdf_path} with PyMuPDF: {str(e)}")
            
        return documents
    
    def extract_text_from_pdf_pypdf2(self, pdf_path: str) -> List[Dict]:
        """Extract text using PyPDF2 as fallback"""
        documents = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    if text.strip():
                        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
                        
                        for i, paragraph in enumerate(paragraphs):
                            if len(paragraph) > 50:
                                documents.append({
                                    'file_name': os.path.basename(pdf_path),
                                    'file_path': pdf_path,
                                    'page_number': page_num + 1,
                                    'paragraph_index': i,
                                    'text': paragraph,
                                    'url': self.generate_pdf_url(pdf_path, page_num + 1)
                                })
                                
        except Exception as e:
            print(f"Error processing {pdf_path} with PyPDF2: {str(e)}")
            
        return documents
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict]:
        """Extract text from PDF with fallback methods"""
        if fitz:
            documents = self.extract_text_from_pdf_pymupdf(pdf_path)
        else:
            documents = self.extract_text_from_pdf_pypdf2(pdf_path)
        
        print(f"Extracted {len(documents)} paragraphs from {os.path.basename(pdf_path)}")
        return documents
    
    def generate_pdf_url(self, pdf_path: str, page_number: int) -> str:
        """Generate a URL that opens PDF at specific page"""
        abs_path = os.path.abspath(pdf_path)
        file_url = f"file:///{abs_path.replace(os.sep, '/')}"
        return f"{file_url}#page={page_number}"
    
    def load_all_pdfs(self):
        """Load all PDF files from directory and subdirectories"""
        pdf_files = []
        
        # Find all PDF files
        for root, dirs, files in os.walk(self.pdf_directory):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))
        
        print(f"Found {len(pdf_files)} PDF files")
        for pdf_file in pdf_files:
            print(f"  - {os.path.basename(pdf_file)}")
        
        # Extract text from all PDFs
        all_documents = []
        for pdf_file in pdf_files:
            docs = self.extract_text_from_pdf(pdf_file)
            all_documents.extend(docs)
        
        self.documents = all_documents
        print(f"\n📊 Total paragraphs extracted: {len(self.documents)}")
        
        return self.documents
    
    def create_embeddings(self):
        """Create embeddings for all documents"""
        if not self.documents:
            print("No documents loaded. Please run load_all_pdfs() first.")
            return False
        
        if not self.ML_AVAILABLE:
            print("⚠️ Machine learning packages not available - skipping embeddings")
            return False
        
        try:
            print("Creating embeddings...")
            texts = [doc['text'] for doc in self.documents]
            
            # Create sentence embeddings
            self.embeddings = self.model.encode(texts)
            
            # Create FAISS index for fast similarity search
            dimension = self.embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(self.embeddings)
            self.index.add(self.embeddings)
            
            # Create TF-IDF matrix for keyword-based search
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
            
            print("✅ Embeddings created successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error creating embeddings: {e}")
            return False
    
    def highlight_text(self, text: str, query: str) -> str:
        """Highlight query terms in text"""
        query_terms = query.lower().split()
        highlighted_text = text
        
        for term in query_terms:
            if len(term) > 2:
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                highlighted_text = pattern.sub(
                    f'<mark style="background-color: yellow; padding: 2px;">{term}</mark>',
                    highlighted_text
                )
        
        return highlighted_text
    
    def search_basic(self, query: str, top_k: int = 5) -> List[Dict]:
        """Basic text search without ML"""
        query_lower = query.lower()
        results = []
        
        for doc in self.documents:
            if any(term in doc['text'].lower() for term in query_lower.split()):
                doc_copy = doc.copy()
                doc_copy['relevance_score'] = 0.5  # Basic score
                doc_copy['highlighted_text'] = self.highlight_text(doc['text'], query)
                results.append(doc_copy)
        
        # Sort by text length as a simple relevance measure
        results.sort(key=lambda x: len(x['text']), reverse=True)
        return results[:top_k]
    
    def search_ml(self, query: str, top_k: int = 5, hybrid_weight: float = 0.7) -> List[Dict]:
        """ML-based search with embeddings"""
        if self.embeddings is None:
            print("Embeddings not created. Using basic search.")
            return self.search_basic(query, top_k)
        
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
            
            # Combine scores
            final_scores = {}
            
            for i, idx in enumerate(semantic_indices):
                if idx < len(self.documents):
                    final_scores[idx] = hybrid_weight * semantic_scores[i]
            
            for idx, score in enumerate(keyword_scores):
                if idx in final_scores:
                    final_scores[idx] += (1 - hybrid_weight) * score
                else:
                    final_scores[idx] = (1 - hybrid_weight) * score
            
            # Sort by combined score
            sorted_results = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
            
            results = []
            for idx, score in sorted_results:
                doc = self.documents[idx].copy()
                doc['relevance_score'] = float(score)
                doc['highlighted_text'] = self.highlight_text(doc['text'], query)
                results.append(doc)
            
            return results
            
        except Exception as e:
            print(f"ML search error: {e}")
            return self.search_basic(query, top_k)
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Main search function"""
        if self.ML_AVAILABLE and self.embeddings is not None:
            return self.search_ml(query, top_k)
        else:
            return self.search_basic(query, top_k)

def main():
    print("🔍 PDF Search System - Processing PDFs")
    print("=" * 50)
    
    # Initialize system
    pdf_search = PDFSearchSystem(".")
    
    # Load PDFs
    documents = pdf_search.load_all_pdfs()
    
    if not documents:
        print("❌ No PDF documents found or processed successfully.")
        return False
    
    # Display summary
    df = pd.DataFrame(documents)
    print("\n📋 Document Summary")
    print("-" * 30)
    print(f"Total paragraphs: {len(documents)}")
    print("\nDocuments by file:")
    print(df['file_name'].value_counts())
    print("\nPages covered:")
    for file_name in df['file_name'].unique():
        file_docs = df[df['file_name'] == file_name]
        print(f"  {file_name}: Pages {file_docs['page_number'].min()}-{file_docs['page_number'].max()}")
    
    # Create embeddings
    embeddings_created = pdf_search.create_embeddings()
    
    # Test search
    print("\n🧪 Testing Search Functionality")
    print("-" * 35)
    test_queries = ["data protection", "GDPR compliance", "individual rights"]
    
    for query in test_queries:
        print(f"\nTesting query: '{query}'")
        results = pdf_search.search(query, top_k=2)
        print(f"Found {len(results)} results")
        
        if results:
            first_result = results[0]
            print(f"  Top result: {first_result['file_name']} (Page {first_result['page_number']})")
            print(f"  Relevance: {first_result['relevance_score']:.3f}")
    
    # Save data for Flask API
    print("\n💾 Saving Search Data")
    print("-" * 25)
    
    search_data = {
        'documents': pdf_search.documents,
        'embeddings': pdf_search.embeddings,
        'tfidf_vectorizer': pdf_search.tfidf_vectorizer,
        'tfidf_matrix': pdf_search.tfidf_matrix
    }
    
    try:
        with open('pdf_search_data.pkl', 'wb') as f:
            pickle.dump(search_data, f)
        print("✅ Search data saved successfully to 'pdf_search_data.pkl'")
        print("   This file will be used by the Flask API.")
        return True
    except Exception as e:
        print(f"❌ Error saving search data: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 PDF processing completed successfully!")
        print("You can now run the Flask API: python app.py")
    else:
        print("\n❌ PDF processing failed. Please check the error messages above.")
