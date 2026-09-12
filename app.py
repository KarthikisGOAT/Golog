import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timezone
import pandas as pd

st.set_page_config(
    page_title="Karthik Logistics",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# Configuration
# -----------------------------
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_ANON_KEY"]
    return create_client(url, key)

try:
    supabase = get_supabase()
except Exception:
    st.error("Supabase is not configured. Add SUPABASE_URL and SUPABASE_ANON_KEY in Streamlit Secrets.")
    st.stop()

# -----------------------------
# Session state
# -----------------------------
defaults = {
    "user": None,
    "profile": None,
    "page": "Home",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# -----------------------------
# Styling
# -----------------------------
st.markdown("""
<style>
    .main { background: #f7f7f7; }
    .hero {
        padding: 2.5rem;
        border-radius: 24px;
        background: linear-gradient(135deg, #b30000 0%, #e31b23 55%, #111 100%);
        color: white;
        margin-bottom: 1.5rem;
    }
    .hero h1 { font-size: 2.7rem; margin-bottom: .4rem; }
    .hero p { font-size: 1.15rem; margin-bottom: 0; }
    .card {
        background: white;
        border: 1px solid #e5e5e5;
        border-radius: 18px;
        padding: 1.15rem;
        margin-bottom: .8rem;
        box-shadow: 0 4px 16px rgba(0,0,0,.05);
    }
    .status {
        display: inline-block;
        padding: .25rem .65rem;
        border-radius: 999px;
        font-weight: 700;
        font-size: .85rem;
        background: #eee;
    }
    .small { color: #666; font-size: .9rem; }
    div.stButton > button {
        border-radius: 12px;
        min-height: 2.7rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Helpers
# -----------------------------
def current_profile():
    return st.session_state.get("profile")

def load_profile(user_id):
    r = supabase.table("profiles").select(
        "id,username,full_name,phone,email,role,company_id,active"
    ).eq("id", user_id).single().execute()
    return r.data

def company_name(company_id):
    if not company_id:
        return "—"
    r = supabase.table("companies").select("name").eq("id", company_id).limit(1).execute()
    return r.data[0]["name"] if r.data else "—"

def logout():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    st.session_state.user = None
    st.session_state.profile = None
    st.session_state.page = "Home"
    st.rerun()

def safe_error(e):
    return str(e)

def job_status_label(s):
    return {
        "pending": "Pending",
        "in_progress": "In Progress",
        "completed": "Completed",
    }.get(s, str(s).replace("_", " ").title())

def set_status(job_id, old_status, new_status, changed_by):
    update = {"status": new_status}
    if new_status == "completed":
        update["completed_at"] = datetime.now(timezone.utc).isoformat()
    else:
        update["completed_at"] = None

    supabase.table("jobs").update(update).eq("id", job_id).execute()

    # History is optional. The SQL patch included with this project adds the
    # required INSERT policy.
    try:
        supabase.table("job_status_history").insert({
            "job_id": job_id,
            "old_status": old_status,
            "new_status": new_status,
            "changed_by": changed_by,
        }).execute()
    except Exception:
        pass

# -----------------------------
# Header / public navigation
# -----------------------------
if not current_profile():
    st.markdown("""
    <div class="hero">
        <h1>🚚 Karthik Logistics</h1>
        <p>Professional logistics, shipping and supply-chain services.</p>
    </div>
    """, unsafe_allow_html=True)

    nav = st.columns(4)
    with nav[0]:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.page = "Home"
    with nav[1]:
        if st.button("📞 Contact Us", use_container_width=True):
            st.session_state.page = "Contact"
    with nav[2]:
        if st.button("🌍 Branches", use_container_width=True):
            st.session_state.page = "Branches"
    with nav[3]:
        if st.button("🔐 Login", use_container_width=True):
            st.session_state.page = "Login"

else:
    p = current_profile()
    st.markdown(f"""
    <div class="hero">
        <h1>🚚 Karthik Logistics</h1>
        <p>Welcome, {p.get("full_name","User")} · {str(p.get("role","")).title()}</p>
    </div>
    """, unsafe_allow_html=True)

    nav = st.columns(4)
    with nav[0]:
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.page = "Dashboard"
    with nav[1]:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.page = "Home"
    with nav[2]:
        if st.button("📞 Contact", use_container_width=True):
            st.session_state.page = "Contact"
    with nav[3]:
        if st.button("🚪 Logout", use_container_width=True):
            logout()

# -----------------------------
# Home
# -----------------------------
if st.session_state.page == "Home":
    st.subheader("Welcome to Karthik Logistics Services FZE!")

    services = [
        "Express Delivery",
        "International Shipping",
        "Warehousing Solutions",
        "Inventory Management",
        "Dangerous Goods Handling & Documentation",
        "E-Commerce",
        "Cold Chain",
        "Industrial Packing",
        "Freight Forwarding",
    ]

    cols = st.columns(3)
    for i, service in enumerate(services):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="card">
                <h3>📦 {service}</h3>
                <div class="small">Karthik Logistics service</div>
            </div>
            """, unsafe_allow_html=True)

    st.link_button(
        "🌐 Visit Website",
        "https://karthiklogistics.com",
        use_container_width=False,
    )

# -----------------------------
# Contact
# -----------------------------
elif st.session_state.page == "Contact":
    st.subheader("📞 Contact Us")
    try:
        deps = supabase.table("contact_departments").select(
            "id,department_name"
        ).order("department_name").execute().data or []
        people = supabase.table("contact_people").select(
            "id,department_id,full_name,phone,email"
        ).execute().data or []

        people_by_dep = {}
        for person in people:
            people_by_dep.setdefault(person["department_id"], []).append(person)

        if not deps:
            st.info("No contact departments have been added yet.")
        else:
            for dep in deps:
                with st.expander(dep["department_name"], expanded=False):
                    rows = people_by_dep.get(dep["id"], [])
                    if not rows:
                        st.caption("No contact person added yet.")
                    for person in rows:
                        st.markdown(f"**{person.get('full_name','')}**")
                        if person.get("phone"):
                            st.markdown(f"📱 {person['phone']}")
                            st.markdown(f'<a href="tel:{person["phone"]}">Call</a>', unsafe_allow_html=True)
                        if person.get("email"):
                            st.markdown(f"✉️ {person['email']}")
                            st.markdown(f'<a href="mailto:{person["email"]}">Email</a>', unsafe_allow_html=True)
                        st.divider()
    except Exception as e:
        st.error(f"Could not load contacts: {safe_error(e)}")

# -----------------------------
# Branches
# -----------------------------
elif st.session_state.page == "Branches":
    st.subheader("🌍 Company Branches")
    try:
        branches = supabase.table("company_branches").select(
            "branch_name,city,country,phone,email,address,logo_url,company_id"
        ).order("city").execute().data or []

        companies = supabase.table("companies").select("id,name").execute().data or []
        cmap = {c["id"]: c["name"] for c in companies}

        if not branches:
            st.info("No branches have been added yet.")
        for b in branches:
            st.markdown(f"""
            <div class="card">
                <h3>{b.get("branch_name","Branch")}</h3>
                <p><b>Company:</b> {cmap.get(b.get("company_id"), "—")}</p>
                <p><b>Location:</b> {b.get("city","")}, {b.get("country","")}</p>
                <p><b>Phone:</b> {b.get("phone") or "—"}</p>
                <p><b>Email:</b> {b.get("email") or "—"}</p>
                <p><b>Address:</b> {b.get("address") or "—"}</p>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Could not load branches: {safe_error(e)}")

# -----------------------------
# Login
# -----------------------------
elif st.session_state.page == "Login":
    st.subheader("🔐 Karthik Login")

    companies = supabase.table("companies").select("id,name,code").order("name").execute().data or []
    company_map = {c["name"]: c for c in companies}

    login_type = st.selectbox("Select Type", ["Company", "Client"])
    selected_company_name = st.selectbox(
        "Select Company",
        list(company_map.keys()) if company_map else []
    )
    identifier = st.text_input(
        "Username / Employee ID",
        placeholder="Enter your username or Employee ID"
    )
    password = st.text_input("Password", type="password")

    st.caption("Use the email associated with the account if username lookup has not been enabled yet.")

    if st.button("Login", type="primary", use_container_width=True):
        if not selected_company_name or not identifier or not password:
            st.warning("Please complete all login fields.")
        else:
            email_for_auth = identifier.strip()

            # First try identifier as an email.
            if "@" not in email_for_auth:
                try:
                    rpc = supabase.rpc(
                        "get_auth_email_by_username",
                        {"p_username": email_for_auth}
                    ).execute()
                    if rpc.data:
                        email_for_auth = rpc.data
                except Exception:
                    pass

            try:
                auth = supabase.auth.sign_in_with_password({
                    "email": email_for_auth,
                    "password": password,
                })

                profile = load_profile(auth.user.id)

                selected_company_id = company_map[selected_company_name]["id"]

                if not profile or not profile.get("active"):
                    raise Exception("This account is inactive or has no profile.")

                if profile.get("company_id") != selected_company_id:
                    raise Exception("The selected company does not match this account.")

                expected_role = "client" if login_type == "Client" else None
                if expected_role and profile.get("role") != expected_role:
                    raise Exception("This account is not registered as a client.")

                if not expected_role and profile.get("role") not in ("manager", "employee"):
                    raise Exception("Company login requires a manager or employee account.")

                st.session_state.user = auth.user
                st.session_state.profile = profile
                st.session_state.page = "Dashboard"
                st.success("Login successful.")
                st.rerun()

            except Exception as e:
                st.error(f"Login failed: {safe_error(e)}")

# -----------------------------
# Dashboard router
# -----------------------------
elif st.session_state.page == "Dashboard":
    p = current_profile()
    if not p:
        st.session_state.page = "Login"
        st.rerun()

    role = p["role"]
    if role == "manager":
        st.session_state.page = "Manager"
        st.rerun()
    elif role == "employee":
        st.session_state.page = "Employee"
        st.rerun()
    elif role == "client":
        st.session_state.page = "Client"
        st.rerun()

# -----------------------------
# Manager dashboard
# -----------------------------
elif st.session_state.page == "Manager":
    p = current_profile()
    st.subheader("🧑‍💼 Manager Dashboard")

    company_id = p["company_id"]
    tabs = st.tabs(["Assign Job", "Do Job"])

    with tabs[0]:
        clients = supabase.table("clients").select(
            "id,client_name,contact_person"
        ).eq("company_id", company_id).eq("active", True).order("client_name").execute().data or []

        employees = supabase.table("employees").select(
            "id,employee_id,full_name,phone"
        ).eq("company_id", company_id).eq("active", True).order("full_name").execute().data or []

        if not clients:
            st.warning("No clients are available for this company.")
        if not employees:
            st.warning("No employees are available for this company.")

        with st.form("assign_job"):
            client_options = {c["client_name"]: c["id"] for c in clients}
            employee_options = {
                f'{e["employee_id"]} — {e["full_name"]}': e["id"]
                for e in employees
            }

            client_name = st.selectbox(
                "Select Client",
                list(client_options.keys()) if client_options else []
            )
            job_title = st.text_input("Job Title *")
            notes = st.text_area("Notes")
            employee_label = st.selectbox(
                "Assign To Employee",
                list(employee_options.keys()) if employee_options else []
            )

            submitted = st.form_submit_button(
                "Assign Job",
                type="primary",
                use_container_width=True
            )

        if submitted:
            if not job_title.strip() or not client_name or not employee_label:
                st.error("Job Title, Client and Employee are required.")
            else:
                try:
                    supabase.table("jobs").insert({
                        "job_title": job_title.strip(),
                        "notes": notes.strip() or None,
                        "company_id": company_id,
                        "client_id": client_options[client_name],
                        "assigned_employee_id": employee_options[employee_label],
                        "created_by": p["id"],
                        "status": "pending",
                    }).execute()
                    st.success("Job assigned successfully.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not create job: {safe_error(e)}")

    with tabs[1]:
        jobs = supabase.table("jobs").select(
            "id,job_title,notes,status,created_at,completed_at,client_id,assigned_employee_id"
        ).eq("company_id", company_id).order("created_at", desc=True).execute().data or []

        clients = supabase.table("clients").select("id,client_name").eq(
            "company_id", company_id
        ).execute().data or []
        employees = supabase.table("employees").select(
            "id,employee_id,full_name,phone"
        ).eq("company_id", company_id).execute().data or []

        cmap = {x["id"]: x["client_name"] for x in clients}
        emap = {x["id"]: x for x in employees}

        if not jobs:
            st.info("No jobs yet.")

        for job in jobs:
            emp = emap.get(job.get("assigned_employee_id"), {})
            with st.expander(
                f'{job["job_title"]} · {job_status_label(job["status"])}'
            ):
                st.write(f'**Client:** {cmap.get(job.get("client_id"), "—")}')
                st.write(f'**Employee:** {emp.get("employee_id","—")} — {emp.get("full_name","—")}')
                st.write(f'**Phone:** {emp.get("phone") or "—"}')
                st.write(f'**Notes:** {job.get("notes") or "—"}')

                if job["status"] != "completed":
                    new_status = st.selectbox(
                        "Status",
                        ["pending", "in_progress", "completed"],
                        index=["pending","in_progress","completed"].index(job["status"]),
                        key=f"manager_status_{job['id']}"
                    )
                    if st.button("Update Status", key=f"manager_update_{job['id']}"):
                        try:
                            set_status(job["id"], job["status"], new_status, p["id"])
                            st.success("Status updated.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Could not update job: {safe_error(e)}")

# -----------------------------
# Employee dashboard
# -----------------------------
elif st.session_state.page == "Employee":
    p = current_profile()
    st.subheader("👷 Employee Dashboard")

    employee = supabase.table("employees").select(
        "id,employee_id,full_name,phone,company_id"
    ).eq("profile_id", p["id"]).single().execute().data

    jobs = supabase.table("jobs").select(
        "id,job_title,notes,status,client_id,created_at"
    ).eq("assigned_employee_id", employee["id"]).order("created_at", desc=True).execute().data or []

    clients = supabase.table("clients").select(
        "id,client_name,contact_person,phone"
    ).eq("company_id", employee["company_id"]).execute().data or []
    cmap = {c["id"]: c for c in clients}

    if not jobs:
        st.info("No jobs are currently assigned to you.")

    for job in jobs:
        client = cmap.get(job["client_id"], {})
        with st.expander(f'{job["job_title"]} · {job_status_label(job["status"])}'):
            st.write(f'**Client:** {client.get("client_name","—")}')
            st.write(f'**Contact:** {client.get("contact_person") or "—"}')
            st.write(f'**Phone:** {client.get("phone") or "—"}')
            st.write(f'**Notes:** {job.get("notes") or "—"}')

            if job["status"] != "completed":
                choices = ["pending", "in_progress", "completed"]
                current_idx = choices.index(job["status"])
                new_status = st.selectbox(
                    "Update Status",
                    choices,
                    index=current_idx,
                    key=f"employee_status_{job['id']}"
                )
                if st.button("Save Status", key=f"employee_save_{job['id']}"):
                    try:
                        set_status(job["id"], job["status"], new_status, p["id"])
                        st.success("Status updated.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not update status: {safe_error(e)}")

# -----------------------------
# Client dashboard
# -----------------------------
elif st.session_state.page == "Client":
    p = current_profile()
    st.subheader("👤 Client Dashboard")

    client = supabase.table("clients").select(
        "id,client_name,company_id"
    ).eq("profile_id", p["id"]).single().execute().data

    jobs = supabase.table("jobs").select(
        "id,job_title,notes,status,assigned_employee_id,created_at,completed_at"
    ).eq("client_id", client["id"]).order("created_at", desc=True).execute().data or []

    employees = supabase.table("employees").select(
        "id,employee_id,full_name,phone"
    ).eq("company_id", client["company_id"]).execute().data or []
    emap = {e["id"]: e for e in employees}

    if not jobs:
        st.info("No jobs have been created for your account yet.")

    for job in jobs:
        emp = emap.get(job.get("assigned_employee_id"), {})
        with st.expander(f'{job["job_title"]} · {job_status_label(job["status"])}'):
            st.write(f'**Job Title:** {job["job_title"]}')
            st.write(f'**Job Status:** {job_status_label(job["status"])}')
            st.write(f'**Assigned Employee:** {emp.get("employee_id","—")}')
            st.write(f'**Employee Name:** {emp.get("full_name","—")}')
            st.write(f'**Employee Phone:** {emp.get("phone") or "—"}')
            st.write(f'**Job Notes:** {job.get("notes") or "—"}')

            if emp.get("phone"):
                st.markdown(
                    f'<a href="tel:{emp["phone"]}">📞 Call Employee</a>',
                    unsafe_allow_html=True
                )

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("Karthik Logistics Services FZE · Internal application")
