# modules/skill_matcher.py
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_weighted_match_score(resume_skills, job_skills, skill_weights):
    """Calculate weighted similarity score using Cosine Similarity."""
    if not resume_skills or not job_skills:
        return 0.0

    # Create weighted vectors
    resume_vector = []
    job_vector = []

    for skill in job_skills:
        weight = skill_weights.get(skill, 1)  # Default weight is 1 if not specified
        resume_vector.append(weight if skill in resume_skills else 0)
        job_vector.append(weight)

    # Calculate cosine similarity
    similarity = cosine_similarity([resume_vector], [job_vector])[0][0]
    return round(similarity * 100, 2)