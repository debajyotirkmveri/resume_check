import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
import pandas as pd

load_dotenv() ## load all our environment variables

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_repsonse(input):
    model=genai.GenerativeModel('gemini-pro')
    response=model.generate_content(input)
    return response.text

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += str(page.extract_text())
    return text

def extract_personal_info(text):
    # This function assumes that the resume text includes the name and experience in a known format.
    # You might need to adjust the parsing logic based on actual resume format.
    name = "Not Available"
    experience = "Not Available"
    
    # Example parsing logic (you should adapt it to your resume format)
    lines = text.split('\n')
    for line in lines:
        if "Name:" in line:
            name = line.replace("Name:", "").strip()
        elif "Experience:" in line:
            experience = line.replace("Experience:", "").strip()
    
    return name, experience

# Prompt Template
input_prompt = """
Hey Act Like a skilled or very experienced ATS(Application Tracking System)
with a deep understanding of the tech field, software engineering, data science, data analysis,
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
    if uploaded_file is not None:
        text = input_pdf_text(uploaded_file)
        name, experience = extract_personal_info(text)
        
        # Construct the input for the AI model
        formatted_prompt = input_prompt.format(text=text, jd=jd)
        response = get_gemini_repsonse(formatted_prompt)
        
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

        # Display the results
        st.subheader("Resume Analysis")
        st.write(f"**Name:** {name}")
        st.write(f"**Experience:** {experience}")

        # Create a DataFrame for tabular display
        df = pd.DataFrame({
            "Metric": ["JD Match", "Missing Keywords", "Profile Summary"],
            "Value": [jd_match, ', '.join(missing_keywords), profile_summary]
        })

        st.table(df)
