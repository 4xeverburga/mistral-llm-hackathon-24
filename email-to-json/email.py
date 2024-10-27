import imaplib
import email
from email.header import decode_header
import json
import time
from datetime import datetime

# Configuración de la cuenta de correo
IMAP_SERVER = 'imap.gmail.com'
EMAIL_ACCOUNT = 'gptgrupoo@gmail.com'  
PASSWORD = 'iuhczjizbcbnttvk'  

def connect_to_email():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, PASSWORD)
        return mail
    except Exception as e:
        print(f"Error al conectar al correo: {e}")
        return None

def get_unread_emails(mail):
    try:
        mail.select("inbox")
        # Buscar solo correos no leídos
        status, messages = mail.search(None, 'UNSEEN')
        email_ids = messages[0].split()

        for email_id in email_ids:
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")

                    from_ = msg.get("From")

                    # Obtener el contenido del correo de manera segura
                    body = None
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))

                            # Intentar obtener el cuerpo solo si es de tipo texto
                            if "attachment" not in content_disposition and content_type == "text/plain":
                                try:
                                    body = part.get_payload(decode=True).decode()
                                except:
                                    pass
                    else:
                        try:
                            body = msg.get_payload(decode=True).decode()
                        except:
                            pass

                    # Crear un diccionario con los datos del correo
                    email_data = {
                        "from": from_,
                        "subject": subject,
                        "body": body if body else "No se pudo obtener el cuerpo del mensaje o el mensaje está vacío."
                    }

                    # Convertir el diccionario a formato JSON
                    email_json = json.dumps(email_data, ensure_ascii=False, indent=4)
                    
                    # Generar un nombre de archivo único basado en la fecha y hora actual
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"email_{timestamp}.json"
                    
                    # Guardar el JSON en un archivo
                    with open(filename, 'w', encoding='utf-8') as json_file:
                        json_file.write(email_json)
                    
                    print(f"Correo guardado en: {filename}")

                    # Marcar el correo como leído
                    mail.store(email_id, '+FLAGS', '\\Seen')
                    print(f"Correo {email_id.decode()} marcado como leído.")

    except Exception as e:
        print(f"Error al obtener el correo: {e}")

if __name__ == "__main__":
    mail = connect_to_email()
    if mail:
        while True:
            print("Revisando correos no leídos...")
            get_unread_emails(mail)
            time.sleep(5)  # Espera 5 segundos antes de revisar de nuevo