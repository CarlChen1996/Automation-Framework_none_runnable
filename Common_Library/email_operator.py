import smtplib
import ntpath
from Framework_Kernel.analyzer import FrameworkSettings
from Framework_Kernel.log import controller_log
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Email:
    def __init__(self):
        self.settings = self.__load_settings()
        self.smtp_server = self.settings['smtp_server']
        self.smtp_port = self.settings['smtp_port']
        self.smtp = self.__init_connection()
        self.sender = self.settings['default_sender']
        self.default_receiver = self.settings['default_receiver']

    def __load_settings(self):
        email_settings = FrameworkSettings().email_settings
        return email_settings

    def __init_connection(self):
        try:
            smtp = smtplib.SMTP()
            smtp.connect(self.smtp_server, self.smtp_port)
            controller_log.info('SMTP server connected successfully')
            return smtp
        except smtplib.SMTPException as e:
            controller_log.info("Error: %s" % e)
            return False

    def send_email(self, subject, to_list, content, content_type, cc_list=None, attachment=None):
        msg = MIMEMultipart('mixed')
        email_content = MIMEText(content, content_type, 'utf-8')
        msg.attach(email_content)
        msg['Subject'] = subject
        msg['From'] = self.sender
        msg['To'] = ','.join(to_list)
        if cc_list is not None:
            msg['cc'] = ','.join(cc_list)
        if attachment is not None:
            msg.attach(self.__get_attachment(attachment))
        try:
            self.smtp.sendmail(self.sender, to_list, msg.as_string())
            controller_log.info('send email: "{}" successfully'.format(subject))
        except smtplib.SMTPException as e:
            controller_log.info("Error: %s" % e)

    def __get_attachment(self, attached_file):
        try:
            with open(attached_file, 'rb') as f:
                send_file = f.read()
            text_attachment = MIMEText(send_file, 'base64', 'utf-8')
            text_attachment['Content-Type'] = 'application/octet-stream'
            att_name = ntpath.basename(attached_file)
            text_attachment['Content-Disposition'] = 'attachment; filename={}'.format(att_name)
            return text_attachment
        except Exception as e:
            print(e)

    def disconnect(self):
        return self.smtp.quit()
