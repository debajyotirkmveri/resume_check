import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
import pandas as pd

load_dotenv()  # Load all our environment variables

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input)
    return response.text

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += str(page.extract_text())
    return text

# Prompt Template
input_prompt = """
Hey Act Like a skilled or very experienced ATS(Application Tracking System) with a deep understanding of the tech field, software engineering, data science, data analysis,
and big data engineering. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide
the best assistance for improving the resume. Assign the percentage matching based
on JD and
the missing keywords with high accuracy.
Resume: {text}
Description: {jd}

I want the response in one single string having the structure
{{"JD Match":"%","MissingKeywords":[],"Profile Summary":""}}
"""

## Streamlit app
st.title("Smart ATS")
st.text("Improve Your Resume ATS")

jd = st.text_area("Paste the Job Description")
uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload the PDF")

submit = st.button("Submit")

if submit:
    if uploaded_file is not None and jd:
        text = input_pdf_text(uploaded_file)
        
        # Construct the input for the AI model
        formatted_prompt = input_prompt.format(text=text, jd=jd)
        response = get_gemini_response(formatted_prompt)
        
        # Parse the AI response
        try:
            response_dict = json.loads(response)
            jd_match = response_dict.get("JD Match", "Not Available")
            missing_keywords = response_dict.get("MissingKeywords", [])
            profile_summary = response_dict.get("Profile Summary", "Not Available")
        except json.JSONDecodeError:
            jd_match = "Error in response format"
            missing_keywords = []
            profile_summary = "Error in response format"

        # Create a DataFrame for tabular display
        df = pd.DataFrame({
            "Metric": ["JD Match", "Missing Keywords", "Profile Summary"],
            "Value": [jd_match, ', '.join(missing_keywords), profile_summary]
        })

        st.subheader("Resume Analysis")
        st.table(df)
    else:
        st.error("Please provide both the job description and upload a resume.")
