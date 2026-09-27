#streamlit_app.py
import requests
import streamlit as st
"""
streamlit_app.py
------------------
Simple Streamlit frontend for the LegalEase FastAPI backend.
Lets the user pick a document type (matching the three project
scenarios), fill in the details, preview the AI-generated text,
and download it as PDF, DOCX, or TXT.
 
Run the backend first:
    uvicorn main:app --reload
Then run this app:
    streamlit run streamlit_app.py
"""
 
import requests
import streamlit as st
 
API_BASE = "st.secrets.get("API_BASE","https://legal-ease-bay.vercel.app")

 
st.set_page_config(page_title="LegalEase", page_icon="⚖️", layout="centered")
st.title("⚖️ LegalEase — AI-Powered Legal Document Generator")
st.caption("Generate employment contracts, NDAs, and lease agreements in seconds.")
 
doc_type = st.selectbox(
    "What would you like to create?",
    ["Employment Contract", "Non-Disclosure Agreement (NDA)", "Residential Lease Agreement"],
)
 
st.divider()
 
# ---------------------------------------------------------------------------
# Scenario 1: Employment Contract
# ---------------------------------------------------------------------------
if doc_type == "Employment Contract":
    with st.form("employment_form"):
        company_name = st.text_input("Company Name")
        employee_name = st.text_input("Employee Name")
        job_title = st.text_input("Job Title / Role")
        start_date = st.date_input("Start Date")
        compensation = st.text_input("Compensation (e.g. $85,000/year)")
        work_location = st.text_input("Work Location", "Remote")
        employment_type = st.selectbox("Employment Type", ["Full-time", "Part-time", "Contract"])
        logo = st.file_uploader("Company Logo (optional, for branding)", type=["png", "jpg", "jpeg"])
        submitted = st.form_submit_button("Generate Contract")
 
    if submitted:
        with st.spinner("Drafting your employment contract..."):
            if logo:
                files = {"logo": (logo.name, logo.getvalue())}
                data = {
                    "company_name": company_name, "employee_name": employee_name,
                    "job_title": job_title, "start_date": str(start_date),
                    "compensation": compensation, "work_location": work_location,
                    "employment_type": employment_type,
                }
                resp = requests.post(f"{API_BASE}/generate/employment-contract/branded",
                                      data=data, files=files)
            else:
                payload = {
                    "company_name": company_name, "employee_name": employee_name,
                    "job_title": job_title, "start_date": str(start_date),
                    "compensation": compensation, "work_location": work_location,
                    "employment_type": employment_type,
                }
                resp = requests.post(f"{API_BASE}/generate/employment-contract", json=payload)
        st.session_state["result"] = resp.json() if resp.ok else {"error": resp.text}
 
# ---------------------------------------------------------------------------
# Scenario 2: NDA
# ---------------------------------------------------------------------------
elif doc_type == "Non-Disclosure Agreement (NDA)":
    with st.form("nda_form"):
        disclosing_party = st.text_input("Disclosing Party")
        receiving_party = st.text_input("Receiving Party (Freelancer/Client)")
        purpose = st.text_area("Purpose of Disclosure")
        scope = st.text_area("Scope of Confidential Information")
        effective_date = st.date_input("Effective Date")
        term = st.text_input("Term / Duration", "2 years from the Effective Date")
        submitted = st.form_submit_button("Generate NDA")
 
    if submitted:
        payload = {
            "disclosing_party": disclosing_party, "receiving_party": receiving_party,
            "purpose": purpose, "scope": scope,
            "effective_date": str(effective_date), "term": term,
        }
        with st.spinner("Drafting your NDA..."):
            resp = requests.post(f"{API_BASE}/generate/nda", json=payload)
        st.session_state["result"] = resp.json() if resp.ok else {"error": resp.text}
 
# ---------------------------------------------------------------------------
# Scenario 3: Lease Agreement
# ---------------------------------------------------------------------------
else:
    with st.form("lease_form"):
        landlord_name = st.text_input("Landlord Name")
        tenant_name = st.text_input("Tenant Name")
        property_address = st.text_input("Property Address")
        lease_start = st.date_input("Lease Start Date")
        lease_end = st.date_input("Lease End Date")
        monthly_rent = st.text_input("Monthly Rent (e.g. $1,500)")
        security_deposit = st.text_input("Security Deposit", "One month's rent")
        submitted = st.form_submit_button("Generate Lease Agreement")
 
    if submitted:
        payload = {
            "landlord_name": landlord_name, "tenant_name": tenant_name,
            "property_address": property_address, "lease_start": str(lease_start),
            "lease_end": str(lease_end), "monthly_rent": monthly_rent,
            "security_deposit": security_deposit,
        }
        with st.spinner("Drafting your lease agreement..."):
            resp = requests.post(f"{API_BASE}/generate/lease-agreement", json=payload)
        st.session_state["result"] = resp.json() if resp.ok else {"error": resp.text}
 
# ---------------------------------------------------------------------------
# Result display
# ---------------------------------------------------------------------------
result = st.session_state.get("result")
if result:
    if "error" in result:
        st.error(result["error"])
    else:
        st.divider()
        st.subheader("📄 Preview")
        st.text_area("Generated document text", result["preview_text"], height=350)
 
        st.subheader("⬇️ Download")
        cols = st.columns(len(result["download_links"]))
        for col, (fmt, link) in zip(cols, result["download_links"].items()):
            file_bytes = requests.get(f"{API_BASE}{link}").content
            col.download_button(
                label=f"Download .{fmt}",
                data=file_bytes,
                file_name=link.split("/")[-1],
            )
