# Supabase Setup Guide for PerformancePulse

This guide walks you through setting up Supabase for Phase 1.1.2 of PerformancePulse.

## Prerequisites

1. ✅ Backend development environment (completed in Phase 1.1.1)
2. ✅ Virtual environment activated (`source pulse_venv/bin/activate`)
3. ✅ All Python dependencies installed

## Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Sign in or create an account
3. Click "New Project"
4. Choose your organization
5. Enter project details:
   - **Name**: `performancepulse-dev`
   - **Database Password**: Generate a strong password (save this!)
   - **Region**: Choose closest to your location
6. Click "Create new project"
7. Wait for project creation (2-3 minutes)

## Step 2: Configure Environment Variables

1. In your Supabase project dashboard, go to **Settings > API**
2. Copy the following values:
   - **Project URL** (looks like: `https://xxxxx.supabase.co`)
   - **Service Role Key** (anon key won't work for backend operations)

3. Create a `.env` file in the backend directory:

```bash
# In /backend/.env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# These will be configured in later phases
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_CLIENT_ID=your_google_oauth_client_id
GOOGLE_CLIENT_SECRET=your_google_oauth_secret
```

## Step 3: Apply Database Schema

1. In your Supabase project, go to **SQL Editor**
2. Copy the contents of `backend/src/database/schema.sql`
3. Paste into the SQL Editor
4. Click "Run" to execute the schema

**The schema includes:**
- ✅ Core tables: `profiles`, `evidence_items`, `data_consents`
- ✅ Row Level Security (RLS) policies
- ✅ Proper indexes for performance
- ✅ Automatic timestamp triggers

## Step 4: Verify Setup

Run the database setup verification script:

```bash
cd backend
source pulse_venv/bin/activate
python3 setup_database.py
```

**Expected output:**
```
🚀 Starting PerformancePulse Database Setup
✅ Environment variables loaded
✅ Database schema loaded
📝 Schema ready for manual application to Supabase project
✅ Database connection successful!
✅ Database service is healthy!
🎉 Database setup verification complete!
✅ Phase 1.1.2 database configuration is ready
```

## Step 5: Test API Endpoints

Start the backend server:

```bash
cd backend
source pulse_venv/bin/activate
python3 -m uvicorn src.main:app --reload
```

Visit: http://localhost:8000/api/docs

**Available endpoints:**
- ✅ `GET /api/health` - Backend health check
- ✅ `GET /api/auth/health` - Auth service health check
- ✅ `GET /api/auth/profile` - Get current user profile (requires auth)
- ✅ `GET /api/team/members` - Get team members (requires auth)
- ✅ `POST /api/team/members` - Create team member (requires auth)

## Google OAuth Setup (Phase 1.1.3)

For Phase 1.1.3, you'll need to configure Google OAuth:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - `http://localhost:3000/auth/callback` (development)
   - Your production domain (later)

## Troubleshooting

### Connection Errors
```bash
# Check environment variables
echo $SUPABASE_URL
echo $SUPABASE_SERVICE_ROLE_KEY

# Verify Supabase project is active
curl -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" "$SUPABASE_URL/rest/v1/profiles"
```

### Schema Errors
- Ensure you used the **Service Role Key**, not the **Anon Key**
- Check that RLS policies are created correctly
- Verify all tables exist in the public schema

### Import Errors
```bash
# Reinstall dependencies if needed
source pulse_venv/bin/activate
pip install -r requirements.txt
```

## Security Notes

🔒 **Important Security Considerations:**
- Never commit `.env` files to version control
- Use Service Role Key only in backend (never in frontend)
- RLS policies protect data even with Service Role Key
- Always validate user permissions in application logic

## Next Steps

Once Supabase is configured:
1. ✅ Phase 1.1.2 complete
2. 🚧 Phase 1.1.3: Authentication & Team Management UI
3. 🚧 Phase 1.2.1: GitLab MCP Integration

---

**Need Help?**
- Check the logs: `tail -f ~/.supabase/logs/supabase.log`
- Supabase docs: https://supabase.com/docs
- Project issues: Create an issue in the repository 