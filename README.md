# Auto CV MatchMaker

This is a Streamlit application that takes job descriptions and a candidate's resume, then evaluates if the candidate is a good fit for the job based on their qualifications. The application can take a CSV file containing multiple job description links or a single job description link, and a resume in PDF format. It generates a match result and creates a CSV output file if multiple job descriptions are provided.

## Features
- Upload job descriptions via a CSV file or provide a single link to a job description.
- Upload the candidate’s resume in PDF format.
- Automatically extract job description summaries and candidate qualifications.
- Compare job description and resume to generate a match evaluation.
- Download the result as a CSV file for batch processing of job descriptions from a CSV.
- Chat-style interface for single job description evaluations.

## How to Use

### 1. Install Dependencies
Install the required packages by running the following command:

```bash
pip install -r requirements.txt
