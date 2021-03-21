from scrapy import signals
from scrapy.exceptions import NotConfigured
from datetime import date
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import logging
import os

logger = logging.getLogger(__name__)


class Notification_Handler:

    def __init__(self, settings, spider):
        self.settings = settings
        self.not_config = settings.get('NOTIFICATION_CONFIG')
        self.not_email = settings.get('NOTIFICATION_EMAIL')
        self.vars = {
            "TODAY": date.today().strftime("%m-%d-%Y"),
            "FILES": getattr(spider, 'OUTPUT_FILE_PATH', '<NO OUTPUT FILES>'),
        }
        self.mailer = self.login()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.mailer.quit()

    def formulate_email(self):
        msg = MIMEMultipart()
        msg['From'] = self.not_config['mailfrom']
        msg['To'] = self.not_email['to']
        if isinstance(self.not_email.get('cc'), list):
            msg['Cc'] = self.formulate_cc()
        if isinstance(self.not_email.get('bcc'), list):
            msg['Bcc'] = self.formulate_bcc()
        msg['Subject'] = self.formulate_subject()
        body = MIMEText(self.formulate_body(), self.not_email['mimetype'])
        msg.attach(body)
        if self.not_email['attach_output']:
            self.attach_output(msg)
        msg = msg.as_string()
        return msg

    def formulate_body(self):
        body = self.not_email['body']
        if isinstance(body, str):
            return body.format(**self.vars)
        elif isinstance(body, list):
            return ''.join(body).format(**self.vars)
        else:
            raise NotConfigured('Body Field is configured improperly')

    def compile_recipients(self):
        recipients = [
            self.not_email.get('to', []),
            self.not_email.get('cc', []),
            self.not_email.get('bcc', []),
            ]

        compiled_recipients = []
        for recipient in recipients:
            if isinstance(recipient, list):
                compiled_recipients += recipient
            elif isinstance(recipient, str):
                if recipient.strip() != '':
                    compiled_recipients += [recipient]

        return compiled_recipients

    def formulate_cc(self):
        cc = self.not_email['cc']
        if isinstance(cc, str):
            return cc
        elif isinstance(cc, list):
            return ', '.join(cc)
        else:
            raise NotConfigured('CC Field is configured improperly')

    def formulate_bcc(self):
        cc = self.not_email['bcc']
        if isinstance(cc, str):
            return cc
        elif isinstance(cc, list):
            return ', '.join(cc)
        else:
            raise NotConfigured('BCC Field is configured improperly')

    def formulate_subject(self):
        subject = self.not_email['subject']
        if isinstance(subject, str):
            return subject.format(**self.vars)
        elif isinstance(subject, list):
            return ''.join(subject).format(**self.vars)
        else:
            raise NotConfigured('Subject Field is configured improperly')

    def attach_output(self, msg):
        filename = os.path.basename(self.vars['FILES'])
        with open(self.vars['FILES'], 'rb') as f:
            attachment = f.read()
        if self.settings.get('STREAM_TO_EXCEL', True):
            xlsx = MIMEBase('application', 'vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            xlsx.set_payload(attachment)
            encoders.encode_base64(xlsx)
            xlsx.add_header('Content-Disposition', 'attachment', filename=filename)
            msg.attach(xlsx)
        else:
            csv_file = MIMEBase('application', "octet-stream")
            csv_file.set_payload(attachment)
            encoders.encode_base64(csv_file)
            csv_file.add_header('Content-Disposition', 'attachment', filename=filename)
            msg.attach(csv_file)

    def login(self):
        if self.not_config['smtpssl']:
            server = smtplib.SMTP_SSL(host=self.not_config['smtphost'], port=self.not_config['smtpport'])
        else:
            server = smtplib.SMTP(host=self.not_config['smtphost'], port=self.not_config['smtpport'])

        server.ehlo()
        if not self.not_config['smtpssl'] and self.not_config['smtptls']:
            server.starttls()
            server.ehlo()

        server.login(self.not_config['smtpuser'], self.not_config['smtppass'])
        return server

    def sendmail(self, sender: str, to_addresses: list, msg: str):
        self.mailer.sendmail(
            sender,
            to_addresses,
            msg
        )

    def send_with_settings(self):
        self.sendmail(
            self.not_config['mailfrom'],
            self.compile_recipients(),
            self.formulate_email(),
        )


class Notify:

    def __init__(self, settings):
        self.settings = settings
        if not self.settings.get('NOTIFICATION_EMAIL'):
            raise NotConfigured('NOTIFICATION_EMAIL is not configured properly')
        if not self.settings.get('NOTIFICATION_CONFIG'):
            raise NotConfigured('NOTIFICATION_CONFIG is not configured properly')

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls(crawler.settings)

        # connect the extension object to signals
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.engine_stopped, signal=signals.engine_stopped)

        # return the extension object
        return ext

    def spider_opened(self, spider):
        self.spider = spider

    def engine_stopped(self):
        logger.info("Sending Notification Email")
        with Notification_Handler(self.settings, self.spider) as nh:
            nh.send_with_settings()
        logger.info("Notification Email Sent")