import subprocess
import os

def generate_key_cert_pem():

    subprocess.run(["openssl", "req", "-x509",
                        "-newkey", "rsa:4096",
                        "-keyout", "key.pem", "-out", "cert.pem",
                        "-days", "365", "-nodes",
                        "-config", "openssl.conf"],
                        cwd=os.getcwd(),
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.STDOUT)