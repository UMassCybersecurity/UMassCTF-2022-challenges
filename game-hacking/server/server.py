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
    character TEXT,
    game_state TEXT
);
''')
con.commit()
cur.close()
con.close()


class GameState(object):
    """All-encompassing state object for a session of the game."""
    def __init__(self):
        self.x = 0
        self.y = 0


class Connection(object):
    """State associated with a particular connection.

    This object primarily concerns account management, but also owns a
    `GameState` to describe the current character and world.
    """
    def __init__(self, ip):
        self.ip = ip
        self.logged_in = False
        self.game_state = None

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

    def create_character(self, template):
        if not self.logged_in:
            return None
        con = sqlite3.connect('users.db')
        cur = con.cursor()

        cur.execute('''UPDATE users SET character = ? WHERE id = ?''', (json.dumps(template), self.user_id))
        con.commit()

        return {
            "name": template["name"],
            "age": template["age"],
            "class": template["class"],
            "order": template["order"],
            "morality": template["morality"],
            "world": worldgen.generate_world()
        }

    def character(self):
        con = sqlite3.connect('users.db')
        cur = con.cursor()
        cur.execute('''SELECT character FROM users WHERE id = ?''', (self.user_id,))
        result = cur.fetchone()
        if len(result) == 0:
            return None
        return json.loads(result[0])


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


def handle_client_packet(message):
    packet_type = message.get("type")
    if packet_type == "register" and validate_fields(message, "register"):
        return lambda x: Connection.register_user(x, message["username"], message["password"])
    elif packet_type == "login" and validate_fields(message, "login"):
        return lambda x: Connection.login_user(x, message["username"], message["password"])
    elif packet_type == "create_character" and validate_fields(message, "create_character"):
        del message["type"]
        return lambda x: Connection.create_character(x, message)
    else:
        return lambda x: { "error": "Unknown packet." }


async def handle_connection(websocket):
    c = Connection(websocket.remote_address)
    while True:
        packet = await websocket.recv()
        try:
            message = json.loads(packet)
            message_id = message.get("id")
            thunk = handle_client_packet(message.get("data", {}))
            await websocket.send(json.dumps({
                "id": message_id,
                "data": thunk(c)
            }))
        except json.JSONDecodeError:
            pass


async def main():
    async with websockets.serve(handle_connection, "localhost", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
