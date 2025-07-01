This web app is meant to allow mobile devices to connect to a computer on the local network, and be used as webcams. It uses Flask and SocketIO along with html and javascript to do so. It is still in development.

This web app needs to be running on https to have access to the users camera. For this, a key.pem and cert.pem must be made, and used for self-certification. Below is the command used to create these two files. Execute it while CD'd into the repository.

```sh
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```
