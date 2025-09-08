#!/bin/bash
# Quick deployment script for Render

echo "🚀 Preparing PDF Search API for Render deployment..."

# Create .gitignore if it doesn't exist
if [ ! -f .gitignore ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Local test files
test_*.py
demo_*.py
simple_app.py
process_pdfs.py

# Keep these for deployment
!render_app.py
!requirements_render.txt
!build.sh
!render.yaml
!Procfile
!DEPLOYMENT_GUIDE.md
EOF
fi

echo "✅ Files prepared for deployment!"
echo ""
echo "📋 Next steps:"
echo "1. Create a GitHub repository"
echo "2. Run these commands:"
echo "   git init"
echo "   git add ."
echo "   git commit -m 'Initial commit - PDF Search API for Render'"
echo "   git branch -M main"
echo "   git remote add origin https://github.com/yourusername/pdf-search-api.git"
echo "   git push -u origin main"
echo ""
echo "3. Go to render.com and deploy from your GitHub repo"
echo "4. Use these settings:"
echo "   - Build Command: chmod +x build.sh && ./build.sh"
echo "   - Start Command: gunicorn --bind 0.0.0.0:\$PORT --workers 1 --timeout 120 render_app:app"
echo ""
echo "🌐 Your API will be available at: https://your-app-name.onrender.com"
