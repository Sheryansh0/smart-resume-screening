# app.py

from flask import Flask, render_template, request, session, send_file
import pandas as pd
import io
import os
import spacy
import re
from config import Config
from modules.sentiment_analysis import get_sentiment_score, analyze_resume_sentiment
from modules.resume_parser import (
    extract_text_from_pdf, extract_contact_info,
    extract_education, extract_experience, extract_projects, extract_years_of_experience
)
from modules.email_sender import send_rejection_email
from modules.skill_matcher import calculate_weighted_match_score
from modules.job_parser import extract_job_details, extract_education_requirements
from modules.utils import ensure_upload_folder_exists
from modules.skills import skill_keywords  # Import the skill set
from modules.fraud_detection import detect_fraud  # Import the fraud detection module

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY
app.config["UPLOAD_FOLDER"] = Config.UPLOAD_FOLDER

# Ensure 'uploads' folder exists
ensure_upload_folder_exists(app.config["UPLOAD_FOLDER"])

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Store screened resumes globally
screened_resumes = []

def extract_candidate_name(file_path):
    """
    Extract candidate name from the file name.
    Assumes the file name is in the format: Firstname_Lastname_Resume.pdf or Firstname_Lastname.pdf
    """
    # Get the file name without the directory path
    file_name = os.path.basename(file_path)
    
    # Remove the file extension (e.g., ".pdf")
    file_name_without_ext = os.path.splitext(file_name)[0]
    
    # Extract the name using regex
    # Matches "Firstname_Lastname" or "Firstname Lastname"
    name_pattern = re.compile(r"([A-Z][a-z]+)[_ ]([A-Z][a-z]+)")
    match = name_pattern.search(file_name_without_ext)
    
    if match:
        # Combine the first and last name
        first_name = match.group(1)
        last_name = match.group(2)
        return f"{first_name} {last_name}"
    
    # If no match is found, return "Unknown Candidate"
    return "Unknown Candidate"

def extract_skills(text):
    """Extract skills from text using predefined skill matching."""
    doc = nlp(text.lower())
    return list(set(token.text for token in doc if token.text in skill_keywords))

def compare_education(candidate_education, job_education):
    """Compare candidate's education with job's education requirements."""
    if not candidate_education or not job_education:
        return "N/A"

    # Check if any of the candidate's education matches the job's education requirements
    for edu in candidate_education:
        if any(req.lower() in edu.lower() for req in job_education):
            return "Yes"
    return "No"

def compare_experience(candidate_experience_years, job_experience_years):
    """Determine if candidate meets experience requirement."""
    if job_experience_years == 0:
        return "Yes"  # No experience requirement means candidate meets it
    return "Yes" if candidate_experience_years >= job_experience_years else "No"

def calculate_statistics(screened_resumes):
    """Calculate statistics for the dashboard."""
    total_resumes = len(screened_resumes)
    suitable_resumes = sum(1 for res in screened_resumes if res["suitable"] == "Yes")
    unsuitable_resumes = total_resumes - suitable_resumes
    suitable_percentage = round((suitable_resumes / total_resumes) * 100, 2) if total_resumes > 0 else 0
    unsuitable_percentage = round((unsuitable_resumes / total_resumes) * 100, 2) if total_resumes > 0 else 0
    average_match_score = round(sum(res["match_score"] for res in screened_resumes) / total_resumes, 2) if total_resumes > 0 else 0

    # Calculate top skills lacking
    skills_lacking = {}
    for res in screened_resumes:
        for skill in res["skills_lacking"]:
            skills_lacking[skill] = skills_lacking.get(skill, 0) + 1
    top_skills_lacking = sorted(skills_lacking.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "total_resumes": total_resumes,
        "suitable_percentage": suitable_percentage,
        "unsuitable_percentage": unsuitable_percentage,
        "average_match_score": average_match_score,
        "top_skills_lacking": top_skills_lacking
    }

