# A Proof-of-Concept Web-Based Barcode Scanner

Uses a combination of SocketIO and a [HTML5 QR code library](https://github.com/mebjas/html5-qrcode) to allow mobile devices to act as barcode scanners that send their scanned values to receiving client.

**Note: Due to security policies in modern browsers, to use the camera on anything other than localhost requires HTTPS.**
If you choose to use self-signed certificates the console will print an ssl.SSLError stack-trace on every connection but will continue to work.

## Installation

Requires Python 3.8+.

```bash
pip install -r requirements.txt
```


