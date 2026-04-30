# SUPABASE AUTHENTICATION INTEGRATION GUIDE

## 🎯 Overview

Your Flavour Fleet application now uses **Supabase** for authentication instead of local bcrypt + MongoDB.

**Benefits:**

- ✅ Enterprise-grade authentication
- ✅ Built-in email verification
- ✅ Password reset emails
- ✅ MFA support (ready)
- ✅ Session management
- ✅ Secure token handling
- ✅ User profiles in PostgreSQL

---

## 📋 STEP 1: Create Supabase Project

### 1a. Go to Supabase

- Visit <https://supabase.com>
- Sign up or log in

### 1b. Create New Project

1. Click "New Project"
2. **Project name:** `flavour-fleet`
3. **Database password:** (Create strong password - you'll need it)
4. **Region:** Choose closest to your users
5. Click "Create new project"
6. ⏳ Wait 1-2 minutes for project initialization

### 1c. Get Your Credentials

Once project is ready:

1. Go to **Settings → API**
2. Copy and save these:
   - **URL:** `https://[project-id].supabase.co`
   - **Anon Key:** (long string starting with `eyJ`)
   - **Service Role Key:** (long string - keep SECRET)

---

## 🔧 STEP 2: Set Up Database Tables

### 2a. Create Users Table

1. Go to Supabase Dashboard → **SQL Editor**
2. Click **New Query**
3. Copy and paste this SQL:

```sql
-- Create users table (extends auth.users)
CREATE TABLE IF NOT EXISTS public.users (
  id UUID PRIMARY KEY DEFAULT auth.uid(),
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  phone TEXT DEFAULT '',
  address TEXT DEFAULT '',
  avatar_url TEXT,
  role TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin', 'restaurant')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  FOREIGN KEY (id) REFERENCES auth.users(id) ON DELETE CASCADE
);

-- Enable Row Level Security
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read their own data
CREATE POLICY "Users can read own profile"
  ON public.users FOR SELECT
  USING (auth.uid() = id);

-- Policy: Users can update their own data
CREATE POLICY "Users can update own profile"
  ON public.users FOR UPDATE
  USING (auth.uid() = id);

-- Policy: Admins can read all profiles
CREATE POLICY "Admins can read all profiles"
  ON public.users FOR SELECT
  USING (EXISTS (
    SELECT 1 FROM public.users
    WHERE id = auth.uid() AND role = 'admin'
  ));

-- Create indexes for performance
CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_users_role ON public.users(role);
CREATE INDEX idx_users_created_at ON public.users(created_at DESC);
```

1. Click **Run**
2. ✅ Tables created successfully

---

## 🌐 STEP 3: Configure Environment Variables

### Backend (.env)

1. Open `backend/.env`
2. Replace with your Supabase credentials:

```
SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
SUPABASE_SERVICE_KEY=eyJ... (Service Role Key)
```

### Frontend (index.html & login.html)

The frontend automatically loads from:

- `localStorage.getItem('supabase_url')`
- `localStorage.getItem('supabase_key')`

Or update in index.html & login.html:

```html
<script>
  window.SUPABASE_URL = 'https://YOUR_PROJECT_ID.supabase.co';
  window.SUPABASE_ANON_KEY = 'eyJ... (Anon Key)';
</script>
```

---

## 📦 STEP 4: Install Dependencies

### Backend

```bash
cd backend
pip install -r requirements.txt
# This installs the new 'supabase' package
```

### Frontend

Already included via CDN:

```html
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
```

---

## 🚀 STEP 5: Test Authentication

### Start Backend

```bash
cd backend
python app.py
```

### Test Registration

1. Open <http://localhost:5000/login.html>
2. Click **Sign Up** tab
3. Enter:
   - Name: `Test User`
   - Email: `test@example.com`
   - Password: `Test123!`
4. Click **Sign Up**
5. ✅ Should see success message

### Verify in Supabase

1. Go to Supabase Dashboard → **Authentication → Users**
2. You should see your new user
3. Click on user to verify email, phone, etc.

### Test Login

1. Go to <http://localhost:5000/login.html>
2. Login with credentials from above
3. ✅ Should redirect to home page

---

## 🔐 STEP 6: Enable Email Verification

### In Supabase Dashboard

1. Go to **Authentication → Providers**
2. Find **Email**
3. Toggle **Confirm email** ON
4. Click **Save**

Now users will receive verification emails!

---

## 🛡️ STEP 7: Configure Password Reset (Optional)

### In Supabase Dashboard

1. Go to **Authentication → Email Templates**
2. Customize password reset template if desired
3. Users can request reset at `/login.html` → "Forgot Password?"

---

## 🔌 API Endpoints Reference

### Authentication Routes

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/auth/register` | POST | Register new user |
| `/api/auth/login` | POST | Login user |
| `/api/auth/logout` | POST | Logout user |
| `/api/auth/profile` | GET | Get current user profile |
| `/api/auth/profile` | PUT | Update user profile |
| `/api/auth/request-password-reset` | POST | Request password reset email |

### Example: Register

```javascript
// Frontend
const { success, user } = await Auth.signup('John', 'john@example.com', 'pass123');

// Backend will:
// 1. Create user in Supabase Auth
// 2. Create profile in public.users table
// 3. Transfer guest cart to user
// 4. Return success response
```

---

## 🐛 Troubleshooting

### Issue: "Supabase not installed"

```bash
pip install supabase
```

### Issue: "Cannot find Supabase URL"

- Check `backend/.env` has `SUPABASE_URL` set
- Restart Flask server after updating .env

### Issue: "Invalid ANON Key"

- Make sure frontend is using **ANON Key** (not Service Key)
- Service Key is for backend only

### Issue: "Email already registered"

- This email already exists in Supabase Auth
- Try with different email or reset in Supabase dashboard

### Issue: "Login fails but registration works"

- Verify credentials are correct
- Check Supabase Authentication → Users table for the user
- Try password reset if password was changed

### Issue: "User can't update profile"

- Check RLS policy is enabled for UPDATE
- Verify user_id in session matches auth.uid()

---

## 🔄 Migration from Old Auth (If Upgrading)

If you had users with the old bcrypt system:

```python
# migration_script.py
from supabase import create_client
from db import users_col  # Old MongoDB

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Migrate each user
for user in users_col.find():
    # Create in Supabase Auth
    result = supabase.auth.admin.create_user({
        'email': user['email'],
        'password': generate_random_password(),  # They'll reset
        'email_confirm': True
    })
    
    # Create profile
    supabase.table('users').insert({
        'id': result.user.id,
        'email': user['email'],
        'name': user.get('name'),
        'phone': user.get('phone'),
        'address': user.get('address'),
        'role': user.get('role', 'user'),
        'created_at': user.get('created_at')
    }).execute()
```

---

## 📚 Additional Resources

- **Supabase Docs:** <https://supabase.com/docs>
- **Supabase Auth JS:** <https://supabase.com/docs/reference/javascript/auth-signup>
- **PostgreSQL RLS:** <https://supabase.com/docs/guides/auth/row-level-security>
- **Flask Integration:** <https://supabase.com/docs/reference/python>

---

## ✅ Deployment Checklist

Before deploying to production:

- [ ] Create Supabase project (not local Dev)
- [ ] Set up production URL & keys in environment
- [ ] Enable email verification
- [ ] Configure custom email templates
- [ ] Set up password reset emails
- [ ] Enable CORS for your domain
- [ ] Test registration → verification → login flow
- [ ] Enable backups in Supabase
- [ ] Set up monitoring/alerts
- [ ] Document Supabase project credentials securely

---

## 💡 Best Practices

1. **Never commit credentials** → Use .env files (added to .gitignore)
2. **Service Key is secret** → Backend only, never expose to frontend
3. **Anon Key is public** → Can be in frontend code
4. **Enable RLS** → Always enable Row Level Security for user data
5. **Test email flow** → Verify emails work in production
6. **Rate limiting** → Supabase includes built-in rate limits
7. **Backups** → Regularly backup Supabase database

---

**Need Help?** Check Supabase Discord or create issue in repository.
