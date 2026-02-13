import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from decouple import config
import os

def send_email(subject, body, recipients):
    msg = MIMEMultipart()
    
    msg['Subject'] = subject
    msg['From'] = config("EMAIL_SENDER")
    msg['To'] = recipients

    text = MIMEText(body, 'html')
    msg.attach(text)
    
    with open(os.path.join(os.getcwd(), 'assets/images/logo-a.png'), 'rb') as f:
        img_data = f.read()
    image = MIMEImage(img_data,_subtype="png")
    image.add_header('Content-ID', 'image-logo')
    msg.attach(image)

    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.login(config("EMAIL_SENDER"), config("EMAIL_PASSWORD"))
    smtp_server.sendmail(config("EMAIL_SENDER"), recipients, msg.as_string())
    smtp_server.quit()

# subject = "Email Subject test"
# body = "This is the body of the text message"
# recipients = ["yuda.permana@ptbsp.com"]

# send_email(subject, body, recipients)