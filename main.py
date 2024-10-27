from fastapi import FastAPI, Request, Response
import uvicorn
import threading
import time
from datetime import datetime
import os
import sys
import asyncio
import logging
from dotenv import load_dotenv
from colorama import init, Fore, Style
import mistral
import twilio_chat

try:
    import multipart
except ImportError:
    print("❌ Error: Falta la librería python-multipart")
    print("Por favor, ejecuta: pip install python-multipart")
    sys.exit(1)

init()
load_dotenv()
PORT = int(os.getenv('PORT', '3000'))


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if 'color' in record.__dict__:
            level_name = f"{record.color}[{record.levelname}]{Style.RESET_ALL}"
        else:
            level_name = f"[{record.levelname}]"

        return f"{timestamp} {level_name} {record.getMessage()}"


# Configurar logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter())
logger.handlers = [handler]

# Desactivar logs innecesarios
logging.getLogger('twilio.http_client').setLevel(logging.WARNING)
logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)

app = FastAPI()


@app.get("/")
async def root():
    return {"status": "active"}


@app.post("/receive_local")
async def receive_message(request: Request):
    try:
        form_data = await request.form()
        message, from_number = await twilio_chat.process_incoming_message(form_data)

        if message and from_number:
            ai_response = mistral.get_completion(message)
            twilio_chat.send_message(from_number, ai_response)

        return Response(
            content="<?xml version='1.0' encoding='UTF-8'?><Response></Response>",
            media_type="application/xml"
        )
    except Exception as e:
        logging.error(f"❌ Error: {str(e)}")
        return Response(
            content="<?xml version='1.0' generation='UTF-8'?><Response></Response>",
            media_type="application/xml"
        )


async def run_fastapi():
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="error",
        access_log=False
    )
    server = uvicorn.Server(config)
    await server.serve()


def log_with_color(message: str, level: str, color: str):
    """Función auxiliar para logging con color"""
    record = logging.LogRecord(
        name="", level=logging.INFO,
        pathname="", lineno=0,
        msg=message, args=(), exc_info=None
    )
    record.levelname = level
    record.color = color
    logger.handle(record)


def main():
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        fastapi_thread = threading.Thread(
            target=lambda: loop.run_until_complete(run_fastapi()),
            daemon=True
        )
        fastapi_thread.start()

        log_with_color(f"✨ Servidor iniciado en puerto {PORT}", "SUCCESSFUL", Fore.GREEN)

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        logging.error(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()