# Railway Deployment Guide

## 🚂 Configuration Overview

This project uses a **monorepo structure** with separate services for frontend and backend.

---

## 📦 Services Setup

### **Backend Service**

**Root Directory:** `/` (leave as root)

**Build Command:** (Custom)
```bash
cd backend && pip install -r requirements.txt
```

**Start Command:** (Custom)
```bash
cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Environment Variables:**
```bash
# Supabase (REQUIRED)
SUPABASE_URL=https://hodawgekwhmbywubydau.supabase.co
SUPABASE_KEY=your_supabase_service_role_key_here

# Port (Railway auto-provides this)
PORT=${{RAILWAY_PORT}}
```

---

### **Frontend Service**

**Root Directory:** `/` (leave as root)

**Build Command:** (Custom)
```bash
cd frontend && npm install && npm run build
```

**Start Command:** (Custom)
```bash
cd frontend && npm start
```

**Environment Variables:**
```bash
# Backend API URL (CRITICAL - must point to Railway backend URL)
NEXT_PUBLIC_API_URL=https://your-backend-service.up.railway.app

# App URL (your frontend URL)
NEXT_PUBLIC_APP_URL=https://your-frontend-service.up.railway.app

# Supabase (optional for direct client access)
NEXT_PUBLIC_SUPABASE_URL=https://hodawgekwhmbywubydau.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhvZGF3Z2Vrd2htYnl3dWJ5ZGF1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkxNjM3MTQsImV4cCI6MjA3NDczOTcxNH0.RK5lxkhBS0LcXAa3PvbTFw5OjCikfm2CMDHp_aA69Jg
```

---

## 🔧 Step-by-Step Deployment

### 1. Create Backend Service
1. Go to Railway project dashboard
2. Click **"New Service"** → **"GitHub Repo"**
3. Select `SuperintelligenceURLs` repo
4. Set **Root Directory**: `/backend`
5. Railway will auto-detect Python and install dependencies
6. Add environment variables (see Backend section above)
7. Deploy will start automatically

### 2. Get Backend URL
1. Once backend deploys, go to **Settings** → **Domains**
2. Click **"Generate Domain"**
3. Copy the URL (e.g., `https://superintelligenceurls-backend.up.railway.app`)

### 3. Create Frontend Service
1. Click **"New Service"** → **"GitHub Repo"**
2. Select `SuperintelligenceURLs` repo again
3. Set **Root Directory**: `/frontend`
4. Add environment variables (see Frontend section above)
   - **IMPORTANT**: Use the backend URL from step 2 for `NEXT_PUBLIC_API_URL`
5. Deploy will start automatically

### 4. Get Frontend URL
1. Once frontend deploys, go to **Settings** → **Domains**
2. Click **"Generate Domain"**
3. Copy the URL (e.g., `https://superintelligenceurls.up.railway.app`)
4. **Update** `NEXT_PUBLIC_APP_URL` with this URL and redeploy

---

## ⚠️ Common Issues

### Backend fails to start
**Error:** `ModuleNotFoundError: No module named 'X'`
**Fix:** Make sure `requirements.txt` is in `/backend` folder

**Error:** `SUPABASE_URL not set`
**Fix:** Add all required environment variables in Railway settings

### Frontend fails to build
**Error:** `Cannot find module 'next'`
**Fix:** Make sure root directory is set to `/frontend`

**Error:** `API calls fail with CORS`
**Fix:** Verify `NEXT_PUBLIC_API_URL` points to correct backend URL

### Frontend shows "Failed to fetch"
**Problem:** Frontend is calling `localhost:8000` instead of Railway backend
**Fix:**
1. Update `NEXT_PUBLIC_API_URL` to Railway backend URL
2. Redeploy frontend service

---

## 🚀 Production Checklist

- [ ] Backend deployed successfully
- [ ] Backend has public domain
- [ ] Frontend `NEXT_PUBLIC_API_URL` points to backend Railway URL
- [ ] Frontend deployed successfully
- [ ] Frontend has public domain
- [ ] Test creating a short URL from production frontend
- [ ] Test redirect from short code works
- [ ] Test analytics dashboard loads

---

## 📊 Monitoring

### View Logs
1. Go to Railway dashboard
2. Click on service (Frontend or Backend)
3. Go to **"Deployments"** tab
4. Click on latest deployment
5. View logs in real-time

### Check Health
- Backend: `https://your-backend.up.railway.app/` (should return JSON)
- Frontend: `https://your-frontend.up.railway.app/` (should show landing page)

---

## 🔄 Redeploying

Railway auto-deploys on git push to `main` branch.

Manual redeploy:
1. Go to service in Railway dashboard
2. Click **"Deployments"** tab
3. Click **"Deploy"** button
4. Or run: `railway up` (if CLI is linked to service)

---

**Project URL:** https://railway.com/project/01a2020f-9dd8-4dd5-a3ae-f32e3694a583
**GitHub Repo:** https://github.com/daniel-carreon/SuperintelligenceURLs
