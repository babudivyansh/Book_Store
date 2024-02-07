import ssl
from email.message import EmailMessage
import smtplib
from Core import Settings
from celery import Celery

app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',  # Example Redis broker URL
    backend='redis://localhost:6379/0'  # Example Redis backend URL
)


app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

em = EmailMessage()


@app.task()
def send_verification_email(token: str, email):
    """
    Description: This function send mail to verify user.
    Parameter: verification_token as string, email of user where send the mailto verify.
    Return: None
    """
    email_sender = Settings.email_sender
    email_password = Settings.email_password

    subject = 'Email Verification'
    body = f"Click the link to verify your email: http://127.0.0.1:8000/verify?token={token}"

    em['From'] = email_sender
    em['To'] = email
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email, em.as_string())
        smtp.quit()
