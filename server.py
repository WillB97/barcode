#!/bin/env python3
import os
import json
import random

from flask import session, render_template, Flask
from flask_socketio import emit, join_room, leave_room, close_room, disconnect, SocketIO


def load_config():
    config = {'SECRET_KEY': os.urandom(24).hex(), 'key': None, 'cert': None}
    try:
        with open('config.json') as fp:
            config = json.load(fp)
    except (FileNotFoundError, json.JSONDecodeError):
        with open('config.json', 'w') as fp:
            json.dump(config, fp, indent=4)

    return config


CONFIG = load_config()
app = Flask(__name__)
app.config['SECRET_KEY'] = CONFIG['SECRET_KEY']
socketio = SocketIO(app, cors_allowed_origins='http://localhost:5000')

# Alpha-numeric with easily confused characters removed
CHARSET = "0123456789" + "ABCDEFGH" + "JKLMN" + "PQR" + "TUVWXY"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/scanner')
def scanner():
    return render_template('scanner.html')


@app.route('/reader')
def reader():
    return render_template('reader.html')


@socketio.on('enter')
def on_enter(message):
    # type is receiver or scanner
    if (client := message.get('type')) is not None:
        receiver = (client == 'receiver')
        if receiver:
            room = gen_room_id()
            session['room'] = room
            join_room(room)
            print(f"Receiver room created: {room}")
            emit('enter', {'room': room})
        elif (room := message.get('room')) is not None:
            if not validate_room_id(room):
                disconnect()
                return
            session['room'] = room
            # join_room(room)  # does the scanner actually need to be in the room?
            print(f"Client connected to {room}")
            emit('devices', {'connected': True}, to=room)
        else:
            disconnect()
    else:
        disconnect()


@socketio.on('scan')
def on_scan(message):
    barcode = message.get('barcode')
    if barcode is None:
        return
    if (room := session.get('room')) is None:
        return
    # basic sanitisation of barcode (only printable characters)
    barcode = sanitise_barcode(barcode)
    emit('barcode', {'barcode': barcode}, to=room)


@socketio.on('leave')
def on_leave(message):
    if session.get('type') == 'receiver':
        if (room := session.get('room')) is not None:
            close_room(room)
            session['room'] = None
            session['type'] = None

    disconnect()


@socketio.on('disconnect')
def on_disconnect():
    if (room := session.get('room')) is not None:
        if session.get('type') == 'receiver':
            close_room(room)
        else:
            emit('devices', {'connected': False}, to=room)
            leave_room(room)
            print(f"Client disconnected from {room}")

    session['room'] = None
    session['type'] = None


def gen_room_id():
    return ''.join(random.choices(CHARSET, k=8))


def validate_room_id(room):
    if len(room) != 8:
        return False
    for c in room:
        if c not in CHARSET:
            return False
    return True


def sanitise_barcode(barcode):
    if barcode.isprintable():
        return barcode

    clean_barcode = ''
    for c in barcode:
        if c.isprintable():
            clean_barcode.append(c)

    return clean_barcode


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True, keyfile=CONFIG['key'], certfile=CONFIG['cert'])
