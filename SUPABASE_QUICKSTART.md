# 🚀 SUPABASE INTEGRATION — Quick Start

## ✅ What's Ready

- ✅ Backend authentication routes (`backend/routes/auth.py`) - **Rewritten for Supabase**
- ✅ Frontend auth module (`js/auth.js`) - **Rewritten for Supabase JS client**
- ✅ HTML files updated - **Supabase script tags added to index.html & login.html**
- ✅ Dependencies installed - **`supabase` Python package ready**
- ✅ Environment template created - **`backend/.env` with configuration template**
- ✅ Configuration helper script - **`configure_supabase.py` for easy setup**

---

## 🎯 What You Need to Do

### Step 1: Create Supabase Project (5 min)

```bash
# Go to https://supabase.com and create new project
# Then copy credentials:
# - SUPABASE_URL: https://YOUR_PROJECT_ID.supabase.co
# - SUPABASE_SERVICE_KEY: eyJ... (from Settings → API)
# - SUPABASE_ANON_KEY: eyJ... (from Settings → API - different key!)
```

### Step 2: Configure Backend

```bash
# Option A: Interactive setup (Recommended)
cd backend
python ../configure_supabase.py

# Option B: Manual setup
# Edit backend/.env and fill in:
# SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
# SUPABASE_SERVICE_KEY=eyJ...
```

### Step 3: Create Database Tables

1. Go to Supabase Dashboard → **SQL Editor**
2. Create new query and run SQL from: **SUPABASE_INTEGRATION.md** (Step 2)

### Step 4: Configure Frontend

Edit `index.html` and `login.html` (both already have placeholders):

```html
<script>
  window.SUPABASE_URL = 'https://YOUR_PROJECT_ID.supabase.co';
  window.SUPABASE_ANON_KEY = 'eyJ... (ANON KEY)';
</script>
```

### Step 5: Test Auth Flow

```bash
# Start backend
cd backend
python app.py

# Open in browser
# http://localhost:5000/login.html
# → Sign up → Test registration
# → Login → Test login
```

---

## 📁 Files Modified/Created

| File | Status | Purpose |
|------|--------|---------|
| `backend/routes/auth.py` | ✅ Updated | Supabase auth endpoints |
| `js/auth.js` | ✅ Updated | Supabase client SDK |
| `index.html` | ✅ Updated | Added Supabase script tag |
| `login.html` | ✅ Updated | Added Supabase script tag |
| `backend/.env` | ✅ Created | Configuration template |
| `backend/requirements.txt` | ✅ Updated | Added supabase dependency |
| `SUPABASE_INTEGRATION.md` | ✅ Created | Comprehensive guide |
| `configure_supabase.py` | ✅ Created | Interactive setup helper |

---

## 🔐 Key Changes

### Authentication Providers

- ❌ **Old:** Local bcrypt + MongoDB users collection
- ✅ **New:** Supabase managed Auth + PostgreSQL users table

### Token Management

- **Backend:** Uses Supabase Service Role Key (server-only, in .env)
- **Frontend:** Uses Supabase Anon Key (client-safe, in index.html)
- **Sessions:** JWT tokens stored in sessionStorage + localStorage

### User Data

- **Location:** PostgreSQL (public.users table in Supabase)
- **RLS:** Row-level security enabled for privacy
- **Sync:** Cart transfers to user on first login

---

## 🧪 Validation Commands

```bash
# Check if Supabase is configured
python configure_supabase.py validate

# Check if package is installed
pip list | findstr supabase

# Test backend can import Supabase
python -c "from supabase import create_client; print('✅ Supabase import successful')"
```

---

## 📋 Credentials Reference

You'll need 3 pieces from Supabase:

| Credential | Where | Use | Secret? |
|-----------|-------|-----|---------|
| **URL** | Settings → API | Both frontend & backend | ❌ No |
| **Anon Key** | Settings → API (public key) | Frontend ONLY | ❌ No |
| **Service Role Key** | Settings → API (secret) | Backend ONLY | ✅ YES |

⚠️ **NEVER put Service Role Key in frontend code!**

---

## 🚨 Common Issues

### "Supabase is not defined"

- Missing `<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>` in HTML
- Check index.html & login.html have the script tag

### "Invalid Supabase URL"

- Make sure SUPABASE_URL in .env has proper format: `https://[project-id].supabase.co`
- Check no trailing slash or extra spaces

### "Invalid authentication credentials"

- Wrong ANON_KEY in frontend (need to get from Supabase → Settings → API)
- Wrong SERVICE_KEY in backend (need to get from Supabase → Settings → API)

### "Column 'auth.uid()' does not exist"

- Database tables not created yet
- Run SQL from SUPABASE_INTEGRATION.md Step 2

### "User already registered"

- This email exists in Supabase Auth
- Try with different email or reset in Supabase dashboard

---

## 📚 Detailed Guides

For complete setup instructions, see:

- **SUPABASE_INTEGRATION.md** - Full 7-step integration guide with SQL scripts

For quick reference:

- **This file** - Quick start checklist
- **backend/.env** - Environment variables template
- **configure_supabase.py** - Interactive configuration

---

## ✨ Features Now Available

- ✅ Email verification (users verify email before login)
- ✅ Password reset (users receive reset link via email)
- ✅ Secure sessions (Supabase manages JWT tokens)
- ✅ User profiles (data stored in PostgreSQL)
- ✅ Row-level security (users can only access their own data)
- ✅ Admin management (easily manage users in Supabase dashboard)

---

## 🚀 Ready to Deploy?

Before deploying to production:

1. ✅ Create Supabase project (done by you)
2. ✅ Configure environment variables (backend/.env)
3. ✅ Update frontend credentials (index.html, login.html)
4. ✅ Test registration → login → profile flows
5. ✅ Configure custom email templates in Supabase
6. ✅ Enable CORS for your domain in Supabase
7. ✅ Set up backups in Supabase
8. ✅ Test on production domain

---

**Questions?** Check SUPABASE_INTEGRATION.md or Supabase docs: <https://supabase.com/docs>
