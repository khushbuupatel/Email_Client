import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.utils import formatdate
from email import encoders
from pathlib import Path


class EmailClient:

    def __init__(self, server_dns: str, server_port: int, email_id: str, mail_password: str):
        """
        This method initializes the smtp server for sending email

        :param server_dns: smpt server for Gmail, yahoo, etc that is to be used
        :param server_port: port of the mail server used above
        :param email_id: mail id of the sender
        :param mail_password: password of the sender
        """
        # initialize the server details
        self.mail_id = email_id
        self.password = mail_password
        self.server = server_dns
        self.server_port = server_port
        self.mail_content = MIMEMultipart()
        self.mail_server = smtplib.SMTP()

        # variables to verify if the mail contents are added properly
        self.subject_added = False
        self.body_added = False
        self.attachment_added = False
        self.signature_added = False

    def set_subject(self, mail_subject: str):
        """
        This method sets the subject of the mail content

        :param mail_subject: subject to be added
        """
        if mail_subject != '':
            self.subject_added = True
            self.mail_content['Subject'] = mail_subject

    def set_body(self, mail_body: str):
        """
        This method add the body to the mail content

        :param mail_body: text of the body to be added
        """
        if mail_body != '':
            self.body_added = True
            self.mail_content.attach(MIMEText(mail_body, 'plain'))

    def set_signature(self, signature: str):
        """
        This method adds the signature to the mail content

        :param signature: text to be added as signature
        """
        # add signature if passed
        if signature != '':
            self.signature_added = True
            self.mail_content.attach(MIMEText(signature, 'plain'))

    def add_attachment(self, mail_attachment_path: str):
        """
        This method add attachment to the email content

        :param mail_attachment_path: path of the file to be attached
        """
        # check if attachment path is a file
        if os.path.isfile(mail_attachment_path):
            attachment = MIMEBase('application', "octet-stream")

            # read the attachment file as binary
            with open(mail_attachment_path, 'rb') as f_obj:
                attachment.set_payload(f_obj.read())
            encoders.encode_base64(attachment)

            attachment.add_header('Content-Disposition',
                                  'attachment; filename="{}"'.format(Path(mail_attachment_path).name))

            # attach the attachment with the mail content
            self.mail_content.attach(attachment)
            self.attachment_added = True

    def send(self, mail_recipient: str) -> bool:
        """
        This method sends the email and returns True if sent successfully and false otherwise.

        :param mail_recipient: Email of the recipient
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

        # set mail_sent variable to false initially
        mail_sent = False

        # set the to and from part of the mail with today's date
        self.mail_content['To'] = mail_recipient
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
            mail_sent = True

        except OSError as e:
            print(
                "Mail was not sent. Some issue occurred. Please check you mail id and password again. \n", e)

        finally:
            # del the mail_content object and close the server
            self.mail_server.quit()
            del self.mail_content

        return mail_sent

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
    os.system('cat /proc/cpuinfo > cpu_info.txt')
    os.system('cat /proc/meminfo > mem_info.txt')
    os.system('ps -aux > running_process.txt')

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
