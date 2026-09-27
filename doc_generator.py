#doc_generator.py
"""
doc_generator.py
------------------
Takes the raw clause text returned by the AI core and turns it into
polished output files:
  - .docx  (editable, branded, via python-docx)
  - .pdf   (print-ready, via fpdf2)
  - .txt   (plain text, quick copy/paste)
 
Also builds a simple "key terms" table (party names, dates, amounts)
that gets placed at the top of the DOCX/PDF output, per the project
requirement for "automatic term tables".
"""
 
import os
import re
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
 
try:
    from fpdf import FPDF
    _FPDF_AVAILABLE = True
except ImportError:  # pragma: no cover - allows DOCX/TXT-only environments
    _FPDF_AVAILABLE = False
 
OUTPUT_DIR = "generated_docs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
 
 
def _split_sections(raw_text: str):
    """Split AI output into (heading, body) tuples using numbered headings."""
    pattern = re.compile(r"\n(?=\d+\.\s)")
    chunks = pattern.split(raw_text.strip())
    sections = []
    for chunk in chunks:
        lines = chunk.strip().split("\n", 1)
        heading = lines[0].strip()
        body = lines[1].strip() if len(lines) > 1 else ""
        sections.append((heading, body))
    return sections
 
 
def _key_terms(doc_type: str, data: dict) -> dict:
    """Builds a small dict of key terms to render as a summary table."""
    if doc_type == "employment_contract":
        return {
            "Company": data.get("company_name", ""),
            "Employee": data.get("employee_name", ""),
            "Role": data.get("job_title", ""),
            "Start Date": data.get("start_date", ""),
            "Compensation": data.get("compensation", ""),
        }
    if doc_type == "nda":
        return {
            "Disclosing Party": data.get("disclosing_party", ""),
            "Receiving Party": data.get("receiving_party", ""),
            "Effective Date": data.get("effective_date", ""),
            "Term": data.get("term", ""),
        }
    if doc_type == "lease_agreement":
        return {
            "Landlord": data.get("landlord_name", ""),
            "Tenant": data.get("tenant_name", ""),
            "Property": data.get("property_address", ""),
            "Lease Term": f"{data.get('lease_start','')} - {data.get('lease_end','')}",
            "Monthly Rent": data.get("monthly_rent", ""),
        }
    return {}
 
 
TITLES = {
    "employment_contract": "EMPLOYMENT CONTRACT",
    "nda": "NON-DISCLOSURE AGREEMENT",
    "lease_agreement": "RESIDENTIAL LEASE AGREEMENT",
}
 
 
# --------------------------------------------------------------------------
# DOCX
# --------------------------------------------------------------------------
def build_docx(doc_type: str, data: dict, raw_text: str, filename: str,
                logo_path: str | None = None) -> str:
    document = Document()
 
    # Branding: optional logo + company/user name in the header
    if logo_path and os.path.exists(logo_path):
        header = document.sections[0].header
        p = header.paragraphs[0]
        run = p.add_run()
        run.add_picture(logo_path, width=Inches(1.2))
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
 
    title = document.add_heading(TITLES.get(doc_type, "LEGAL DOCUMENT"), level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
 
    # Key terms table
    terms = _key_terms(doc_type, data)
    if terms:
        document.add_heading("Key Terms", level=2)
        table = document.add_table(rows=0, cols=2)
        table.style = "Light Grid Accent 1"
        for key, value in terms.items():
            row = table.add_row().cells
            row[0].text = key
            row[1].text = str(value)
        document.add_paragraph()
 
    # Clause sections
    document.add_heading("Agreement Text", level=2)
    for heading, body in _split_sections(raw_text):
        h = document.add_heading(heading, level=3)
        for para in body.split("\n"):
            if para.strip():
                document.add_paragraph(para.strip())
 
    out_path = os.path.join(OUTPUT_DIR, f"{filename}.docx")
    document.save(out_path)
    return out_path
 
 
# --------------------------------------------------------------------------
# PDF
# --------------------------------------------------------------------------
if _FPDF_AVAILABLE:
    class LegalPDF(FPDF):
        def header(self):
            self.set_font("Helvetica", "B", 14)
            self.cell(0, 10, self.title_text, align="C", new_x="LMARGIN", new_y="NEXT")
            self.ln(2)
 
        def footer(self):
            self.set_y(-15)
            self.set_font("Helvetica", "I", 8)
            self.cell(0, 10, f"Page {self.page_no()}", align="C")
 
 
def build_pdf(doc_type: str, data: dict, raw_text: str, filename: str) -> str:
    if not _FPDF_AVAILABLE:
        raise RuntimeError("fpdf2 is not installed. Run: pip install fpdf2")
    pdf = LegalPDF()
    pdf.title_text = TITLES.get(doc_type, "LEGAL DOCUMENT")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
 
    terms = _key_terms(doc_type, data)
    if terms:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Key Terms", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        for key, value in terms.items():
            pdf.cell(0, 6, f"{key}: {value}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)
 
    for heading, body in _split_sections(raw_text):
        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 7, heading)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 6, body)
        pdf.ln(2)
 
    out_path = os.path.join(OUTPUT_DIR, f"{filename}.pdf")
    pdf.output(out_path)
    return out_path
 
 
# --------------------------------------------------------------------------
# TXT
# --------------------------------------------------------------------------
def build_txt(doc_type: str, raw_text: str, filename: str) -> str:
    out_path = os.path.join(OUTPUT_DIR, f"{filename}.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"{TITLES.get(doc_type, 'LEGAL DOCUMENT')}\n")
        f.write("=" * 60 + "\n\n")
        f.write(raw_text)
    return out_path
 
 
def generate_all_formats(doc_type: str, data: dict, raw_text: str,
                          filename: str, logo_path: str | None = None) -> dict:
    """Convenience helper used by the API layer to build every format at once."""
    outputs = {
        "docx": build_docx(doc_type, data, raw_text, filename, logo_path),
        "txt": build_txt(doc_type, raw_text, filename),
    }
    if _FPDF_AVAILABLE:
        outputs["pdf"] = build_pdf(doc_type, data, raw_text, filename)
    return outputs
