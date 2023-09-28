import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .parser import settings
from . import DBOperator

smtp_client = smtplib.SMTP_SSL('smtp.yandex.com', 465)
smtp_client.login(settings['host'], settings['port'])


def send_code_for_email_confirmation(user_email, id, code):
    message = MIMEMultipart()
    message['To'] = user_email
    message['From'] = 'i@savnil.ru'
    message['Subject'] = 'Please, confirm your email in GigaChat'

    message.attach(MIMEText(settings['url'].format(id=id, token=code)))

    smtp_client.sendmail(settings['sender'], user_email, message.as_string())


def save_token(id, token):
    DBOperator.save_token(id, token)
