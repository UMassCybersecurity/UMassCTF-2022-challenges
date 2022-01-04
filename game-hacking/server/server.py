#!/usr/bin/env python

import asyncio
import copy
import hashlib
import json
import sqlite3
import time
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


class Sign(object):
    def __init__(self):
        self.position = { "x": 5, "y": 5 }
        self.text = "This sign is a test."

    def interact(self, game_state):
        return [
            { "type": "message", "text": "The sign reads: \"{}\"".format(self.text) }
        ]

    def serialize(self):
        return {
            "position": self.position,
            "world_view": "🪧",
        }

class Zombie(object):
    def __init__(self):
        self.position = { "x": 4, "y": 4 }
        self.health = 5

    def interact(self, game_state):
        self.health -= 1
        base = [
            { "type": "message", "text": "You hit the zombie." }
        ]
        if self.health == 0:
            return base + [ { "type": "message", "text": "The zombie dies!" } ]
        return base


    def serialize(self):
        return {
            "position": self.position,
            "world_view": "🧟",
        }


class Character(object):
    def __init__(self):
        pass

    def from_template(template):
        self = Character()
        self.name           = template["name"]
        self.age            = template["age"]
        self.alliance_class = template["class"]
        self.alliance_order = template["order"]
        self.morality       = template["morality"]
        # TODO: Parse bonus into inventory system entity.
        self.inventory      = [template["bonus"]]
        self.level          = 0
        self.health         = 3
        self.strength       = 1
        self.constitution   = 1
        self.intelligence   = 1
        self.initiative     = 1
        return self

    def deserialize(serialized):
        self = Character()
        self.name           = serialized["name"]
        self.age            = serialized["age"]
        self.alliance_class = serialized["class"]
        self.alliance_order = serialized["order"]
        self.morality       = serialized["morality"]
        # TODO: Deserialize inventory.
        self.inventory      = serialized["inventory"]
        self.level          = serialized["level"]
        self.health         = serialized["health"]
        self.strength       = serialized["strength"]
        self.constitution   = serialized["constitution"]
        self.intelligence   = serialized["intelligence"]
        self.initiative     = serialized["initiative"]
        return self

    def serialize(self):
        return {
            "name"         : self.name,
            "age"          : self.age,
            "class"        : self.alliance_class,
            "order"        : self.alliance_order,
            "morality"     : self.morality,
            # TODO: Map deserialize onto `self.inventory`
            "inventory"    : self.inventory,
            "level"        : self.level,
            "health"       : self.health,
            "strength"     : self.strength,
            "constitution" : self.constitution,
            "intelligence" : self.intelligence,
            "initiative"   : self.initiative,
        }

class GameState(object):
    """All-encompassing state object for a session of the game."""
    def __init__(self, character):
        self.character = character
        self.position = { "x": 0, "y": 0 }
        self.mobs = [Sign(), Zombie()]
        self.deltas = [
            { "type": "new_mob", "entity": self.mobs[0].serialize() },
            { "type": "new_mob", "entity": self.mobs[1].serialize() }
        ]

    def move_or_interact(self, direction):
        anticipated = copy.copy(self.position)
        if direction == "north":
            anticipated["y"] -= 1
        elif direction == "northeast":
            anticipated["y"] -= 1
            anticipated["x"] += 1
        elif direction == "east":
            anticipated["x"] += 1
        elif direction == "southeast":
            anticipated["y"] += 1
            anticipated["x"] += 1
        elif direction == "south":
            anticipated["y"] += 1
        elif direction == "southwest":
            anticipated["y"] += 1
            anticipated["x"] -= 1
        elif direction == "west":
            anticipated["x"] -= 1
        elif direction == "northwest":
            anticipated["y"] -= 1
            anticipated["x"] -= 1

        entity = self.find_entity(anticipated["x"], anticipated["y"])
        if entity is not None:
            self.deltas += entity.interact(self)
        else:
            self.position = anticipated

    def find_entity(self, x, y):
        for entity in self.mobs:
            if entity.position["x"] == x and entity.position["y"] == y:
                return entity

    def queue_updates(self):
        deltas = self.deltas
        self.deltas = []
        return [
            { "type": "update_position", "x": self.position["x"], "y": self.position["y"] },
        ] + deltas


RATE_LIMIT = 32
RATE_LIMIT_LAST_FLUSH = time.time()
RATE_LIMITER = {}
def allowed_by_rate_limit(endpoint, ip):
    global RATE_LIMIT_LAST_FLUSH
    global RATE_LIMITER
    if time.time() >= RATE_LIMIT_LAST_FLUSH + 3600:
        RATE_LIMIT_LAST_FLUSH = time.time()
        RATE_LIMITER = {}
    if ip not in RATE_LIMITER:
        RATE_LIMITER[ip] = {}
    if endpoint not in RATE_LIMITER[ip]:
        RATE_LIMITER[ip][endpoint] = 0
    RATE_LIMITER[ip][endpoint] += 1
    return RATE_LIMITER[ip][endpoint] >= RATE_LIMIT


class Connection(object):
    """State associated with a particular connection.

    This object primarily concerns account management, but also owns a
    `GameState` to describe the current character and world.
    """
    def __init__(self, ip):
        self.ip = ip
        self.logged_in = False
        self.game_state = None

    def register_user(self, username, password):
        if not allowed_by_rate_limit("register_user", self.ip):
            return None

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
        if result is None:
            return None
        self.user_id = result[0]

        print("Successfully logged in as {}".format(username))
        self.logged_in = True
        self.username = username
        self.game_state = GameState(Character.deserialize(self.character()))
        return {
            "username": username,
            "character": self.character()
        }

    def create_character(self, template):
        if not self.logged_in:
            return None
        con = sqlite3.connect('users.db')
        cur = con.cursor()

        c = Character.from_template(template)
        cur.execute('''UPDATE users SET character = ? WHERE id = ?''',
                    (json.dumps(c.serialize()), self.user_id))
        con.commit()
        self.game_state = GameState(c)

        return {
            "character": c.serialize(),
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

    def game_action(self, handler, message):
        if self.game_state is not None:
            handler(self.game_state, **message)
            return self.game_state.queue_updates()


EXPECTED_FIELDS = {
    "register": ["username", "password"],
    "login": ["username", "password"],
    "create_character": ["name", "age", "class", "order", "morality", "bonus"],
    "move_or_interact": ["direction"],
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
    elif packet_type == "move_or_interact" and validate_fields(message, "move_or_interact"):
        del message["type"]
        return lambda x: Connection.game_action(x, GameState.move_or_interact, message)
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
