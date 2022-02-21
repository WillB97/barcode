#! /usr/bin/env python3
import sys
import argparse
import warnings

import socketio
import pyqrcode


def run_receiver(url, insecure=False):
    if insecure:
        warnings.filterwarnings('ignore', message='Unverified HTTPS request')
        sio = socketio.Client(ssl_verify=False)
    else:
        sio = socketio.Client()

    @sio.on('barcode')
    def on_barcode(message):
        """Print received barcode"""
        if message.get('barcode') is not None:
            print(message['barcode'])

    @sio.on('devices')
    def device_change(message):
        """Announce devices joining or leaving toe stderr"""
        if message.get('connected'):
            print('A device connected', file=sys.stderr)
        else:
            print('A device disconnected', file=sys.stderr)

    @sio.on('enter')
    def on_enter(message):
        if message.get('room') is not None:
            print(f"Room ID: {message['room']}", file=sys.stderr)
            qrcode = pyqrcode.create(message['room'])
            print(qrcode.terminal(quiet_zone=1))

    sio.connect(url)
    sio.emit('enter', {'type': 'receiver'})

    sio.wait()


def main():
    parser = argparse.ArgumentParser(
        description="Console receiver for web-based barcode scanner"
    )
    parser.add_argument(
        'url',
        help="The URI of the barcode server. e.g. https://localhost:5000/"
    )
    parser.add_argument(
        '--insecure',
        action='store_true',
        help="Allow self-signed certificates by disabling SSL verification"
    )

    args = parser.parse_args()
    try:
        run_receiver(args.url, args.insecure)
        pass
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
