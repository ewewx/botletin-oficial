# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Content


def send_mail(mailContent, mailSubject, mailRecipients):
    message = Mail(
        from_email='innovacion@chequeado.com',
        to_emails=mailRecipients,
        subject=mailSubject,
        html_content=mailContent)
    try:
        print(os.environ.get('SENDGRID_API_KEY'))
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)

    except Exception as e:
        print(e)
