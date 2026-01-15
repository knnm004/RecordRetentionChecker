import os
import re
import pytesseract
import numpy as np
from datetime import datetime
from pdf2image import convert_from_path
from duckduckgo_search import DDGS
from google import adk 

POPPLER_PATH = os.getenv('POPPLER_PATH')
TESSERACT_EXE = os.getenv('TESSERACT_EXE')

if TESSERACT_EXE:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE

# EXTRACTION TOOL
def extract_thai_text_from_pdf(file_path: str):
    """Thai OCR using Tesseract (Stable & Fast)."""
    
    if not POPPLER_PATH or not TESSERACT_EXE:
        return "TOOL_ERROR: System paths not found in .env file."
    file_path = os.path.normpath(file_path.strip().replace('"', '').replace("'", ""))
    if not os.path.exists(file_path):
        return f"TOOL_ERROR: File not found at {file_path}"

    try:
        pages = convert_from_path(file_path, dpi=150, poppler_path=POPPLER_PATH)
        full_text = ""
        for i, page in enumerate(pages):
            text = pytesseract.image_to_string(page, lang='tha+eng')
            full_text += f"\n--- Page {i+1} ---\n{text}"
        
        return full_text if full_text.strip() else "TOOL_ERROR: No text found in PDF."
    
    except Exception as e:
        return f"TOOL_ERROR: {str(e)}"

# DATE PARSING TOOL 
def parse_thai_date(text: str):
    """Converts Thai BE date strings to AD YYYY-MM-DD."""
    if not text or "not found" in text.lower():
        return "Date not found"

    thai_months = {
        "มกราคม": 1, "กุมภาพันธ์": 2, "มีนาคม": 3, "เมษายน": 4, "พฤษภาคม": 5, "มิถุนายน": 6,
        "กรกฎาคม": 7, "สิงหาคม": 8, "กันยายน": 9, "ตุลาคม": 10, "พฤศจิกายน": 11, "ธันวาคม": 12,
        "ม.ค.": 1, "ก.พ.": 2, "มี.ค.": 3, "เม.ย.": 4, "พ.ค.": 5, "มิ.ย.": 6,
        "ก.ค.": 7, "ส.ค.": 8, "ก.ย.": 9, "ต.ค.": 10, "พ.ย.": 11, "ธ.ค.": 12
    }
    
    thai_num_map = str.maketrans('๐๑๒๓๔๕๖๗๘๙', '0123456789')
    clean_text = text.translate(thai_num_map)
    
    pattern = r"(\d{1,2})\s+([ก-๙\.]+)\s+(?:พ\.ศ\.\s+)?(\d{4})"
    match = re.search(pattern, clean_text)
    
    if match:
        day = int(match.group(1))
        month_name = match.group(2).strip()
        year_be = int(match.group(3))
        
        year_ad = year_be - 543
        month_num = thai_months.get(month_name)
        
        if not month_num and not month_name.endswith('.'):
             month_num = thai_months.get(month_name + '.')

        if month_num:
            try:
                return datetime(year_ad, month_num, day).strftime("%Y-%m-%d")
            except ValueError:
                return "Invalid Date Values"
    return "Date not found"

# CLASSIFICATION & SEARCH TOOLS 
def classify_document(text: str):
    """Categorizes document based on Thai Saraban Keywords."""
    text = text.lower()
    categories = {
        "Policy & Regulation": ["ประกาศ", "ระเบียบ", "ข้อบังคับ", "คำสั่ง"],
        "Financial & Accounting": ["การเงิน", "งบประมาณ", "ใบเสร็จ", "จัดซื้อ", "ฎีกา", "บัญชี"],
        "Medical Records": ["เวชระเบียน", "ประวัติคนไข้", "การรักษา", "พจนานุกรมโรค"],
        "Personnel": ["ประวัติบุคคล", "ทะเบียนประวัติ", "ก.พ.7", "บรรจุแต่งตั้ง"],
        "Routine Correspondence": ["หนังสือรับ", "หนังสือส่ง", "เวียน", "แจ้งเพื่อทราบ"]
    }
    for category, keywords in categories.items():
        if any(k in text for k in keywords):
            return category
    return "General Correspondence"
#if cannot found in search, use fallback rules
def get_fallback_rule(category: str):
    rules = {
        "Policy & Regulation": "Permanent (Minimum 10 years)",
        "Financial & Accounting": "10 years",
        "Medical Records": "5-10 years",
        "Personnel": "10 years after retirement",
        "Routine Correspondence": "1-5 years"
    }
    return rules.get(category, "10 years")

def search_thai_retention_rules(doc_name: str):
    """Searches go.th for retention; returns fallback if nothing found."""
    category = classify_document(doc_name)
    queries = [
        f'"{doc_name}" อายุการเก็บเอกสาร site:go.th',
        f'ตารางกำหนดอายุการเก็บเอกสาร "{category}" site:go.th'
    ]
    
    all_results = ""
    try:
        with DDGS() as ddgs:
            for q in queries:
                res = list(ddgs.text(q, max_results=2))
                for item in res:
                    all_results += f"Source: {item['href']}\nInfo: {item['body']}\n\n"
    except:
        pass

    if not all_results.strip():
        return f"Category: {category}. Standard Rule: {get_fallback_rule(category)} (No specific online update found)."
    
    return f"Category: {category}\n\nSearch Results:\n{all_results}"

# AGENT
root_agent = adk.Agent(
    name="RecordRetentionChecker",
    model='gemini-2.0-flash',
    instruction=f"""
    You are an expert in Thai Government Document Archiving and the 'ระเบียบสำนักนายกรัฐมนตรี ว่าด้วยงานสารบรรณ'.
    Today's Date: {datetime.now().strftime('%Y-%m-%d')}.

    WORKFLOW:
    1. Extract text using 'extract_thai_text_from_pdf'. Report TOOL_ERROR immediately if it fails.
    2. Identify the document title and date (Look for 'ประกาศ ณ วันที่' or 'ลงวันที่' or around the signature or the top right corner).
    3. Pass the Thai date string to 'parse_thai_date'.
    4. Pass the document title/type to 'search_thai_retention_rules'.
    5. CALCULATE the destruction eligibility:
       - Current Year - Document Year = Age.
       - Compare Age with 'Keeping Years' from search/fallback.
    
    OUTPUT FORMAT:
    Provide a Markdown Table:
    | Field | Details |
    | :--- | :--- |
    | **Document Name** | [Name found in text] |
    | **Extracted Category** | [Category from tool] |
    | **Document Date (AD)** | [Result from parse_thai_date] |
    | **Retention Period** | [Years] |
    | **Eligible for Destruction?** | [YES/NO + Reason] |
    """,
    tools=[extract_thai_text_from_pdf, search_thai_retention_rules, parse_thai_date]
)

