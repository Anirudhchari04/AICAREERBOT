import streamlit as st
import PyPDF2
import requests
import json
import os
from fpdf import FPDF
import tempfile

# Set your Groq API key here
API_KEY = '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'  # Replace this with your actual Groq API key

# Set the Groq API URL
API_URL = 'https://api.groq.com/openai/v1/chat/completions'  # Use the correct Groq API endpoint

# Set the title of the Streamlit app
st.title("AI Career Assistant with Groq API")

st.write("""
    This app helps you enhance your resume, match job descriptions, prepare for interviews, and build your portfolio using AI.
""")

# Function to extract text from PDF file
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text.strip()

# Function to interact with Groq API
def get_groq_response(prompt):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        'model': 'qwen-2.5-32b',  # Change to the model you want to use
        'messages': [{'role': 'user', 'content': prompt}]
    }

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content'].strip()
        else:
            return f"Error: Unable to get a response from Groq API. Status code: {response.status_code}"
    except Exception as e:
        return f"Error: {e}"

# ----------- Resume Upload & Enhancement Section ----------- 
st.header("Upload Your Resume (PDF)")
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if 'enhanced_resume' not in st.session_state:
    st.session_state.enhanced_resume = ""
    st.session_state.previous_resume = ""

if uploaded_file is not None:
    resume_text = extract_text_from_pdf(uploaded_file)
    if not st.session_state.enhanced_resume:
        st.session_state.enhanced_resume = resume_text  # Initialize with original resume

st.header("Enhance Your Resume")
st.session_state.enhanced_resume = st.text_area("Your Resume", st.session_state.enhanced_resume, height=300)

if st.button("Enhance Resume"):
    st.session_state.previous_resume = st.session_state.enhanced_resume  # Save current before enhancing
    prompt = f"Provide an enhanced version of the following resume. Keep the original structure intact and focus on improving the professionalism, impact, and clarity. Do not include any explanations, descriptions, or additional content. Just return the revised resume text in the format of a resume:\n\n{st.session_state.enhanced_resume}"
    enhanced_text = get_groq_response(prompt)
    st.session_state.enhanced_resume = enhanced_text  # Store only the cleaned enhancement
    st.rerun()

if st.button("Previous Enhancement"):
    st.session_state.enhanced_resume, st.session_state.previous_resume = st.session_state.previous_resume, st.session_state.enhanced_resume
    st.rerun()

# ----------- Job Matching Section ----------- 
st.header("Job Matching")
job_description = st.text_area("Enter a job description:")

if st.button("Match Job"):
    if job_description and st.session_state.enhanced_resume:
        prompt = f"Analyze the following resume and compare it with this job description. Provide a detailed skill gap analysis and highlight strengths:\n\nJob Description:\n{job_description}\n\nResume:\n{st.session_state.enhanced_resume}"
        job_match_results = get_groq_response(prompt)
        st.subheader("Job Match Results")
        st.write(job_match_results)
    else:
        st.write("Please enter a job description and upload your resume.")

# ----------- Interview Preparation Section ----------- 
st.header("Interview Preparation")

# Buttons for two different modes
view_questions_clicked = st.button("View Questions & Focus Areas")
if view_questions_clicked:
    if st.session_state.enhanced_resume:
        prompt = f"Generate 5 structured interview questions directly based on the resume content below. Provide the key focus areas for each question:\n\nResume Content:\n{st.session_state.enhanced_resume}"
        interview_questions = get_groq_response(prompt)
        st.subheader("Interview Questions & Key Focus Areas")
        st.write(interview_questions)
    else:
        st.write("Please upload a resume to generate interview questions.")

# ----------- Portfolio Builder Section ----------- 
st.header("Portfolio Builder")

# Automatically generate the portfolio based on the resume content
if uploaded_file is not None:
    # Extract key information for portfolio generation
    prompt = f"""
    Based on the following resume content, generate a portfolio page with a structured HTML layout that includes:
    1. A heading "Portfolio"
    2. A brief introduction about the developer
    3. A list of projects with the following details for each:
       - Project title
       - Description
       - Skills used
       - Project link (if available)
    Ensure the portfolio is in HTML format and includes proper HTML tags for structure, including headings, paragraphs, and links.

    Resume Content:
    {st.session_state.enhanced_resume}
    """

    portfolio_html = get_groq_response(prompt)

    if portfolio_html:
        # Save the generated portfolio to a temporary HTML file
        temp_dir = tempfile.mkdtemp()
        html_filename = os.path.join(temp_dir, "portfolio.html")
        with open(html_filename, 'w') as f:
            f.write(portfolio_html)

        # Provide download link for the generated HTML portfolio
        with open(html_filename, "r") as file:
            st.download_button("Download Portfolio", file, file_name="portfolio.html")
    else:
        st.write("Failed to generate portfolio content. Please ensure your resume contains enough project details.")

# ----------- Footer Section ----------- 
st.write("""
    AI Career Assistant - Your AI-powered career companion.
""")
