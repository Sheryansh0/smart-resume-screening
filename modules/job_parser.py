# modules/job_parser.py
import re

def extract_job_details(job_description):
    """Extract job details like title, experience, location, and salary from job description."""
    job_details = {
        "title": "N/A",
        "experience": "N/A",
        "location": "N/A",
        "salary": "N/A"
    }

    # Extract job title (first line)
    title_match = re.search(r"^[^\n]+", job_description)
    if title_match:
        job_details["title"] = title_match.group(0).strip()

    # Extract experience (e.g., "3+ years of experience")
    experience_pattern = r"(\d+\+?\s*(years?|yrs?)\s*(of\s*experience)?)"
    experience_match = re.search(experience_pattern, job_description, re.IGNORECASE)
    if experience_match:
        job_details["experience"] = experience_match.group(0).strip()

    # Extract location (e.g., "New York, NY" or "Remote")
    location_pattern = r"(remote|hybrid|onsite|[\w\s]+,\s*[A-Z]{2})"
    location_match = re.search(location_pattern, job_description, re.IGNORECASE)
    if location_match:
        job_details["location"] = location_match.group(0).strip()

    # Extract salary range (e.g., "$80,000 - $100,000")
    salary_pattern = r"(\$\d{1,3}(,\d{3})\s-\s*\$\d{1,3}(,\d{3})*)"
    salary_match = re.search(salary_pattern, job_description)
    if salary_match:
        job_details["salary"] = salary_match.group(0).strip()

    return job_details

def extract_education_requirements(text):
    """Extract education requirements from job description."""
    education_keywords = ["bachelor", "master", "phd", "degree", "diploma", "university", "college"]
    education_requirements = []
    for sent in text.split("\n"):
        if any(keyword in sent.lower() for keyword in education_keywords):
            education_requirements.append(sent.strip())
    return education_requirements if education_requirements else ["N/A"]