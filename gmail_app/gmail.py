import imaplib
import smtplib
import email
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import logging

load_dotenv()

# Configuración del servidor y credenciales
IMAP_SERVER = 'imap.gmail.com'
SMTP_SERVER = 'smtp.gmail.com'
EMAIL_ACCOUNT = os.getenv('EMAIL_ACCOUNT')
PASSWORD = os.getenv('EMAIL_PASSWORD')
MAX_MESSAGE_LENGTH = 1500

logging.basicConfig(level=logging.INFO)

# Conexión a Gmail
def connect_to_email():
    try:
        logging.info("Conectando al servidor de correo...")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, PASSWORD)
        logging.info("Conexión a correo exitosa.")
        return mail
    except Exception as e:
        logging.error(f"Error al conectar al correo: {e}")
        return None

# Leer correos no leídos
def get_unread_emails(mail):
    try:
        logging.info("Seleccionando la bandeja de entrada...")
        mail.select("inbox")
        status, messages = mail.search(None, 'UNSEEN')
        email_ids = messages[0].split()
        emails = []
        logging.info(f"{len(email_ids)} correos no leídos encontrados.")

        for email_id in email_ids:
            logging.info(f"Procesando correo ID: {email_id.decode()}")
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    from_ = msg.get("From")
                    body = extract_email_body(msg)

                    emails.append({"from": from_, "subject": subject, "body": body or "Mensaje vacío"})
                    logging.info(f"Correo de {from_} con asunto '{subject}' procesado.")
                    mail.store(email_id, '+FLAGS', '\\Seen')  # Marcar como leído
                    logging.info(f"Correo ID {email_id.decode()} marcado como leído.")

        return emails
    except Exception as e:
        logging.error(f"Error al obtener el correo: {e}")
        return []

# Extraer el cuerpo del mensaje
def extract_email_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and "attachment" not in part.get("Content-Disposition", ""):
                return part.get_payload(decode=True).decode()
    else:
        return msg.get_payload(decode=True).decode()
    return None

# Enviar correos
def send_email(to_address, subject, body):
    try:
        logging.info(f"Preparando para enviar correo a {to_address}...")
        with smtplib.SMTP_SSL(SMTP_SERVER, 465) as server:
            server.login(EMAIL_ACCOUNT, PASSWORD)
            msg = MIMEMultipart()
            msg['From'] = EMAIL_ACCOUNT
            msg['To'] = to_address
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            server.sendmail(EMAIL_ACCOUNT, to_address, msg.as_string())
        logging.info(f"Correo enviado a {to_address}.")
    except Exception as e:
        logging.error(f"Error enviando el correo: {e}")
