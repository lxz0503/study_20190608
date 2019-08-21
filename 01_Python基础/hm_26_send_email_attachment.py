# 发送带文字内容，图片附件，文本附件，html附件格式的邮件
# 下面的例子是一个全面的例子，根据需要可以裁减
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import Header

# 设置smtplib所需的参数
# 下面的发件人，收件人是用于邮件传输的。
smtpserver = 'smtp.163.com'
username = 'lxz_20081025@163.com'
password = 'lxzmm201143'
sender = 'lxz_20081025@163.com'
# receiver='XXX@126.com'
# 收件人为多个收件人,放在列表里
receiver = ['lxz_20081025@163.com', '281237214@qq.com']

subject = 'Python email test'
# 通过Header对象编码的文本，包含utf-8编码信息和Base64编码信息。以下中文名测试ok
# subject = '中文标题'
# subject=Header(subject, 'utf-8').encode()

# 构造邮件对象MIMEMultipart对象
# 下面的主题，发件人，收件人，日期是显示在邮件页面上的。
msg = MIMEMultipart('mixed')
msg['Subject'] = subject
msg['From'] = 'lxz_20081025@163.com <lxz_20081025@163.com>'
# 收件人为多个收件人,通过join将列表转换为以;为间隔的字符串，或者直接用分号分隔所有收件人
msg['To'] = ";".join(receiver)
# msg['Date']='2012-3-16'

# 构造文字内容
# text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.baidu.com"
# text_plain = MIMEText(text, 'plain', 'utf-8')
# msg.attach(text_plain)

# 构造文字内容，尝试把html文件里面的内容作文邮件正文,不能和上面那段代码共存
with open(r'send_email\ltaf_email.html', 'r') as f:
    mail_body = f.read()
html_content = MIMEText(mail_body, 'html', 'utf-8')
msg.attach(html_content)

# 构造图片链接
sendimagefile = open(r'send_email\err.jpg', 'rb').read()
image = MIMEImage(sendimagefile)
image.add_header('Content-ID', '<image1>')
image["Content-Disposition"] = 'attachment; filename="testimage.png"'   # 附件名字以这个为准
msg.attach(image)

# 构造html
text_html = MIMEText(r'send_email\test.html', 'html', 'utf-8')
text_html["Content-Disposition"] = 'attachment; filename="test.html"'   # 附件名字以这个为准
msg.attach(text_html)

# 构造文本附件
sendfile = open(r'send_email\test.txt', 'rb').read()
text_att = MIMEText(sendfile, 'base64', 'utf-8')
text_att["Content-Type"] = 'application/octet-stream'
# 以下附件可以重命名成aaa.txt
#text_att["Content-Disposition"] = 'attachment; filename="aaa.txt"'
#另一种实现方式
text_att.add_header('Content-Disposition', 'attachment', filename='test.txt')    # 附件名字以这个为准
msg.attach(text_att)

# 发送邮件
smtp = smtplib.SMTP()
smtp.connect('smtp.163.com')
# 我们用set_debuglevel(1)就可以打印出和SMTP服务器交互的所有信息。
# smtp.set_debuglevel(1)
smtp.login(username, password)
smtp.sendmail(sender, receiver, msg.as_string())
smtp.quit()

# if use company mail box
# mailServer = 'prod-webmail.corp.ad.wrs.com'
# smtp = smtplib.SMTP(mailServer)              # connect, no log-in step
# smtp.sendmail(sender, receiver, msg.as_string())
# smtp.quit()
