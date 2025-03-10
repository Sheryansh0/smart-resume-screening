# modules/resume_parser.py
import re
import spacy
import pdfplumber
import os

nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip().lower()


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

def extract_contact_info(text):
    """Extract email and phone number from resume text."""
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    phone_pattern = r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"

    email = re.search(email_pattern, text)
    phone = re.search(phone_pattern, text)

    return {
        "email": email.group(0) if email else "N/A",
        "phone": phone.group(0) if phone else "N/A"
    }

def extract_education(text):
    """Extract education details from resume text."""
    education_keywords = ["bachelor", "master", "phd", "degree", "diploma", "university", "college"]
    education = []
    for sent in text.split("\n"):
        if any(keyword in sent.lower() for keyword in education_keywords):
            education.append(sent.strip())
    return education if education else ["N/A"]

def extract_experience(text):
    """Extract experience details from resume text."""
    experience_keywords = ["experience", "worked", "intern", "job", "role"]
    experience = []
    for sent in text.split("\n"):
        if any(keyword in sent.lower() for keyword in experience_keywords):
            experience.append(sent.strip())
    return experience if experience else ["N/A"]

def extract_projects(text):
    """Extract projects from resume text."""
    project_keywords = ["project", "developed", "built", "created"]
    projects = []
    for sent in text.split("\n"):
        if any(keyword in sent.lower() for keyword in project_keywords):
            projects.append(sent.strip())
    return projects if projects else ["N/A"]

def extract_years_of_experience(text):
    """Extract years of experience from text."""
    experience_pattern = r"(\d+)\s*(years?|yrs?)"
    match = re.search(experience_pattern, text, re.IGNORECASE)
    return int(match.group(1)) if match else 0

def extract_experience(text):
    """
    Extract work experience from resume text.
    
    :param text: Resume text.
    :return: List of dictionaries containing experience details.
    """
    # Example implementation (modify based on your actual logic)
    experience = []
    # Use regex or NLP to extract experience details
    # Example regex pattern for dates (modify as needed)
    date_pattern = re.compile(r"(\d{4}-\d{2}-\d{2})")
    matches = date_pattern.findall(text)
    
    # Example: Create experience entries
    for i in range(0, len(matches), 2):
        if i + 1 < len(matches):
            experience.append({
                "start_date": matches[i],
                "end_date": matches[i + 1],
                "job_title": "Example Job Title",  # Extract this from text
                "company": "Example Company",  # Extract this from text
            })
    
    return experience
def extract_education(text):
    """
    Extract education details from resume text.
    
    :param text: Resume text.
    :return: List of dictionaries containing education details.
    """
    # Example implementation (modify based on your actual logic)
    education = []
    # Use regex or NLP to extract education details
    # Example regex pattern for institutions (modify as needed)
    institution_pattern = re.compile(r"(University|College|Institute) of [A-Za-z]+")
    matches = institution_pattern.findall(text)
    
    # Example: Create education entries
    for match in matches:
        education.append({
            "institution": match,
            "degree": "Example Degree",  # Extract this from text
            "duration": "Example Duration",  # Extract this from text
        })
    
    return education