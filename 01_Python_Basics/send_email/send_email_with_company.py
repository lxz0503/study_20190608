#!/usr/bin/env python3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import Header
from ping import check_anvl

class SendMail(object):
    def __init__(self, mail_server, sender, receiver):
        self.mail_server = mail_server
        self.sender = sender
        self.receiver = receiver

    def send_mail(self):
        subject = 'Python email test'
        # 构造邮件对象MIMEMultipart对象
        # 下面的主题，发件人，收件人，日期是显示在邮件页面上的。
        msg = MIMEMultipart('mixed')
        msg['Subject'] = subject
        msg['From'] = 'VxWorks7 Nightly NEVER_REPLY <target@windriver.com>'
        # 收件人为多个收件人,通过join将列表转换为以;为间隔的字符串，或者直接用分号分隔所有收件人
        msg['To'] = ";".join(self.receiver)
        # msg['Date']='2012-3-16'

        # 构造文字内容
        text = check_anvl()
        #text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.baidu.com"
        text_plain = MIMEText(text, 'plain', 'utf-8')
        msg.attach(text_plain)

        # if use company mail box
        smtp = smtplib.SMTP(mail_server)              # connect, no log-in step
        smtp.sendmail(self.sender, self.receiver, msg.as_string())
        smtp.quit()


if __name__ == '__main__':
    # 设置smtplib所需的参数
    mail_server = 'prod-webmail.corp.ad.wrs.com'
    sender = 'target@windriver.com'     # this is not important
    # 收件人为多个收件人,放在列表里
    receiver = ['xiaozhan.Li@windriver.com']
    ts = SendMail(mail_server, sender, receiver)
    ts.send_mail()