@app.route("/", methods=["GET", "POST"])
def home():
    global screened_resumes

    if request.method == "POST":
        if "job_description" in request.form:
            job_description = request.form.get("job_description", "").strip().lower()
            if job_description:
                session["job_description"] = job_description
                session["job_skills"] = extract_skills(job_description)
                job_details = extract_job_details(job_description)
                session["job_title"] = job_details["title"]
                session["job_experience"] = job_details["experience"]
                session["job_location"] = job_details["location"]
                session["job_salary"] = job_details["salary"]
                session["job_experience_years"] = extract_years_of_experience(job_details["experience"])
                session["job_education"] = extract_education_requirements(job_description)

                # Initialize skill weights (default weight is 1)
                session["skill_weights"] = {skill: 1 for skill in session["job_skills"]}

        elif "resume_pdf" in request.files:
            files = request.files.getlist("resume_pdf")
            for file in files:
                if not file or not file.filename.endswith(".pdf"):
                    continue

                file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
                file.save(file_path)

                # Extract candidate name from file name
                candidate_name = extract_candidate_name(file_path)

                # Extract text from PDF
                resume_text = extract_text_from_pdf(file_path)
                resume_skills = extract_skills(resume_text)

                job_skills = session.get("job_skills", [])
                skill_weights = session.get("skill_weights", {})
                match_score = calculate_weighted_match_score(resume_skills, job_skills, skill_weights)
                suitability = "Yes" if match_score >= 50 else "No"

                # Calculate skills lacking
                skills_lacking = list(set(job_skills) - set(resume_skills))
                candidate_experience_years = extract_years_of_experience(resume_text)

                # Check if candidate meets experience requirement
                job_experience_years = session.get("job_experience_years", 0)
                experience_met = compare_experience(candidate_experience_years, job_experience_years)
                
                # Extract contact information
                contact_info = extract_contact_info(resume_text)
                projects = extract_projects(resume_text)
                candidate_experience = extract_experience(resume_text)
                candidate_experience = candidate_experience if candidate_experience else ["N/A"]  # Handle empty experience field if present
                
                # Check if candidate meets education requirement
                education = extract_education(resume_text)
                education = education if education else ["N/A"]  # Handle empty education field if present
                
                job_education = session.get("job_education", ["N/A"])
                education_met = compare_education(education, job_education)

                # Perform Sentiment Analysis
                sentiment_label, sentiment_score = get_sentiment_score(resume_text)

                # Perform Fraud Detection
                # Inside the home() function, where you call detect_fraud
                fraud_result = detect_fraud({
                    "summary": resume_text,
                    "skills": resume_skills,
                    "education": education,
                    "experience": candidate_experience,  # Ensure this is a list of dictionaries
                })
                

                screened_resumes.append({
                    "slno": len(screened_resumes) + 1,
                    "name": candidate_name,
                    "email": contact_info["email"],
                    "phone": contact_info["phone"],
                    "education": education,
                    "education_met": education_met,
                    "experience": candidate_experience,
                    "candidate_experience_years": candidate_experience_years,
                    "projects": projects,
                    "skills": resume_skills,
                    "suitable": suitability,
                    "match_score": match_score,
                    "skills_lacking": skills_lacking,
                    "experience_met": experience_met,
                    "sentiment": sentiment_label,
                    "sentiment_score": sentiment_score,
                    "plagiarism": fraud_result["plagiarism"],
                    "institution_check": fraud_result["institution_check"],
                    "experience_gap": fraud_result["experience_gap"],
                    "fraud_status": fraud_result["fraud_status"],
                })

                # Send rejection email if candidate is unsuitable
                if suitability == "No":
                    send_rejection_email(contact_info["email"], candidate_name, skills_lacking, match_score)

                os.remove(file_path)

    # Calculate statistics for the dashboard
    statistics = calculate_statistics(screened_resumes)

    return render_template(
        "index.html",
        job_description=session.get("job_description", ""),
        job_skills=session.get("job_skills", []),
        job_title=session.get("job_title", "N/A"),
        job_experience=session.get("job_experience", "N/A"),
        job_location=session.get("job_location", "N/A"),
        job_salary=session.get("job_salary", "N/A"),
        skill_weights=session.get("skill_weights", {}),
        screened_resumes=screened_resumes,
        statistics=statistics
    )

@app.route("/update-weights", methods=["POST"])
def update_weights():
    if request.method == "POST":
        skill_weights = {}
        for skill in session.get("job_skills", []):
            weight = request.form.get(f"weight_{skill}", "1")
            skill_weights[skill] = int(weight)
        session["skill_weights"] = skill_weights
    return "Weights updated successfully."

@app.route("/download-report")
def download_report():
    global screened_resumes
    df = pd.DataFrame(screened_resumes)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    return send_file(
        io.BytesIO(csv_buffer.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="screened_resumes.csv"
    )

@app.route("/clear-resumes")
def clear_resumes():
    global screened_resumes
    screened_resumes = []
    return "Cleared all resumes."

@app.route("/analyze-sentiment", methods=["GET"])
def analyze_sentiment():
    global screened_resumes
    if not screened_resumes:
        return "No resumes to analyze."

    # Convert screened_resumes to a DataFrame
    df = pd.DataFrame(screened_resumes)
    
    # Perform sentiment analysis
    sentiment_results = analyze_resume_sentiment(df)
    
    # Save results to a CSV file
    csv_buffer = io.StringIO()
    sentiment_results.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    
    return send_file(
        io.BytesIO(csv_buffer.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="resume_sentiment_analysis.csv"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)