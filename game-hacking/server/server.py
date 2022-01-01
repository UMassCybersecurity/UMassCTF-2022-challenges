#!/usr/bin/env python

import asyncio
import hashlib
import json
import sqlite3
import websockets

# Obviously, we'll need more than `name` and `password` down the line, but I'm
# just doing registration for right now.
con = sqlite3.connect('users.db')
cur = con.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, character INTEGER, FOREIGN KEY(player) REFERENCES characters(id))''')
cur.execute('''CREATE TABLE IF NOT EXISTS characters (id INTEGER PRIMARY KEY, name TEXT, age INTEGER, class TEXT, char_order TEXT, morality TEXT)''')

class Connection(object):
    def __init__(self):
        pass

    # TODO: Rate-limit this endpoint.
    def register_user(self, username, password):
        password_hash = hashlib.md5(password.encode()).digest()
        con = sqlite3.connect('users.db')
        cur = con.cursor()
        cur.execute('''SELECT * FROM users WHERE username = ?''', (username,))
        if len(cur.fetchall()) != 0:
            return None
        cur.execute('''INSERT INTO users (username, password) VALUES (?, ?)''', (username, password_hash))
        con.commit()
        print("Successfully registered as {}".format(username))
        return {
            "username": username,
            "character": None
        }

    def login_user(self, username, password):
        password_hash = hashlib.md5(password.encode()).digest()
        con = sqlite3.connect('users.db')
        cur = con.cursor()
        cur.execute('''SELECT * FROM users WHERE username = ? AND password = ?''', (username, password_hash))
        if len(cur.fetchall()) == 0:
            return None
        print("Successfully logged in as {}".format(username))
        self.username = username
        return {
            "username": username,
            "character": None
        }

    def create_character(self, message):
        # TODO: Better check of whether or not we're logged in.
        if not hasattr(self, "username"):
            return None
        cur.execute('''INSERT INTO characters (name, age, class, char_order, morality) VALUES (?, ?, ?, ?, ?)''', (message["name"], message["age"], message["class"], message["order"], message["morality"]))
        con.commit()
        return {
            "name": message["name"],
            "age": message["age"],
            "class": message["class"],
            "order": message["order"],
            "morality": message["morality"]
        }

EXPECTED_FIELDS = {
    "register": ["username", "password"],
    "login": ["username", "password"],
    "create_character": ["name", "age", "class", "order", "morality", "bonus"],
}

def validate_fields(message, message_type):
    for field in EXPECTED_FIELDS[message_type]:
        if field not in message:
            return False
    return True

def handle_client_packet(packet):
    try:
        message = json.loads(packet)
        message_id = message.get("id")
        message = message.get("data")
        packet_type = message.get("type")
        if packet_type == "register" and validate_fields(message, "register"):
            username = message["username"]
            password = message["password"]
            return (message_id, lambda x: Connection.register_user(x, username, password))
        elif packet_type == "login" and validate_fields(message, "login"):
            username = message["username"]
            password = message["password"]
            return (message_id, lambda x: Connection.login_user(x, username, password))
        elif packet_type == "create_character" and validate_fields(message, "create_character"):
            return (message_id, lambda x: Connection.create_character(x, message))
        elif packet_type == "ping":
            return (message_id, lambda x: "pong!")
        else:
            return (message_id, lambda x: { "error": "Unknown packet." })
    except json.JSONDecodeError:
        pass


async def handle_connection(websocket):
    c = Connection()
    while True:
        packet = await websocket.recv()
        print(packet)
        message_id, thunk = handle_client_packet(packet)
        await websocket.send(json.dumps({
            "id": message_id,
            "data": thunk(c)
        }))

async def main():
    async with websockets.serve(handle_connection, "localhost", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
