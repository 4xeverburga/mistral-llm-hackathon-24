from fastapi import FastAPI
import threading
import asyncio
import logging
import gmail
import mistral
import time
from datetime import datetime

logging.basicConfig(level=logging.INFO)
app = FastAPI()

def save_email_to_txt(email_data):
    """
    Guarda la información del correo en un archivo .txt
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"correo_{timestamp}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"De: {email_data['from']}\n")
        f.write(f"Asunto: {email_data['subject']}\n")
        f.write(f"Cuerpo:\n{email_data['body']}\n")
    logging.info(f"Correo guardado en {filename}")

def check_and_process_emails():
    """
    Revisa correos no leídos cada 5 segundos, guarda cada correo en un .txt y responde.
    """
    mail = gmail.connect_to_email()
    if mail:
        while True:
            logging.info("Revisando correos no leídos...")
            emails = gmail.get_unread_emails(mail)
            for email_data in emails:
                # Guardar correo en archivo .txt
                save_email_to_txt(email_data)
                
                # Obtener respuesta de la IA
                logging.info(f"Generando respuesta para el correo de {email_data['from']}...")
                ai_response = mistral.get_completion(email_data["body"], email_data["from"])
                logging.info(f"Respuesta generada: {ai_response}")
                
                # Enviar respuesta
                gmail.send_email(email_data["from"], "Respuesta de IA", ai_response)
            
            # Esperar 5 segundos antes de revisar de nuevo
            time.sleep(5)
        mail.logout()
    else:
        logging.error("No se pudo conectar a la cuenta de correo.")

@app.get("/")
async def root():
    return {"status": "active"}

async def run_fastapi():
    import uvicorn
    config = uvicorn.Config(app, host="0.0.0.0", port=3000, log_level="error")
    server = uvicorn.Server(config)
    await server.serve()

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Iniciar servidor FastAPI en un hilo
    fastapi_thread = threading.Thread(
        target=lambda: loop.run_until_complete(run_fastapi()),
        daemon=True
    )
    fastapi_thread.start()
    logging.info("Servidor FastAPI iniciado.")
    
    # Iniciar revisión de correos en un hilo
    email_thread = threading.Thread(target=check_and_process_emails, daemon=True)
    email_thread.start()
    
    while True:
        pass  # Mantener el servidor activo

if __name__ == "__main__":
    main()
