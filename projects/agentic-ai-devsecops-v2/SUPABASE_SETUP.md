# Supabase setup for Agentic AI DevSecOps v2

This guide describes how to connect the v2 project to Supabase for persistent storage of scans and findings.

## 1. Create a Supabase project

1. Go to https://supabase.com and create a new project.
2. Wait for the project to finish provisioning.
3. Open the project dashboard.

## 2. Get your credentials

In Supabase Settings -> API, copy:
- Project URL
- anon public key
- service role key

## 3. Create the database table

Open the SQL editor in Supabase and run this SQL:

```sql
create table if not exists scans (
  id uuid primary key default gen_random_uuid(),
  scan_id text unique not null,
  payload jsonb not null,
  review_required boolean default false,
  created_at timestamptz default now()
);

create index if not exists scans_review_required_idx on scans(review_required);
create index if not exists scans_created_at_idx on scans(created_at desc);
```

## 4. Configure environment variables

Create a `.env` file in the v2 project with:

```env
STORAGE_BACKEND=supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

## 5. Install Python dependency

Install the Supabase client library:

```bash
pip install supabase
```

## 6. Next step

Once the database table exists, the v2 backend can persist scans and review items in Supabase instead of using in-memory storage.
