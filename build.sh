#!/bin/bash
# Render.com build script for PDF Search API

echo "🚀 Starting build process for PDF Search API..."

# Install Python dependencies
echo "📦 Installing dependencies..."
pip install -r requirements_render.txt

# Try to copy processed data if available
echo "📄 Checking for processed PDF data..."
if [ -f "pdf_search_data.pkl" ]; then
    echo "✅ Found processed PDF data - copying to production app"
    cp pdf_search_data.pkl ./
else
    echo "⚠️ No processed PDF data found - app will use demo data"
fi

echo "✅ Build completed successfully!"
echo "🌐 API will be available at your Render URL"
echo "📖 Documentation will be at: https://your-app.onrender.com/"
