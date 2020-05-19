from flask import render_template
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.message import EmailMessage

"""
    Mail server settings to use for sending
    notification emails. Currently using
    a Gmail account.
"""
#MAIL_SERVER = "smtp.gmail.com"
#SMTP_PORT = 587

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
    def __init__(self, address, password, email_server, email_port):
        # Cuts off the newline character at end of string
        self.from_addr = address
        self.user = address
        self.password = password
        self.server = email_server
        self.port = email_port

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

        """
            Actual logging in to the SMTP server happens right before
            we send the email. Originally, this was done only once
            in the constructor, but we seemed to get server disconnection
            errors occasionally, potentially due to timeouts, so instead
            we login before every email is sent.
            If the application is taking too long to process requests, another
            possibility would be to wrap sending an email in a try/except block
            and only try to re-connect if we get an exception.
        """
        smtp_client = smtplib.SMTP(self.server, self.port)
        smtp_client.starttls()
        smtp_client.login(self.user, self.password)
        smtp_client.send_message(msg)
        smtp_client.quit()

    """
        Destructor for Notifier object, simply
        ends the current SMTP session
    """
    #def __del__(self):
    #    self.smtp_client.quit()
