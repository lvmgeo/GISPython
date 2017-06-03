# -*- coding: utf-8 -*-
"""
     Module for e-mail operations
"""
import os

class MailHelper:
    """Class for easing the SMTP operations"""

    def __init__(self, From, recipients, Subject, Text):
        """Class initialization procedure

        Args:
            self: The reserved object 'self'
            From: E-mail adress from which to send
            recipients: Recipient array
            Subject: E-mail subject
            Text: E-mail text
        """
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        self.msg = MIMEMultipart()
        self.msg['Subject'] = Subject
        self.msg['To'] = ", ".join(recipients)
        self.msg.attach(MIMEText(Text, 'plain', 'utf-8'))
        self.From = From
        self.recipients = recipients

    def AttachFile(self, FilePath):
        """Procedure to add attachments

        Args:
            self: The reserved object 'self'
            FilePath: Path to the attachment
        """
        from email.mime.base import MIMEBase
        from email import encoders
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(FilePath, "rb").read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(os.path.basename(FilePath)))
        self.msg.attach(part)

    def SendMessage(self, Mailserver, port=None, user=None, password=None, useTLS=False, useSSL=False):
        """Procedure for sending an e-mail

        Args:
            self: The reserved object 'self'
            Mailserver: Mailserver name
            port: Mailserver port number
            user: Username
            password: Password
            useTLS: Use TLS (Default = False)
            useSSL: Use SSL (Default = False)
        """
        import smtplib
        if useSSL:
            mailer = smtplib.SMTP_SSL()
        else:
            mailer = smtplib.SMTP()
        if port != None:
            mailer.connect(Mailserver, port)
        else:
            mailer.connect(Mailserver)
        if useTLS:
            mailer.starttls()
        if user != None:
            mailer.login(user, password)
        mailer.sendmail(self.From, self.recipients, self.msg.as_string())
        mailer.close()

class GISPythonMailHelper(MailHelper):
    """MailHelper wrapper class, which acquires parameters from the GISPython parameter file"""

    def __init__(self, Pr, recipients, Subject, Text):
        """Class initialization procedure

        Args:
            self: The reserved object 'self'
            Pr: Parameter file with corresponding parameters
            recipients: Recipient array
            Subject: E-mail subject
            Text: E-mail text
        """
        mailer = MailHelper(Pr.MailFromAdress, recipients, Subject, Text)

        # Check if attributes exists
        if hasattr(Pr, 'MailserverPort'):
            port = Pr.MailserverPort
        else:
            port = None

        if hasattr(Pr, 'MailserverUseTLS'):
            useTLS = Pr.MailserverUseTLS
        else:
            useTLS = None

        if hasattr(Pr, 'MailserverUseSSL'):
            useSSL = Pr.MailserverUseSSL
        else:
            useSSL = None

        if hasattr(Pr, 'MailserverUser'):
            user = Pr.MailserverUser
            pwd = Pr.MailserverPWD
        else:
            user = None
            pwd = None

        # Send a message
        mailer.SendMessage(Pr.Mailserver, port, user, pwd, useTLS, useSSL)
