import streamlit as st
from supabase import create_client, Client

# Page Config
st.set_page_config(page_title="Karthik Logistics", page_icon="🚚", layout="wide")

# Custom Red & White Branding
st.markdown("""
    <style>
    .stButton>button {
        background-color: #D32F2F;
        color: white;
        border-radius: 8px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #B71C1C;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Supabase
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["supabase"]["SUPABASE_URL"]
    key = st.secrets["supabase"]["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# Session State for Auth
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None

# Navigation Router
def logout():
    st.session_state.authenticated = False
    st.session_state.user = None
    st.rerun()

# ---------------- LOGIN SCREEN ----------------
if not st.session_state.authenticated:
    st.title("🔐 Karthik Logistics - Login")
    
    user_type = st.selectbox("Select Type", ["Company", "Client"])
    
    selected_company_id = None
    selected_client_id = None

    if user_type == "Company":
        companies = supabase.table("companies").select("*").execute().data
        company_names = {c["name"]: c["id"] for c in companies}
        choice = st.selectbox("Select Company", list(company_names.keys()))
        selected_company_id = company_names[choice]
    else:
        clients = supabase.table("clients").select("*").execute().data
        client_names = {c["name"]: c["id"] for c in clients}
        choice = st.selectbox("Select Client", list(client_names.keys()))
        selected_client_id = client_names[choice]

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        # Fetch user
        query = supabase.table("users").select("*").eq("username", username).eq("password_hash", password)
        res = query.execute()

        if res.data:
            user = res.data[0]
            st.session_state.authenticated = True
            st.session_state.user = user
            st.success(f"Welcome back, {user['full_name']}!")
            st.rerun()
        else:
            st.error("Invalid credentials or company mismatch.")

# ---------------- DASHBOARDS ----------------
else:
    user = st.session_state.user
    role = user["role"]

    # Top Navigation Bar
    col1, col2 = st.columns([8, 2])
    with col1:
        st.subheader(f"Welcome, {user['full_name']} ({role})")
    with col2:
        if st.button("Logout"):
            logout()

    st.divider()

    # --- MANAGER DASHBOARD ---
    if role == "Manager":
        tab1, tab2 = st.tabs(["📌 Assign Job", "📋 Do / Manage Jobs"])

        with tab1:
            st.subheader("Assign a New Job")
            clients = supabase.table("clients").select("*").eq("company_id", user["company_id"]).execute().data
            client_dict = {c["name"]: c["id"] for c in clients}

            employees = supabase.table("users").select("*").eq("role", "Employee").eq("company_id", user["company_id"]).execute().data
            emp_dict = {f"{e['full_name']} ({e['employee_id']})": e["id"] for e in employees}

            if client_dict and emp_dict:
                selected_client_name = st.selectbox("Select Client", list(client_dict.keys()))
                job_title = st.text_input("Job Title *")
                job_notes = st.text_area("Notes (Optional)")
                assigned_emp_name = st.selectbox("Assign To Employee", list(emp_dict.keys()))

                if st.button("Assign Job"):
                    if job_title:
                        supabase.table("jobs").insert({
                            "title": job_title,
                            "notes": job_notes,
                            "client_id": client_dict[selected_client_name],
                            "company_id": user["company_id"],
                            "assigned_to": emp_dict[assigned_emp_name],
                            "status": "Pending"
                        }).execute()
                        st.success("Job assigned successfully!")
                    else:
                        st.warning("Job Title is required.")

        with tab2:
            st.subheader("All Company Jobs")
            jobs = supabase.table("jobs").select("*, clients(name), users!jobs_assigned_to_fkey(full_name)").eq("company_id", user["company_id"]).execute().data
            
            for job in jobs:
                col_a, col_b, col_c = st.columns([4, 2, 2])
                with col_a:
                    st.write(f"**{job['title']}** - Client: {job['clients']['name']}")
                    st.caption(f"Assigned to: {job['users']['full_name'] if job['users'] else 'Unassigned'}")
                with col_b:
                    st.write(f"Status: **{job['status']}**")
                with col_c:
                    if job["status"] != "Completed":
                        if st.button("Mark Completed", key=job["id"]):
                            supabase.table("jobs").update({"status": "Completed"}).eq("id", job["id"]).execute()
                            st.rerun()

    # --- EMPLOYEE DASHBOARD ---
    elif role == "Employee":
        st.subheader("My Assigned Jobs")
        jobs = supabase.table("jobs").select("*, clients(name)").eq("assigned_to", user["id"]).execute().data

        for job in jobs:
            st.write(f"### {job['title']}")
            st.write(f"**Client:** {job['clients']['name']}")
            st.write(f"**Notes:** {job['notes']}")
            st.write(f"**Current Status:** {job['status']}")

            new_status = st.selectbox("Update Status", ["Pending", "In Progress", "Completed"], 
                                      index=["Pending", "In Progress", "Completed"].index(job["status"]), 
                                      key=f"status_{job['id']}")
            
            if st.button("Save Status", key=f"btn_{job['id']}"):
                supabase.table("jobs").update({"status": new_status}).eq("id", job["id"]).execute()
                st.success("Status updated!")
                st.rerun()
            st.divider()

    # --- CLIENT DASHBOARD ---
    elif role == "Client":
        st.subheader("Track Your Jobs")
        jobs = supabase.table("jobs").select("*, users!jobs_assigned_to_fkey(full_name, phone)").eq("client_id", user["client_id"]).execute().data

        for job in jobs:
            st.write(f"### {job['title']}")
            st.write(f"**Status:** {job['status']}")
            st.write(f"**Notes:** {job['notes']}")
            if job["users"]:
                st.write(f"**Assigned Driver/Employee:** {job['users']['full_name']}")
                st.write(f"**Contact:** {job['users']['phone']}")
            st.divider()
