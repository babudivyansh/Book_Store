import ssl
from email.message import EmailMessage
import smtplib
from Core import Settings


def send_verification_email(verification_token: str, email):
    """
    Description: This function send mail to verify user.
    Parameter: verification_token as string, email of user where send the mailto verify.
    Return: None
    """
    email_sender = Settings.email_sender
    email_password = Settings.email_password

    subject = 'Email Verification'
    body = f"Click the link to verify your email: http://127.0.0.1:8000/verify?token={verification_token}"

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email, em.as_string())
        smtp.quit()

