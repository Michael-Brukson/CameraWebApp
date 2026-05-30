import subprocess
import qrcode
import logging
import functools
import socket
from pathlib import Path

logger: logging.Logger = logging.getLogger()

# TODO: This does not work as intented. For some reason, the files do not get created.
def generate_key_cert_pem() -> None:
    base_dir: Path = Path(__file__).resolve().parent

    cmd: list[str] = ["openssl", "req", "-x509", "-newkey", "rsa:4096",
        "-keyout", "key.pem", "-out", "cert.pem", "-nodes",
        "-days", "365", "-config", "openssl.conf"]  
    print(*cmd) 
    try:
        subprocess.run(cmd,
                        cwd=base_dir,
                        shell=True,
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.STDOUT)
    except Exception as e:
        logger.error(f"errored out during key/cert creation because: \n {type(e).__name__} -> {e}")
        print(f"Encountered error during initialization. logs written at {logger.handlers[0].baseFilename}")
        exit(-1)

    if not Path("key.pem").exists() or not Path("cert.pem").exists():
        logger.error("failed to create private key and/or certificate.")
        exit(-1)
        
# TODO: when there are multiple ip addresses (ethernet + wireless connection), choose the last one
def generate_env(port: int = 443) -> None:
    # hostname: str = socket.gethostname()
    # host: str = socket.gethostbyname(hostname)

    subprocess.run(["echo", f"HOST=0.0.0.0", ">", ".env"], shell=True)
    subprocess.run(["echo", f"PORT={port}", ">>", ".env"], shell=True)

def generate_qr(host: str, port: str) -> None :
    url: str = f"https://{host}/{port}"
    logger.info(f"making qr code for: {url}")
    qr = qrcode.make(url)
    qr.show(title = url)

def log_func(func):
    logger.info(f"Log for {func.__name__}")
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        return func(*args, **kwargs)
    
    return wrap
    # try: return inner
    # finally: logger.info(f"End of log for {func.__name__}")