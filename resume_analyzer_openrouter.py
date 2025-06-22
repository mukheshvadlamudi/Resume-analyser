import streamlit as st
import PyPDF2
import requests

# --- UI Config ---
st.set_page_config(page_title="Resume Analyzer", page_icon="📄")
st.title("📄 Resume Analyzer (LLM - OpenRouter)")

st.markdown("Upload your resume PDF and get instant feedback powered by LLaMA 3.\n\n💡 *For best results, enter your OpenRouter API key below.*")

# --- User Inputs ---
api_key = st.secrets["OPENROUTER_API_KEY"]
st.write("🔐 API Key Present:", "OPENROUTER_API_KEY" in st.secrets)
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
You are an AI resume reviewer integrated into a GenAI-based resume feedback app.

Your job is to read the following resume text and provide detailed, structured feedback that helps job seekers improve their resume quality and relevance.

Please use this output format:

### ✅ Strengths
- Bullet point strengths of this resume

### ⚠️ Weaknesses
- Bullet point issues (clarity, formatting, missing info)

### 🛠️ Suggestions for Improvement
- Specific, actionable advice

### 📊 ATS Score
**Score:** /100  
*Based on keyword relevance, formatting, role alignment, and content completeness.*

### 🔁 Final Summary
Summarize in 1–2 sentences the top things the applicant should improve or keep doing well.

"""
    if job_role:
        prompt += f"\nThis resume is intended for the role of **{job_role}**."

    if is_fresher:
        prompt += "\nNote: The applicant is a fresher. Focus on academic achievements, projects, certifications, and relevant skills instead of work experience."

    prompt += f"\n\n---\n\nResume:\n{text}"
    return prompt.strip()

# --- OpenRouter call ---
def analyze_resume(prompt, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://chat.openrouter.ai"
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
