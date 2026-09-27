#demo_generate.py
"""
demo_generate.py
------------------
Offline demo runner. Uses realistic *sample* AI-drafted text (the same
shape Gemini returns for the prompts in templates/prompts.py) and feeds
it through the REAL doc_generator.py pipeline, so the .docx/.txt files
this produces are byte-for-byte what the running app would create for
that AI output. Lets the whole pipeline be demonstrated without a live
API key.
"""
 
import os
from doc_generator import build_docx, build_txt
 
SAMPLE_TEXTS = {
    "employment_contract":,
 
    "nda":,
 
    "lease_agreement":,
}
 
SAMPLE_DATA = {
    "employment_contract": {
        "company_name": "Nimbus Robotics Inc.", "employee_name": "Priya Sharma",
        "job_title": "Backend Engineer", "start_date": "2026-10-06",
        "compensation": "$95,000/year", "work_location": "Austin, TX (Hybrid)",
        "employment_type": "Full-time",
    },
    "nda": {
        "disclosing_party": "Aiden Cole", "receiving_party": "Blueharbor Media LLC",
        "purpose": "Website redesign project", "scope": "Design specs, pricing, client materials",
        "effective_date": "2026-09-27", "term": "2 years from the Effective Date",
    },
    "lease_agreement": {
        "landlord_name": "Marcus Webb", "tenant_name": "Elena Torres",
        "property_address": "48 Willow Creek Lane, Denver, CO 80203",
        "lease_start": "2026-10-01", "lease_end": "2027-09-30",
        "monthly_rent": "$1,750", "security_deposit": "$1,750 (one month's rent)",
    },
}
 
if __name__ == "__main__":
    os.makedirs("generated_docs", exist_ok=True)
    for doc_type, text in SAMPLE_TEXTS.items():
        data = SAMPLE_DATA[doc_type]
        docx_path = build_docx(doc_type, data, text, f"sample_{doc_type}")
        txt_path = build_txt(doc_type, text, f"sample_{doc_type}")
        print(f"[OK] {doc_type}: {docx_path}, {txt_path}")
 
