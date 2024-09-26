import smtplib
import os
import logging
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

handler = logging.StreamHandler(sys.stdout)
handler.flush = sys.stdout.flush  # Ensure flush method is called on each log entry
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger(__name__)

def send_email(to_email, subject, body, attachments=None):
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = os.getenv('SMTP_PORT', 587)
    smtp_user = "XXX"
    smtp_password = "XXX"
    
    server = smtplib.SMTP(smtp_server, int(smtp_port))
    server.starttls()  # Use TLS encryption
    server.login(smtp_user, smtp_password)

    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    if attachments:
        for file_path in attachments:
            with open(file_path, 'rb') as attachment:
                mime_base = MIMEBase('application', 'octet-stream')
                mime_base.set_payload(attachment.read())
                encoders.encode_base64(mime_base)

                filename = os.path.basename(file_path)
                mime_base.add_header(
                    'Content-Disposition',
                    f'attachment; filename={filename}'
                )
                msg.attach(mime_base)

    server.sendmail(smtp_user, to_email, msg.as_string())
    server.quit()

    print(f"Email with attachments sent to {to_email} successfully.")

to = os.getenv("to")
ndvi_label = os.getenv("ndvi")

ndvi_plot = '/cfs' + str(ndvi_label) + '/ndvi_time_series.png'
ndvi_csv = '/cfs' + str(ndvi_label) + '/ndvi_time_series.csv'

send_email(
    to_email=str(to),
    subject="ColonyOS NDVI Processing Completed",
    body="Your NDVI time series analysis is completed. Please find the attached time series plot and CSV file.",
    attachments=[ndvi_plot, ndvi_csv]
)
