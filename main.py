import streamlit as st
import pandas as pd
import pdfplumber
from langchain_groq import ChatGroq
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate
from io import BytesIO
import os
from dotenv import load_dotenv
load_dotenv()

# Initialize the ChatGroq LLM model
llm = ChatGroq(
    temperature=0, 
    api_key = os.getenv('API_KEY'),
    model_name="llama-3.1-70b-versatile"
)

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Function to load job description from a webpage link
def load_job_description(link):
    loader = WebBaseLoader(link)
    page_data = loader.load().pop().page_content
    return page_data

# Function to extract the summary of a job description
def extract_job_summary(page_data):
    prompt_extract = PromptTemplate.from_template(
        """
        ### JOB DESCRIPTION TEXT:
        {page_data}
        
        ### INSTRUCTION:
        Summarize the job description provided. The summary should include the key role, required experience, key skills, and a brief description of what the job entails. 
        Only return the summary in text format. Do not provide a preamble.
        """
    )
    chain_extract = prompt_extract | llm 
    res = chain_extract.invoke(input={'page_data': page_data})
    return res.content

# Function to extract the summary from a CV
def extract_cv_summary(cv_text):
    prompt_cv_extract = PromptTemplate.from_template(
        """
        ### CV TEXT:
        {cv_text}
        
        ### INSTRUCTION:
        Summarize the CV provided. The summary should include the candidate's role, experience, key skills, and a brief description of the candidate's qualifications. 
        Only return the summary in text format. Do not provide a preamble.
        """
    )
    chain_cv_extract = prompt_cv_extract | llm
    res = chain_cv_extract.invoke({"cv_text": cv_text})
    return res.content

# Function to evaluate the fit between job description and CV and generate an email or a "not fit" message
def evaluate_fit(job_summary, candidate_summary):
    prompt_evaluate_fit = PromptTemplate.from_template(
        """
        ### JOB DESCRIPTION SUMMARY:
        {job_summary}
        
        ### CANDIDATE DESCRIPTION SUMMARY:
        {candidate_summary}
        
        ### INSTRUCTION:
        Compare the job description summary with the candidate description summary provided. Be strict in evaluating the match between the job's required skills and experience and the candidate's qualifications. 
        If the candidate's qualifications fit the job role well, generate a professional email expressing the candidate's interest in the role, highlighting their qualifications, and be sure to include the candidate's CV link.
        If the qualifications do not match, return a message indicating that the candidate does not meet the requirements for this role.
        
        Provide your response in the following format:
        - If a match is found: "Fit: True", followed by the email content.
        - If a match is not found: "Fit: False", followed by a brief explanation of why the candidate does not fit the role.
        Do not provide a preamble.
        """
    )
    chain_evaluate_fit = prompt_evaluate_fit | llm
    res = chain_evaluate_fit.invoke({
        "job_summary": job_summary,
        "candidate_summary": candidate_summary
    })
    return res.content

# Streamlit interface
st.title("Auto CV Matchmaker")

# Upload Job Description (CSV or single link)
job_desc_type = st.radio("Upload job descriptions as a CSV file or enter a single link:", ("CSV File", "Single Link"))

# Upload CSV or enter a link
if job_desc_type == "CSV File":
    job_csv = st.file_uploader("Upload the CSV file with job description links", type=["csv"])
elif job_desc_type == "Single Link":
    job_link = st.text_input("Enter the link to the job description:")

# Upload Resume PDF
cv_file = st.file_uploader("Upload the candidate's resume (PDF)", type=["pdf"])

if cv_file:
    # Extract text from the uploaded CV
    cv_text = extract_text_from_pdf(cv_file)
    candidate_summary = extract_cv_summary(cv_text)

    if job_desc_type == "CSV File" and job_csv:
        # Process each job description from the CSV
        job_data = pd.read_csv(job_csv)
        job_descriptions = job_data['link']

        results = []
        for link in job_descriptions:
            page_data = load_job_description(link)
            job_summary = extract_job_summary(page_data)
            result = evaluate_fit(job_summary, candidate_summary)
            results.append(result)

        # Add results to the CSV
        job_data['match_result'] = results
        csv_buffer = BytesIO()
        job_data.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        st.download_button("Download the result CSV", csv_buffer, "job_match_results.csv", mime="text/csv")

    elif job_desc_type == "Single Link" and job_link:
        # Process a single job description
        page_data = load_job_description(job_link)
        job_summary = extract_job_summary(page_data)
        result = evaluate_fit(job_summary, candidate_summary)
        st.write(result)
