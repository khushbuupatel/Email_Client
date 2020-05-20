import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.utils import formatdate
from email import encoders
from pathlib import Path


class EmailClient:

    def __init__(self, server: str, server_port: int, mail_id: str, password: str):
        """
        This method initializes the smtp server for sending email

        :param server: smpt server for Gmail, yahoo, etc that is to be used
        :param server_port: port of the mail server used above
        :param mail_id: mail id of the sender
        :param password: password of the sender
        """
        # initialize the server details
        self.mail_id = mail_id
        self.password = password
        self.server = server
        self.server_port = server_port
        self.mail_content = MIMEMultipart()

        # variables to verify if the mail contents are added properly
        self.subject_added = False
        self.body_added = False
        self.attachment_added = False
        self.signature_added = False

    def set_subject(self, subject: str):
        """
        This method sets the subject of the mail content

        :param subject: subject to be added
        """
        if subject != '':
            self.subject_added = True
            self.mail_content['Subject'] = subject

    def set_body(self, body: str):
        """
        This method add the body to the mail content

        :param body: text of the body to be added
        """
        if body != '':
            self.body_added = True
            self.mail_content.attach(MIMEText(body, 'plain'))

    def set_signature(self, signature: str):
        """
        This method adds the signature to the mail content

        :param signature: text to be added as signature
        """
        # add signature if passed
        if signature != '':
            self.signature_added = True
            self.mail_content.attach(MIMEText(signature, 'plain'))

    def add_attachment(self, attachment_path: str):
        """
        This method add attachment to the email content

        :param attachment_path: path of the file to be attached
        """
        # check if attachment path is a file
        if os.path.isfile(attachment_path):
            attachment = MIMEBase('application', "octet-stream")

            # read the attachment file as binary
            with open(attachment_path, 'rb') as file:
                attachment.set_payload(file.read())
            encoders.encode_base64(attachment)

            attachment.add_header('Content-Disposition',
                                  'attachment; filename="{}"'.format(Path(attachment_path).name))

            # attach the attachment with the mail content
            self.mail_content.attach(attachment)
            self.attachment_added = True

    def send(self, recipient: str) -> bool:
        """
        This method sends the email and returns True if sent successfully and false otherwise.

        :param recipient: Email of the recipient
        :return: True if sent successfully, false other
        """

        # email cannot not be sent if there is an attachment and no subject
        if self.attachment_added and not self.subject_added:
            print('Subject of mail cannot be empty!')
            return False

        # email cannot be sent if attachment path is invalid
        if not self.attachment_added:
            print('Attachment file path is not valid!')
            return False

        # empty email cannot be sent
        if not self.subject_added and not self.body_added and not self.signature_added:
            print('Cannot send empty emails!')
            return False

        # set mailSent variable to false initially
        mailSent = False

        # set the to and from part of the mail with today's date
        self.mail_content['To'] = recipient
        self.mail_content['From'] = self.mail_id
        self.mail_content['Date'] = formatdate(localtime=True)

        try:
            # establish a smtp server
            self.mail_server = smtplib.SMTP(host=self.server, port=self.server_port)

            # connect to the smtp server
            self.mail_server.starttls()

            # login to the smtp sever with the user credentials
            self.mail_server.login(self.mail_id, self.password)

            # send email
            self.mail_server.send_message(self.mail_content)
            mailSent = True

        except OSError as e:
            print(
                "Mail was not sent. Some issue occurred. Please check you mail id and password again. \n", e)

        finally:
            # del the mail_content object and close the server
            self.mail_server.quit()
            del self.mail_content

        return mailSent

    def reset_email(self):
        """
        This method resets the content of email
        """
        # reset the email content except the initialization part
        self.mail_content = MIMEMultipart()
        self.mail_content['From'] = self.mail_id

        # reset boolean variables to false
        self.subject_added = False
        self.body_added = False
        self.signature_added = False
        self.attachment_added = False


if __name__ == "__main__":

    # credentials of the sender
    mail_id, password = '', ''

    with open('Credentials.txt', 'r') as f:
        mail_id, password = f.read().split(",")

    # server details
    server = 'smtp.zoho.com.au'
    port_number = 587

    # mail contents
    subject = 'Server Performance'
    attachment_path = 'running_process.txt'

    # currently setting recipient same as the sender
    recipient = mail_id

    # add Cpu and Memory usage info to respective files
    os.system('cat /proc/cpuinfo >> cpu_info.txt')
    os.system('cat /proc/meminfo >> mem_info.txt')
    os.system('ps -aux >> running_process.txt')

    body = '*************** CPU INFO ***************\n'
    # add cpu info to body
    with open('cpu_info.txt') as file:
        for line in file.readlines():
            body += line

    body += '*************** MEMORY USAGE INFO ***************\n'
    # add memory info to body
    with open('mem_info.txt') as file:
        for line in file.readlines():
            body += line

    # connect to the server and set the email details
    email_client = EmailClient(server, port_number, mail_id, password)
    email_client.set_subject(subject)
    email_client.set_body(body)
    email_client.set_signature('\nRegards,\nKhushbu Patel.')
    email_client.add_attachment(attachment_path)

    # send email to recipient
    if email_client.send(recipient):
        print('Email was sent successfully to ', recipient)

