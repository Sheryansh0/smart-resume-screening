# modules/fraud_detection.py

import pandas as pd
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def detect_fraud(resume_data):
    """
    Function to detect fraud in the provided resume data.
    
    :param resume_data: Data to be analyzed for fraud.
    :return: Dictionary containing plagiarism, institution check, experience gap, and fraud status.
    """
    # Perform plagiarism check
    plagiarism_result = check_plagiarism(resume_data)
    
    # Perform experience gap check
    gap_result = check_experience_gaps(resume_data)
    
    # Perform institution check
    institution_result = check_institution(resume_data)
    
    # Determine fraud status
    fraud_status = "Fraud" if plagiarism_result or gap_result or institution_result else "Not Fraud"
    
    return {
        "plagiarism": plagiarism_result,
        "institution_check": institution_result,
        "experience_gap": gap_result,
        "fraud_status": fraud_status,  # Add fraud status
    }

def check_plagiarism(resume_data, threshold=0.8, resume_data_file="resume_data.csv"):
    """
    Check for plagiarism by comparing the resume text with a dataset of existing resumes.
    
    :param resume_data: Resume data containing text to check.
    :param threshold: Similarity threshold to consider as plagiarism (default: 0.8).
    :param resume_data_file: Path to the CSV file containing existing resumes.
    :return: Boolean indicating if plagiarism was detected.
    """
    # Load the dataset of existing resumes from the CSV file
    try:
        existing_resumes_df = pd.read_csv(resume_data_file)
        # Assuming the CSV has a column named 'resume_text' containing the resume text
        existing_resumes = existing_resumes_df["resume_text"].tolist()
    except FileNotFoundError:
        print(f"Error: The file {resume_data_file} was not found.")
        return False
    except KeyError:
        print(f"Error: The CSV file must contain a column named 'resume_text'.")
        return False

    # Combine the resume text from the provided data
    resume_text = " ".join([
        resume_data.get("summary", ""),
        " ".join(resume_data.get("skills", [])),
        " ".join(resume_data.get("education", [])),
        " ".join(resume_data.get("experience", [])),
    ])

    # Add the new resume text to the dataset
    all_texts = existing_resumes + [resume_text]

    # Compute TF-IDF and cosine similarity
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    similarity_matrix = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])

    # Check if any similarity score exceeds the threshold
    if any(score > threshold for score in similarity_matrix[0]):
        return True  # Plagiarism detected
    return False  # No plagiarism

def check_experience_gaps(resume_data, gap_threshold=365):
    """
    Check for suspicious gaps in work experience.
    
    :param resume_data: Resume data containing work experience.
    :param gap_threshold: Maximum allowed gap in days (default: 365 days).
    :return: Boolean indicating if suspicious gaps were detected.
    """
    experience = resume_data.get("experience", [])
    if not experience:
        return False  # No experience to check

    # Ensure experience is a list of dictionaries
    if isinstance(experience, list) and all(isinstance(exp, dict) for exp in experience):
        # Parse dates and calculate gaps
        previous_end_date = None
        for exp in experience:
            start_date_str = exp.get("start_date", "")
            end_date_str = exp.get("end_date", "")

            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            except ValueError:
                # Skip invalid date formats
                continue

            if previous_end_date:
                gap_days = (start_date - previous_end_date).days
                if gap_days > gap_threshold:
                    return True  # Suspicious gap detected

            previous_end_date = end_date

    return False  # No suspicious gaps

def check_institution(resume_data, valid_institutions_file="valid_institutions.csv"):
    """
    Check if the educational institutions in the resume are valid.
    
    :param resume_data: Resume data containing education information.
    :param valid_institutions_file: Path to a CSV file containing valid institutions.
    :return: Boolean indicating if invalid institutions were detected.
    """
    # Load the list of valid institutions
    valid_institutions = pd.read_csv(valid_institutions_file)["institution_name"].tolist()

    # Check each institution in the resume
    education = resume_data.get("education", [])
    for edu in education:
        institution = edu
        if institution and institution not in valid_institutions:
            return True  # Invalid institution detected

    return False  # All institutions are valid
