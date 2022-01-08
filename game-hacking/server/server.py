#!/usr/bin/env python

from base64 import b64encode
import asyncio
import copy
import hashlib
import json
import re
import secrets
import sqlite3
import time
import traceback
import websockets

import entity
import inventory
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


SIGN_MESSAGES = [
    "Welcome to MapleQuest!"
]


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

        self.level        = 0
        self.health       = 3
        self.strength     = 1
        self.constitution = 1
        self.intelligence = 1
        self.initiative   = 1

        bonus_item = re.findall(r". (.*) \(.*\)", template["bonus"])[0]
        bonus_item = inventory.deserialize({ "type": bonus_item })
        if bonus_item is None:
            self.inventory = []
        else:
            self.inventory = [bonus_item]
        return self

    def deserialize(serialized):
        self = Character()
        self.name           = serialized["name"]
        self.age            = serialized["age"]
        self.alliance_class = serialized["class"]
        self.alliance_order = serialized["order"]
        self.morality       = serialized["morality"]
        self.inventory      = [inventory.deserialize(x) for x in serialized["inventory"]]
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
            "inventory"    : [x.serialize() for x in self.inventory],
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
        self.mobs = [entity.Sign(5, 5), entity.Zombie(4, 4), entity.Pickup(inventory.Guitar(), 3, 4)]
        self.deltas = [
            { "type": "new_mob", "entity": self.mobs[0].serialize() },
            { "type": "new_mob", "entity": self.mobs[1].serialize() },
            { "type": "new_mob", "entity": self.mobs[2].serialize() }
        ]

    def replace_mob(self, old_id, new):
        for i, mob in enumerate(self.mobs):
            if mob.id == old_id:
                self.mobs[i] = new

    def delete_mob(self, id):
        for i, mob in enumerate(self.mobs):
            print(i, mob, id)
            if mob.id == id:
                return self.mobs.pop(i)

    def process_events(self, events):
        processed = []
        for event in events:
            if event["type"] == "become":
                self.replace_mob(event["id"], event["replacement"])
                processed.append({
                    "type": "become",
                    "id": event["id"],
                    "replacement": event["replacement"].serialize()
                })
            elif event["type"] == "delete_mob":
                self.delete_mob(event["id"])
                processed.append(event)
            else:
                processed.append(event)
        return processed

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
        if entity is not None and entity.can_interact():
            events = entity.interact(self)
            events = self.process_events(events)
            self.deltas += events
        else:
            self.position = anticipated

    def find_entity(self, x, y):
        for entity in self.mobs:
            if entity.position["x"] == x and entity.position["y"] == y:
                return entity

    def pickup_all(self):
        ent = self.find_entity(self.position["x"], self.position["y"])
        if isinstance(ent, entity.Pickup):
            self.character.inventory.append(ent.item)
            events = self.process_events([
                { "type": "message", "text": f"You pick up the {ent.item.type()}" },
                { "type": "new_item", "item": ent.item.serialize() },
                { "type": "delete_mob", "id": ent.id}
            ])
            self.deltas += events

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
    return RATE_LIMITER[ip][endpoint] <= RATE_LIMIT

SESSIONS = []

def lookup_session(token):
    for session in SESSIONS:
        if session.token == token:
            return session

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
        self.username = username
        self.token = b64encode(secrets.token_bytes(16)).decode()
        SESSIONS.append(self)
        return {
            "token": self.token,
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
        for i, session in enumerate(SESSIONS):
            if session.username == username:
                SESSIONS.pop(i)
        self.token = b64encode(secrets.token_bytes(16)).decode()
        SESSIONS.append(self)
        return {
            "token": self.token,
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
    "sign_text": ["id"],
    "move_or_interact": ["direction"],
    "pickup_all": [],
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
    elif packet_type == "sign_text" and validate_fields(message, "sign_text"):
        idx = message["id"]
        if idx >= 0 and idx < len(SIGN_MESSAGES):
            return lambda x: { "text": SIGN_MESSAGES[idx] }
        return lambda x: { "error": "No such sign!" }
    elif packet_type == "move_or_interact" and validate_fields(message, "move_or_interact"):
        del message["type"]
        return lambda x: Connection.game_action(x, GameState.move_or_interact, message)
    elif packet_type == "pickup_all" and validate_fields(message, "pickup_all"):
        del message["type"]
        return lambda x: Connection.game_action(x, GameState.pickup_all, message)
    else:
        return lambda x: { "error": "Unknown packet." }


async def handle_connection(websocket):
    c = Connection(websocket.remote_address)
    while True:
        try:
            packet = await websocket.recv()
            message = json.loads(packet)

            # Special handling for re-connects.
            if message.get("type") == "reconnect" and "token" in message:
                tmp = lookup_session(message["token"])
                if tmp is not None:
                    c = tmp
                else:
                    print("Invalid token")
                continue

            message_id = message.get("id")
            thunk = handle_client_packet(message.get("data", {}))
            await websocket.send(json.dumps({
                "id": message_id,
                "data": thunk(c)
            }))
        except json.JSONDecodeError:
            await websocket.send(json.dumps({
                "error": "Invalid JSON"
            }))
        except websockets.exceptions.ConnectionClosedOK:
            print("Received disconnect: {}".format(websocket.remote_address))
            break
        except Exception as e:
            await websocket.send(json.dumps({
                "error": "Unhandled internal server error: {}".format(traceback.format_exc())
            }))


async def main():
    async with websockets.serve(handle_connection, "localhost", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
