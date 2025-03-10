# Smart Resume Screening System 🚀
The **Smart Resume Screening System** is an AI-powered tool designed to automate the process of screening resumes and matching them with job descriptions. It uses **Natural Language Processing (NLP)**, **Machine Learning**, and **rule-based techniques** to evaluate resumes based on skills, experience, education, and other criteria. The system also includes **fraud detection**, **sentiment analysis**, and **email notifications** for rejected candidates.
## Installation 🛠️

### Prerequisites
- Python 3.8 or higher.
- Required libraries:
  ```bash
  pip install flask pandas spacy pdfplumber scikit-learn transformers
  python -m spacy download en_core_web_sm



    
## Run Locally

Clone the project

```bash
  git clone <repository-url>
```

Go to the project directory

```bash
  cd smart-resume-screening
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Start the server

```bash
  python app.py
```


## Usage/Examples

1)Job Description Input:

Paste the job description into the input box and submit.

The system will extract job details and skills.

2)Resume Upload:

Upload one or more resumes in PDF format.

The system will parse the resumes, match skills, and perform fraud detection and sentiment analysis.

3)Dashboard:

View statistics and a table of screened resumes.

Filter resumes by suitability and download reports.

4)Email Notifications:

Unsuitable candidates will receive a rejection email with feedback.


## Tech Stack


**Frontend:** HTML, CSS, Bootstrap, JavaScript

**Backend:** Flask (Python)

**NLP:** spaCy, BERT (Transformers)

**Machine Learning:** Scikit-learn

**Database:** None (in-memory storage for demo purposes)

**Other Libraries:** Pandas, pdfplumber
## API Reference

#### Get all resume

```http
  GET /api/resumes
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `api_key` | `string` | **Required**. Your API key |

#### Get resume by ID

```http
  GET /api/resumes/{id}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `id`      | `string` | **Required**. ID of the resume. |

#### Update Skill Weights
```http
  POST /api/update-weights
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `skill`      | `string` | **Required**. Name of the skill. |
| `weight`      | `int` | **Required**. Weight of the skill.|

#### Download Report
```http
  GET /api/download-report
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `api_key`      | `string` | **Required**. Your API key |


#### Analyze Sentiment
```http
  GET /api/analyze-sentiment
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `api_key`      | `string` | **Required**. Your API key |

#### Clear Resumes
```http
  DELETE /api/clear-resumes
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `api_key`      | `string` | **Required**. Your API key |

## Environment Variables

To run this project, update the config.py file with your email credentials and SMTP server details:
```
class Config:
    EMAIL_ADDRESS = "your-email@example.com"
    EMAIL_PASSWORD = "your-email-password"
    SMTP_SERVER = "smtp.example.com"
    SMTP_PORT = 587
    SECRET_KEY = "your-secret-key"
    UPLOAD_FOLDER = "uploads"

```
## Authors

- [@Shreyansh](https://www.github.com/Sheryansh0)
- [@Chandramouli](https://www.github.com/ChandramouliGude)
- [@Nani](https://www.github.com/NaniBabuNalli)
- [@Srinivas](https://www.github.com/SrinivasLakavath)




## Acknowledgements

spaCy for NLP capabilities.

Hugging Face for the BERT model.

Bootstrap for frontend styling.


## Feedback

If you have any feedback, please reach out to us at bachchushreyansh@gmail.com


## FAQ

#### Question 1: How do I update skill weights?
A: Use the /update-weights route to update skill weights dynamically.

#### Question 2: Can I use this for non-PDF resumes?
A: Currently, the system only supports PDF resumes.

