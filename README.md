# Karthik Logistics — Streamlit + Supabase

## 1. Supabase

Your existing database schema is used by this app.

Run `supabase_streamlit_patch.sql` in Supabase SQL Editor.

The patch adds:
- username -> auth email lookup for login
- job status history INSERT policy

## 2. Local setup

Python 3.11+ is recommended.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create `.streamlit/secrets.toml`:

```toml
SUPABASE_URL = "https://YOUR-PROJECT.supabase.co"
SUPABASE_ANON_KEY = "YOUR-SUPABASE-ANON-KEY"
```

Then run:

```bash
streamlit run app.py
```

## 3. Supabase users

Create users in Supabase Authentication.

For every Auth user, create the matching `profiles` row.

Employee:
- profiles.role = employee
- profiles.company_id = the employee's company
- employees.profile_id = Auth user's id
- employees.employee_id = unique ID such as EMP001

Manager:
- profiles.role = manager
- profiles.company_id = their company

Client:
- profiles.role = client
- profiles.company_id = their company
- clients.profile_id = Auth user's id

Passwords stay in Supabase Auth. Do not put passwords in PostgreSQL tables.

## 4. Streamlit Community Cloud

1. Put this project in a GitHub repository.
2. Open Streamlit Community Cloud.
3. Create a new app.
4. Select your repository.
5. Main file: `app.py`.
6. Deploy.
7. Open the app's Settings / Secrets.
8. Add:

```toml
SUPABASE_URL = "https://YOUR-PROJECT.supabase.co"
SUPABASE_ANON_KEY = "YOUR-SUPABASE-ANON-KEY"
```

9. Save and reboot the app.

Never commit `.streamlit/secrets.toml` containing your real keys.

## Features

- Public Home
- Services list
- Contact Us
- Company branches
- Company/client login
- Manager dashboard
- Employee dashboard
- Client dashboard
- Job assignment
- Job status tracking
- Supabase Auth
- PostgreSQL Row Level Security
