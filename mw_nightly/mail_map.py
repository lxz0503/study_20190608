import os
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

maiSubject = os.environ['MAIL_SUBJECT']
mailTo = os.environ['MAIL_TO']
mail_txt = os.environ['MAIL_TXT']
def main(argv):
    strFrom = 'VxWorks7 Nightly NEVER_REPLY <target@windriver.com>'
    strTo = mailTo.split(',')
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = maiSubject
    msgRoot['From'] = strFrom
    msgRoot['To'] = mailTo
    msgRoot.preamble = 'This is a multi-part message in MIME format.'

    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)

    msgText = MIMEText('This is the alternative plain text message.')
    msgAlternative.attach(msgText)

    text = open(mail_txt).read( )
    msgText = MIMEText(text, 'html')
    msgAlternative.attach(msgText)

    fp = open(os.path.join(os.path.dirname(mail_txt),'Trend.png'), 'rb')
    msgImage = MIMEImage(fp.read())
    fp.close()

    msgImage.add_header('Content-ID', '<chartImage>')
    msgRoot.attach(msgImage)

    smtp = smtplib.SMTP()
    smtp.connect('smtp-na.wrs.com')
    smtp.sendmail(strFrom, strTo, msgRoot.as_string())
    smtp.close()

if __name__ == "__main__":
    main(sys.argv[0:1])
