#!/bin/bash
# Simplified build script for Render

echo "🚀 Building PDF Search API..."

# Install dependencies
pip install --upgrade pip
pip install flask flask-cors gunicorn

echo "✅ Build completed successfully!"
