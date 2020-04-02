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
            # Cuts off the newline character at end of string
            self.from_addr = creds.readline().strip()
            user = creds.readline().strip()
            password = creds.readline().strip()
            # Logs into the SMTP Server
            self.smtp_client.login(user, password)
            creds.close()

    """
        Send an email message to the desired "to_addr".
        The subject of the message is passed into "subject"
        The body of the email is passed into "body"
        The type of the content (either 'html' or 'plain') is passed
          through content_type
    """
    def send_message(self, to_addr, subject, body, body_type):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.from_addr
        msg['To'] = to_addr
        if body_type.lower() == 'html':
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))

        self.smtp_client.send_message(msg)

    """
        Destructor for Notifier object, simply
        ends the current SMTP session
    """
    #def __del__(self):
    #    self.smtp_client.quit()
