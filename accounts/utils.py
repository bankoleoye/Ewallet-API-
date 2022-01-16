from django.core.mail import EmailMessage
import random
import string


class Util:

    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'],
            body=data['email_body'],
            to=[data['to_email']],
        )
        email.send()

    @staticmethod
    def generate_otp(num):
        return ''.join(random.choice(string.digits) for i in range(num))

    @staticmethod
    def create_account_number(num):
        return '419' + ''.join(random.choice(string.digits) for i in range(num))
