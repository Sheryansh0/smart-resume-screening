# modules/email_sender.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

def send_rejection_email(candidate_email, candidate_name, skills_lacking, match_score):
    """
    Send a rejection email to the candidate with personalized feedback.
    """
    subject = "Application Status Update"
    body = f"""
    Dear {candidate_name},

    Thank you for applying for the position. After careful consideration, we regret to inform you that your application has not been successful.

    Here are some details regarding your application:
    - Match Score: {match_score}%
    - Skills Lacking: {', '.join(skills_lacking) if skills_lacking else 'N/A'}

    Suggestions for Improvement:
    - Consider gaining experience in the following areas: {', '.join(skills_lacking) if skills_lacking else 'N/A'}
    - Enhance your skills in the mentioned areas through online courses or certifications.

    We encourage you to apply for future openings that match your skills and experience.

    Best regards,
    Hiring Team
    """

    msg = MIMEMultipart()
    msg['From'] = Config.EMAIL_ADDRESS
    msg['To'] = candidate_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT)
        server.starttls()  # Upgrade the connection to secure
        server.login(Config.EMAIL_ADDRESS, Config.EMAIL_PASSWORD)  # Log in to the email account

        # Send the email
        server.sendmail(Config.EMAIL_ADDRESS, candidate_email, msg.as_string())
        server.quit()  # Close the connection
        print(f"Rejection email sent to {candidate_email}")
        return True
    except Exception as e:
        # Log the error for debugging
        print(f"Failed to send email to {candidate_email}: {e}")
        return False