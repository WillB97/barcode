# A Proof-of-Concept Web-Based Barcode Scanner

Uses a combination of SocketIO and a [HTML5 QR code library](https://github.com/mebjas/html5-qrcode) to allow mobile devices to act as barcode scanners that send their scanned values to receiving client.

**Note: Due to security policies in modern browsers, to use the camera on anything other than localhost requires HTTPS.**
If you choose to use self-signed certificates the console will print an ssl.SSLError stack-trace on every connection but will continue to work.

## Installation

Requires Python 3.8/3.9.

```bash
pip install -r requirements.txt
```

To generate a self-signed cert use:
```bash
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```
and select default options.

## Deployment

This server uses eventlet for its async workers.
Look at [Flask-SocketIO](https://flask-socketio.readthedocs.io/en/latest/deployment.html#gunicorn-web-server) for the command needed to run this using Gunicorn.
Note, even though this only uses one worker it can support several clients.

When putting this behind nginx the required options can be found on the [Flask-SocketIO docs](https://flask-socketio.readthedocs.io/en/latest/deployment.html#using-nginx-as-a-websocket-reverse-proxy).

```shell
apt update && apt upgrade
apt install python3-pip
cd /srv/
git clone https://github.com/WillB97/barcode.git
cd barcode/
pip install -U pip wheel
pip install -r requirements.txt
pip install -r requirements-prod.txt
cp barcode.service /etc/systemd/system/barcode.service
systemctl daemon-reload
systemctl enable --now barcode.service
```
