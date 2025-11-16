import subprocess
import os

def generate_key_cert_pem() -> None:

    subprocess.run(["openssl", "req", "-x509",
                        "-newkey", "rsa:4096",
                        "-keyout", "key.pem", "-out", "cert.pem",
                        "-days", "365", "-nodes",
                        "-config", "openssl.conf"],
                        cwd=os.getcwd(),
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.STDOUT)

def generate_env(port: int = 443) -> None:
    subprocess.run(["echo", "HOST='0.0.0.0'", ">", ".env"], shell=True)
    subprocess.run(["echo", f"PORT={port}", ">>", ".env"], shell=True)

# Function requires command ipv4_qr to be set as environment variable.
# See https://github.com/Michael-Brukson/Tools for installation.
# Only works on windows (for now)
def generate_qr(port: int) -> None :

    subprocess.run(["cmd", "/c", "ipv4_qr", "-s", "-p", f"{port}"])