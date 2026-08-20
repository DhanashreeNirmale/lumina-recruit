# API Integration Guide

This document describes how Lumina Recruit integrates with third-party systems: **Google Gemini API** (for extraction/explanation) and the **Judge0 API** (for code execution).

---

## 1. Google Gemini API

Lumina Recruit utilizes the `google-genai` library to interface with the Gemini API (model `gemini-3.6-flash`).

### Configurations
Environment Variables:
- `GEMINI_API_KEY`: API authorization key.

### Integration Locations
- **`agents/resume_agent.py`**:
  - Triggers on candidate resume upload.
  - Extracts full profile details matching the JSON contract schema.
  - **Fallback:** Executes deterministic regex for email, phone, notice period, and keyword skill matching if the key is missing or offline.
- **`agents/job_agent.py`**:
  - Triggers on recruiter job postings.
  - Returns structured requirements.
  - **Fallback:** Extracts job title from the first non-empty line and scans against default tech skills.
- **`agents/matching_agent.py`**:
  - Triggers on application submission.
  - Formats compatibility statistics and requests a structured narrative report.
  - **Fallback:** Returns a structured summary detailing matched and missing skills.
- **`agents/recruiter_agent.py`**:
  - Provides a question answering console.
  - **Fallback:** Scans query keywords for skills or experience parameters and filters candidates.

---

## 2. Judge0 Sandbox Compiler API

Coding assessments are executed dynamically inside a Judge0 instance.

### Configurations
- `JUDGE0_API_URL`: URL to the compiler instance (default: `http://localhost:2358`).

### Integration Locations
- **`services/judge0_service.py`**:
  - Submits POST queries to `/submissions?wait=true&base64_encoded=false`.
  - Maps common languages: Python (ID 71), Java (ID 62), and C++ (ID 54).
  - **Fallback:** If Judge0 is offline:
    - *Python:* Compiles and runs code inside a safe local sub-thread environment, matching outputs.
    - *Java/C++:* Auto-approves the submission if code syntax length is non-empty, appending warning notifications.
