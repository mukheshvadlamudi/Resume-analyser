import streamlit as st
import PyPDF2
import requests

# --- UI Config ---
st.set_page_config(page_title="Resume Analyzer", page_icon="📄")
st.title("📄 Resume Analyzer (LLM - OpenRouter)")

st.markdown("Upload your resume PDF and get instant feedback powered by LLaMA 3.")

# --- User Inputs ---
api_key = st.secrets["OPENROUTER_API_KEY"]
job_role = st.text_input("🎯 Target Job Role (optional)", placeholder="e.g., Data Analyst, Web Developer")
is_fresher = st.checkbox("🧑‍🎓 I am a fresher (0 work experience)")
uploaded_file = st.file_uploader("📎 Upload your Resume (PDF only)", type="pdf")

# --- Config ---
MODEL = "meta-llama/llama-3-8b-instruct"
MAX_TOKENS = 1000

# --- Extract resume text from PDF ---
def extract_text_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text

# --- Build the prompt ---
def build_prompt(text, job_role, is_fresher):
    prompt = f"""
You are an AI resume reviewer integrated into a GenAI-based resume analysis platform.

Your task is to evaluate a candidate's resume and provide clear, structured feedback to help improve their chances of passing Applicant Tracking Systems (ATS) and impressing recruiters.

Use the following format in your response:

### ✅ Strengths
- Clearly state 2–4 standout points about the resume

### ⚠️ Weaknesses
- List 2–4 areas that need improvement (content, formatting, clarity, etc.)

### 🛠️ Suggestions for Improvement
- Give actionable suggestions to enhance the resume’s quality

### 📊 ATS Score
**Score:** /100  
*Short explanation (1–2 lines) of how the score was determined, based on keyword usage, role alignment, formatting, and relevance.*

### 🔁 Final Summary
Give a 1–2 sentence wrap-up of the most important thing the candidate should improve or continue doing.
"""

    if job_role:
        prompt += f"\n\nThis resume is intended for the role of **{job_role}**. Tailor your feedback accordingly."

    if is_fresher:
        prompt += "\n\nNote: The candidate is a fresher. Focus on skills, projects, academics — not work experience."

    prompt += f"\n\n---\nResume Content:\n{text}"
    return prompt.strip()

# --- OpenRouter call ---
def analyze_resume(prompt, api_key):
    headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://resumeanalyzero.streamlit.app/"
    }


    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": MAX_TOKENS
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"⚠️ API Error {response.status_code}: {response.text}"

# --- Process resume ---
if uploaded_file and api_key:
    with st.spinner("🔍 Analyzing your resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)
        if resume_text.strip():
            prompt = build_prompt(resume_text, job_role, is_fresher)
            feedback = analyze_resume(prompt, api_key)
            st.subheader("🧠 AI Feedback")
            st.markdown(feedback)
        else:
            st.error("❌ Could not extract readable text from the PDF.")
