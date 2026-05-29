from flask import Flask
from flask_socketio import SocketIO
import util
from pathlib import Path
import logging
from datetime import datetime
# from dotenv import load_dotenv

socketio: SocketIO = SocketIO()

def init_folders() -> None:
    logger: logging.Logger = logging.getLogger(__name__)

    key_path: Path = Path("key.pem")
    cert_path: Path = Path("cert.pem")
    env_path: Path = Path(".env")
    logs_path: Path = Path("logs")

    while True:
        try: 
            logging.basicConfig(filename = f"logs/{datetime.now().strftime('%dd-%mm-%yy_%Hh_%Mm_%Ss')}.log", level=logging.INFO)
        except FileNotFoundError:
            logs_path.mkdir()
            continue
        break
    if not key_path.exists() or not cert_path.exists():
        logger.info("no self certification found, generating now...")
        util.generate_key_cert_pem()
    if not env_path.exists():
        logger.info("no .env file found, generating now...")
        util.generate_env()


def create_app() -> Flask:
    app = Flask(__name__)

    logger: logging.Logger = logging.getLogger('werkzeug')
    logger.setLevel(logging.INFO)
    
    socketio.init_app(app) 

    return app