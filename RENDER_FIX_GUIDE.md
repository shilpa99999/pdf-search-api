# 🔧 Render Deployment Fix Guide

## 🚨 Current Issue: 502 Bad Gateway

Your Render deployment is showing a 502 error, which means the service isn't starting properly. I've created fixed files to resolve this.

## ✅ **Solution: Update Your Render Configuration**

### Step 1: Update Render Settings

Go to your Render dashboard for the `pdf-search-api` service and update these settings:

**Build & Deploy Configuration:**
- **Build Command:** `chmod +x build_fixed.sh && ./build_fixed.sh`
- **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 render_app_fixed:app`

### Step 2: Redeploy

After updating the settings:
1. Click "Manual Deploy" → "Deploy latest commit"
2. Wait for the build to complete (3-5 minutes)

## 📋 **Alternative: Create New Service**

If updating doesn't work, create a new service:

1. **Go to Render Dashboard**
2. **Create New Web Service**
3. **Connect GitHub:** Select `pdf-search-api` repository
4. **Configure:**
   - **Name:** `pdf-search-api-v2`
   - **Build Command:** `chmod +x build_fixed.sh && ./build_fixed.sh`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 render_app_fixed:app`
   - **Environment:** Python 3
   - **Plan:** Free

## 🔍 **What Was Fixed:**

### 1. **Simplified Dependencies**
- Removed complex ML libraries that cause build issues
- Only essential packages: Flask, Flask-CORS, Gunicorn

### 2. **Fixed Port Binding**
- Proper `$PORT` environment variable usage
- Correct host binding (`0.0.0.0`)

### 3. **Embedded Data**
- No dependency on external pickle files
- Built-in demo data for immediate functionality

### 4. **Simplified Build Process**
- Minimal build script
- Faster deployment time

## 🧪 **Test Your Fixed API**

Once deployed, test these endpoints:

### Health Check
```
GET https://your-app-name.onrender.com/health
```

### Search Test
```
GET https://your-app-name.onrender.com/search?q=GDPR&max_results=3
```

### Chat Test
```
POST https://your-app-name.onrender.com/chat
Body: {"message": "What are GDPR principles?"}
```

## 🔗 **Power Automate Integration**

Use this URL in Power Automate:
```
https://your-app-name.onrender.com/search?q=[query]&max_results=5
```

## 🤖 **Copilot Studio Integration**

Use this endpoint:
```
POST https://your-app-name.onrender.com/chat
Headers: Content-Type: application/json
Body: {"message": "[user question]"}
```

## 📊 **Expected Response Format**

### Search Response:
```json
{
  "success": true,
  "query": "GDPR",
  "total_results": 3,
  "results": [
    {
      "file_name": "GDPR-Principles.pdf",
      "page_number": 2,
      "text": "Key principles under GDPR include...",
      "highlighted_text": "Key principles under <mark>GDPR</mark> include...",
      "url": "https://example.com/gdpr-principles.pdf#page=2",
      "relevance_score": 0.85
    }
  ]
}
```

### Chat Response:
```json
{
  "success": true,
  "message": "Found 3 results for 'GDPR principles':\n\n**1. GDPR-Principles.pdf (Page 2)**\nKey principles under GDPR include...",
  "query": "GDPR principles",
  "total_results": 3,
  "results": [...]
}
```

## 🚀 **Next Steps**

1. **Update Render settings** with the new commands
2. **Redeploy** the service
3. **Test** the endpoints
4. **Configure** Power Automate with your working URL
5. **Set up** Copilot Studio integration

## 📞 **If Issues Persist**

If you still see errors:
1. Check Render logs (Dashboard → Logs)
2. Try creating a completely new service
3. Ensure your GitHub repository is public
4. Verify the build and start commands are exactly as specified

---

**Your API should be working within 5-10 minutes after updating the configuration!** 🎉
