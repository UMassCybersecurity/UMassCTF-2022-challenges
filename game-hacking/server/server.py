#!/usr/bin/env python

import asyncio
import hashlib
import json
import sqlite3
import websockets

import worldgen

# Initialise the database.
con = sqlite3.connect('users.db')
cur = con.cursor()
cur.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    character INTEGER,
    FOREIGN KEY(character) REFERENCES characters(id)
);
''')
cur.execute('''
CREATE TABLE IF NOT EXISTS characters (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    class TEXT NOT NULL,
    char_order TEXT NOT NULL,
    morality TEXT NOT NULL
);
''')
con.commit()
cur.close()
con.close()

class Connection(object):
    def __init__(self):
        self.logged_in = False

    # TODO: Rate-limit this endpoint.
    def register_user(self, username, password):
        con = sqlite3.connect('users.db')
        cur = con.cursor()

        # Does the username exist already?
        cur.execute('''SELECT * FROM users WHERE username = ?''', (username,))
        if len(cur.fetchall()) != 0:
            return None

        password_hash = hashlib.md5(password.encode()).digest()
        print(password_hash)
        cur.execute('''INSERT INTO users (username, password) VALUES (?, ?)''', (username, password_hash))
        con.commit()
        self.user_id = cur.lastrowid

        print("Successfully registered as {}".format(username))
        self.logged_in = True
        return {
            "username": username,
            "character": None
        }

    def login_user(self, username, password):
        password_hash = hashlib.md5(password.encode()).digest()
        con = sqlite3.connect('users.db')
        cur = con.cursor()
        cur.execute('''SELECT id FROM users WHERE username = ? AND password = ?''', (username, password_hash))
        result = cur.fetchone()
        if len(result) == 0:
            return None
        self.user_id = result[0]

        print("Successfully logged in as {}".format(username))
        self.logged_in = True
        self.username = username
        return {
            "username": username,
            "character": self.character()
        }

    def create_character(self, message):
        if not self.logged_in:
            return None
        con = sqlite3.connect('users.db')
        cur = con.cursor()

        # Create the actual character entry.
        cur.execute(
            '''INSERT INTO characters (name, age, class, char_order, morality) VALUES (?, ?, ?, ?, ?)''',
            (message["name"], message["age"], message["class"], message["order"], message["morality"])
        )

        # Update the `user` entry to point at it.
        character_id = cur.lastrowid
        cur.execute('''UPDATE users SET character = ? WHERE id = ?''', (character_id, self.user_id))
        con.commit()

        return {
            "name": message["name"],
            "age": message["age"],
            "class": message["class"],
            "order": message["order"],
            "morality": message["morality"],
            "world": worldgen.generate_world()
        }

    def character_id(self):
        con = sqlite3.connect('users.db')
        cur = con.cursor()
        cur.execute('''SELECT character FROM users WHERE id = ?''', (self.user_id,))
        result = cur.fetchone()
        if len(result) == 0:
            return None
        return result[0]

    def character(self):
        con = sqlite3.connect('users.db')
        cur = con.cursor()
        cur.execute('''SELECT name, age, class, char_order, morality FROM characters WHERE id = ?''', (self.character_id(),))
        result = cur.fetchone()
        if len(result) == 0:
            return None
        return dict(zip(["name", "age", "class", "order", "morality"], result))

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
