from flask import Flask
from flask_socketio import SocketIO
import util
from pathlib import Path
import logging
from datetime import datetime
# from dotenv import load_dotenv

socketio: SocketIO = SocketIO()

# Function to check if the required files and folders exist, and if not, initalize them.
def init_dependencies() -> None:
    logger: logging.Logger = logging.getLogger(__name__)

    key_path: Path = Path("key.pem")
    cert_path: Path = Path("cert.pem")
    env_path: Path = Path(".env")
    logs_path: Path = Path("logs")

    # error loop to check if 'logs' folder exists for logger. 
    while True:
        try: 
            logging.basicConfig(filename = f"logs/{datetime.now().strftime('%dd-%mm-%yy_%Hh-%Mm-%Ss')}.log", level=logging.INFO)
        except FileNotFoundError:
            logs_path.mkdir()
            continue
        break
    # check if private key and public cert exists for https
    if not key_path.exists() or not cert_path.exists():
        logger.info("no self certification found, generating now...")
        util.generate_key_cert_pem()
    # check if .env exists for knowing the default host and port
    if not env_path.exists():
        logger.info("no .env file found, generating now...")
        util.generate_env()


# Function to create and return flask app.
def create_app() -> Flask:
    app = Flask(__name__)

    logger: logging.Logger = logging.getLogger('werkzeug')
    logger.setLevel(logging.INFO)
    
    socketio.init_app(app) 

    return app