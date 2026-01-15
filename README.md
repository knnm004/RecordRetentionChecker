
# RecordRetentionChecker

**User Message**

![alt text](https://github.com/knnm004/RecordRetentionChecker/blob/main/assets/screenshot_userinput.jpg?raw=True)

**Final Result from Agent** 

![alt text](https://github.com/knnm004/RecordRetentionChecker/blob/main/assets/screenshot_agentresponse.jpg?raw=True)

I developed this project based on my experience with record management during my academic years. While researching the local organization, I realized that small and medium-sized teams often cannot prioritize record management. With limited staff and heavy workloads, following complex retention protocols becomes a significant burden. I created RecordRetentionChecker to simplify this process and provide much-needed support to these overworked teams.

## Key Features
- **Thai OCR**: High-accuracy text extraction using Tesseract OCR with specific support for Thai and English characters.
- **Buddhist Era Date Parsing**: Automatically converts Thai BE dates (e.g., พ.ศ. ๒๕๖๘) into standard Gregorian AD dates (YYYY-MM-DD).
- **Document Classification**: Categorizes files into standard government sectors like Policy, Financial, Personnel, and Medical Records.
- **Smart Retention Search**: Dynamically queries official `go.th` sources for current retention schedules using DuckDuckGo search.
- **Automated Verdicts**: Calculates if a document is eligible for destruction based on the extracted date and discovered retention rules.

## System Prerequisites
    Before running the agent, ensure the following external dependencies are installed on your machine:
1. **Tesseract OCR**: Required for reading Thai text from images. (Make sure to include the Thai language pack during installation).
2. **Poppler**: Required for rendering PDF pages for the OCR engine.


## Usage

1. **Activate Environment**: Ensure your virtual environment is active.
   ```cmd
   .venv\Scripts\activate
2. **Launch Agent**: Run the ADK web server from your project root.
   ```cmd
   adk web .
3. **Open Browser**: Navigate to http://localhost:8000 (or the URL shown in your terminal).
4. **Upload & Analyze**:
- Drag and drop a Thai government PDF (e.g., a Ministry Announcement or Regulation) into the chat.
- The agent will automatically trigger the OCR tool, extract the date, and search for retention rules.
 
## Use Case ExampleScenario: 
A staff member at a provincial health office needs to know if they can destroy a pile of *"Food Labeling Regulations"* from several years ago to save shelf space. 

**Step-by-Step Interaction**:
1. **User**: Uploads ```example.pdf``` (Announcement of the Ministry of Public Health No. 466)

2. **Agent Activity**:
- **OCR** : Reads the text "ประกาศ ณ วันที่ ๒๗ พฤศจิกายน พ.ศ. ๒๕๖๘"
- **Date Parsing**: Converts the Thai Buddhist Era year ๒๕๖๘ to 2025 AD.
- **Classification**: Identifies the document as "Policy & Regulation"
- **Rule Search**: Finds that standard government regulations must be kept for at least 10 years.

3. **Final Result**:

| Field | Details |
| :--- | :--- |
| **Document Name** | ประกาศกระทรวงสาธารณสุข (ฉบับที่ ๔๖๖) |
| **Extracted Category** | Policy & Regulation |
| **Document Date (AD)** | 2025-11-27 |
| **Retention Period** | 10 Years |
| **Eligible for Destruction?** | **NO** - This document is from 2025. It must be retained until 2035. |

## Limitations

### 1. Model Dependency
- **Gemini 2.0 Flash**: This project is optimized for the Gemini 2.0 Flash model. While fast and efficient, the accuracy of the final "retention verdict" depends on the model's ability to reason through Thai regulations.
- **Hallucination Risk**: Like all Large Language Models (LLMs), the agent may occasionally misinterpret complex legal nuances or provide incorrect dates if the OCR text is garbled. Always verify the final output against official sources.

### 2. Language & File Support
- **Language**: The core logic is designed for **Thai Government Documents**. While it uses English for reasoning, the date parsing and OCR are specifically tuned for Thai Buddhist Era (BE) formats. It may not perform as intended on international documents or other calendar systems.
- **Handwriting**: The OCR engine (Tesseract) works best on typed, printed text. Handwritten notes, signatures, or highly degraded physical scans may lead to poor text extraction and incorrect results.

### 3. OCR & Image Quality
- **Resolution**: Low-resolution scans (below 300 DPI) may result in "noise" that confuses the Thai character recognition, leading to errors in the extracted year or document title.
- **Complex Layouts**: Documents with multi-column layouts, heavy watermarks, or complex tables may cause the OCR to read text out of order, impacting the agent's understanding.

### 4. Internet Connectivity
- **Web Search**: The `search_thai_retention_rules` tool requires an active internet connection to query DuckDuckGo and official government portals. If the search results are blocked or the site is down, the agent may default to general knowledge rather than specific, up-to-date laws.

## 📂 Project Structure

```text
RecordRetentionChecker/
├── .adk/              # Local ADK session data (ignored by git)
├── .venv/             # Python virtual environment 
├── __init__.py        # Package initialization; exposes the root_agent
├── .env               # Private environment variables and paths
├── .env.example       # Template for environment variables
├── agent.py           # Main logic, tools, and agent definition
├── README.md          # Project documentation
└── requirements.txt   # List of Python dependencies


