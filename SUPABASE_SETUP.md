# SUPABASE AUTHENTICATION SETUP GUIDE

## Step 1: Create Supabase Project

1. Go to <https://supabase.com>
2. Sign up / Log in
3. Create a new project:
   - Project name: `flavour-fleet`
   - Database password: (strong password)
   - Region: (closest to you)
4. Wait for project to be ready (~1-2 minutes)

## Step 2: Get Credentials

Once project is ready, get these from Settings → API:

- **Supabase URL**: `https://[project-id].supabase.co`
- **Public ANON Key**: `eyJ... (long string)`
- **Service Role Key**: `eyJ... (for backend only)`

## Step 3: Create Users Table

In Supabase SQL Editor, run:

```sql
-- Create custom users table
CREATE TABLE public.users (
  id UUID PRIMARY KEY DEFAULT auth.uid(),
  email TEXT UNIQUE,
  name TEXT,
  phone TEXT DEFAULT '',
  address TEXT DEFAULT '',
  avatar_url TEXT,
  role TEXT DEFAULT 'user',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can read their own data
CREATE POLICY "Users can read own data" ON public.users
  FOR SELECT USING (auth.uid() = id);

-- RLS Policy: Users can update their own data
CREATE POLICY "Users can update own data" ON public.users
  FOR UPDATE USING (auth.uid() = id);

-- Public read for user profiles
CREATE POLICY "Public read user profiles" ON public.users
  FOR SELECT USING (true);
```

## Step 4: Configure Environment Variables

### Backend (.env)

```
SUPABASE_URL=https://[your-project-id].supabase.co
SUPABASE_SERVICE_KEY=eyJ... (Service Role Key - KEEP SECRET)
```

### Frontend (create .env.local in root)

```
VITE_SUPABASE_URL=https://[your-project-id].supabase.co
VITE_SUPABASE_ANON_KEY=eyJ... (Anon Key)
```

Or in frontend index.html, add before script tags:

```html
<script>
  window.SUPABASE_URL = 'https://[your-project-id].supabase.co';
  window.SUPABASE_ANON_KEY = 'eyJ...';
</script>
```

## Step 5: Install Dependencies

### Backend

```bash
pip install supabase python-dotenv
```

### Frontend

```html
<!-- Add to index.html <head> -->
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
```

## Step 6: Deploy Changes

After setting up:

1. Update backend environment variables
2. Restart Flask server
3. Test registration/login on <http://localhost:5000/login.html>

## Troubleshooting

- **"Cannot find Supabase URL"**: Check .env file exists and SUPABASE_URL is set
- **"Invalid credentials"**: Verify you're using correct Anon Key (not Service Key) in frontend
- **"User already exists"**: Email is already registered in Supabase Auth
- **401 Unauthorized**: Session token expired, user needs to log in again
