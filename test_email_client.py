import unittest
from email_client import EmailClient


class EmailClientTestCases(unittest.TestCase):

    # server details
    server = 'smtp.zoho.com.au'
    server_port = 587

    # sender's credentials
    with open('Credentials.txt', 'r') as f:
        mail_id, password = f.read().split(",")

    # mail contents
    # currently setting recipient same as the sender
    recipient = mail_id
    test_subject = 'This is the mail subject!'
    test_body = 'This is the mail body!'
    test_signature = 'This is the mail signature'
    test_attachment = 'test_attachment.txt'

    def test_empty_mails(self):
        """
        This function tests that the mail is sent successfully when all the mail contents are proper
        """
        # initialize the email client
        email_client = EmailClient(self.server, self.server_port, self.mail_id, self.password)

        # set email contents to empty string
        email_client.set_subject('')
        email_client.set_body('')
        email_client.set_signature('')
        email_client.add_attachment('')

        # verify that the email is not sent
        self.assertFalse(email_client.send(self.recipient))

    def test_valid_mails(self):
        """
        This function tests that the mail is not sent when email contents are empty
        """
        # initialize the email client
        email_client = EmailClient(self.server, self.server_port, self.mail_id, self.password)

        # set email contents to test strings and files
        email_client.set_subject(self.test_subject)
        email_client.set_body(self.test_body)
        email_client.set_signature(self.test_signature)
        email_client.add_attachment(self.test_attachment)

        # verify that the email is sent
        self.assertTrue(email_client.send(self.recipient))

    def test_empty_subject_mails(self):
        """
        This function tests that mail is not sent when attachment is present but no subject is added
        """
        # initialize the email client
        email_client = EmailClient(self.server, self.server_port, self.mail_id, self.password)

        # set subject of email to empty string
        email_client.set_subject('')

        # set email contents to test strings and files
        email_client.set_body(self.test_body)
        email_client.set_signature(self.test_signature)
        email_client.add_attachment(self.test_attachment)

        # verify that the email is sent
        self.assertFalse(email_client.send(self.recipient))

    def test_invalid_attachment_path_mails(self):
        """
        This functions tests that mail is not sent when attachment path is invalid
        """
        # initialize the email client
        email_client = EmailClient(self.server, self.server_port, self.mail_id, self.password)

        # set email contents to test strings and files
        email_client.set_subject(self.test_subject)
        email_client.set_body(self.test_body)
        email_client.set_signature(self.test_signature)
        email_client.add_attachment('xyz.txt')

        # verify that the email is sent
        self.assertFalse(email_client.send(self.recipient))

    def test_reset_functionality(self):
        """
        This functions tests that mail contents are reset after calling reset()
        """
        # initialize the email client
        email_client = EmailClient(self.server, self.server_port, self.mail_id, self.password)

        # set email contents to test strings and files
        email_client.set_subject(self.test_subject)
        email_client.set_body(self.test_body)
        email_client.set_signature(self.test_signature)
        email_client.add_attachment(self.test_attachment)

        # before reset will be true as email will be sent
        before_reset = email_client.send(self.recipient)

        # reset the email contents
        email_client.reset_email()

        # after reset will be false as email won't be sent as the contents removed
        after_reset = email_client.send(self.recipient)

        # compare that both are not equal
        self.assertNotEqual(before_reset, after_reset)


if __name__ == '__main__':
    unittest.main()
