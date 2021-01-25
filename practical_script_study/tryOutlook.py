import sys,os
import getopt
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr, formataddr
import base64

if __name__ == "__main__":
    s_enc = "d3JseC10ZXN0ZXJAd2luZHJpdmVyLmNvbQ=="
    p_enc = "bGUqWTYkc2xHYQ=="
    sender = base64.b64decode(s_enc.encode("utf-8")).decode("utf-8") 
    password = base64.b64decode(p_enc.encode("utf-8")).decode("utf-8")

    subjectText = sys.argv[1]
    receivers = sys.argv[2].split(",")
    #file_h = open(sys.argv[3],'r')
    #mailText = file_h.read()
    #file_h.close()
    mailText = sys.argv[3]
    message = MIMEText(mailText, 'html', 'utf-8')
    me = sender + "<" + sender + ">"
    message['From'] = sender
    message['To'] = ";".join(receivers)
    print(message['To'])
    message['Subject'] = Header(subjectText, 'utf-8')
    try:
        smtpObj = smtplib.SMTP('smtp.office365.com', port=587)
        smtpObj.connect('smtp.office365.com', port=587)
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.ehlo()
        smtpObj.login(sender, password)
        smtpObj.sendmail(sender, receivers, message.as_string())
        smtpObj.quit()
        print("email send successful")
    except smtplib.SMTPException:
        print("Error: email send failed")
