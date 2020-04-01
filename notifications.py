import smtplib
from flask import render_template

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.message import EmailMessage


# UTCS mail server
MAIL_SERVER = "mail2.cs.utexas.edu"
SMTP_PORT = 587

"""
    Credentials File Format:
    1st line: Outbound email address
    2nd line: Server username
    3rd line: Server user password
"""

class Notifier:
    """
        Creates a new Notifier object.
        Requires a credentials file for logging into the
        SMTP server. (See comment above for format)
    """
    def __init__(self, credentials_file):
        self.smtp_client = smtplib.SMTP(MAIL_SERVER, SMTP_PORT)
        self.smtp_client.starttls()
        with open(credentials_file) as creds:
            self.from_addr = creds.readline()[:-1]
            user = creds.readline()[:-1]
            password = creds.readline()[:-1]
            self.smtp_client.login(user, password)

    """
        Send an email message to the desired "to_addr".
        The body of the email is passed into "content"
        The type of the content (either 'html' or 'plain') is passed
          through content_type
    """
    def send_message(self, to_addr, content, content_type):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Notification from lab hours queue"
        msg['From'] = self.from_addr
        msg['To'] = to_addr
        if content_type.lower() == 'html':
            msg.attach(MIMEText(content, 'html'))
        else:
            msg.attach(MIMEText(content, 'plain'))

        self.smtp_client.send_message(msg)

    """
        Destructor for Notifier object, simply
        ends the current SMTP session
    """
    def __del__(self):
        self.smtp_client.quit()
