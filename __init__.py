from flask import Flask
from flask_socketio import SocketIO
import util
import os
import logging
# from dotenv import load_dotenv

socketio = SocketIO()

def create_app():
    if not os.path.exists("key.pem") or not os.path.exists("cert.pem"):
        print("no self certification found, generating now...")
        util.generate_key_cert_pem()
    if not os.path.exists(".env"):
        print("no .env file found, generating now...")
        util.generate_env()
  
    app = Flask(__name__)
    
    socketio.init_app(app) 

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    return app