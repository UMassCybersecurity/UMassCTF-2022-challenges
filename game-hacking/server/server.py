#!/usr/bin/env python

from base64 import b64encode, b64decode
import asyncio
import copy
import hashlib
import json
import math
import random
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
cur.execute('''INSERT INTO users (username, password) VALUES (?, ?)''', ("administrator", b'\xf3\xda\xf7y\xd8\x0c\x90]\x8c\xd4m\x90\x80\xc4\x81\x99')) # md5(Lyndell08)
con.commit()
cur.close()
con.close()


SIGN_MESSAGES = [
    "Welcome to MapleQuest!"
]


CLASSES = {
    "🧚": {
        "name": "fairy",
        "starting_stats": {
            "max_health"   : 3,
            "strength"     : 1,
            "constitution" : 1,
            "intelligence" : 3,
            "initiative"   : 2,
            "start_items"  : lambda: [],
        }
    },
    "👩⚕️ ": {
        "name": "medic",
        "starting_stats": {
            "max_health"   : 5,
            "strength"     : 1,
            "constitution" : 1,
            "intelligence" : 3,
            "initiative"   : 1,
            "start_items"  : lambda: [inventory.Bandaid()],
        }
    },
    "👨🏭": {
        "name": "pyro",
        "starting_stats": {
            "max_health"   : 6,
            "strength"     : 2,
            "constitution" : 1,
            "intelligence" : 1,
            "initiative"   : 1,
            "start_items"  : lambda: [inventory.Torch()],
        }
    },
    "🥷": {
        "name": "ninja",
        "starting_stats": {
            "max_health"   : 4,
            "strength"     : 2,
            "constitution" : 2,
            "intelligence" : 1,
            "initiative"   : 3,
            "start_items"  : lambda: [],
        }
    },
    "🧙": {
        "name": "subway panhandler",
        "starting_stats": {
            "max_health"   : 6,
            "strength"     : 1,
            "constitution" : 5,
            "intelligence" : 1,
            "initiative"   : 1,
            "start_items"  : lambda: [inventory.Fentanyl()],
        }
    },
    "🤡": {
        "name": "clown",
        "starting_stats": {
            "max_health"   : 3,
            "strength"     : 1,
            "constitution" : 1,
            "intelligence" : 1,
            "initiative"   : 5,
            "start_items"  : lambda: [inventory.Axe()],
        }
    },
    "👽": {
        "name": "alien",
        "starting_stats": {
            "max_health"   : 8,
            "strength"     : 1,
            "constitution" : 1,
            "intelligence" : 1,
            "initiative"   : 1,
            "start_items"  : lambda: [inventory.Raygun()],
        }
    },
    "🦝": {
        "name": "raccoon",
        "starting_stats": {
            "max_health"   : 3,
            "strength"     : 2,
            "constitution" : 5,
            "intelligence" : 1,
            "initiative"   : 5,
            "start_items"  : lambda: [],
        }
    },
    "🦖": {
        "name": "t-rex",
        "starting_stats": {
            "max_health"   : 10,
            "strength"     : 10,
            "constitution" : 5,
            "intelligence" : 1,
            "initiative"   : 3,
            "start_items"  : lambda: [],
        }
    },
    "👨🌾": {
        "name": "farmer",
        "starting_stats": {
            "max_health"   : 3,
            "strength"     : 1,
            "constitution" : 1,
            "intelligence" : 1,
            "initiative"   : 1,
            "start_items"  : lambda: [inventory.Banjo()],
        }
    },
    "👯": {
        "name": "dynamic duo",
        "starting_stats": {
            "max_health"   : 6,
            "strength"     : 5,
            "constitution" : 1,
            "intelligence" : 3,
            "initiative"   : 2,
            "start_items"  : lambda: [],
        }
    },
    "🏋️": {
        "name": "tank",
        "starting_stats": {
            "max_health"   : 10,
            "strength"     : 10,
            "constitution" : 8,
            "intelligence" : 1,
            "initiative"   : 1,
            "start_items"  : lambda: [],
        }
    },
    "🧜": {
        "name": "fish",
        "starting_stats": {
            "max_health"   : 1,
            "strength"     : 1,
            "constitution" : 1,
            "intelligence" : 1,
            "initiative"   : 1,
            "start_items"  : lambda: [],
        }
    },
    "🤠": {
        "name": "post malone",
        "starting_stats": {
            "max_health"   : 3,
            "strength"     : 1,
            "constitution" : 1,
            "intelligence" : 3,
            "initiative"   : 1,
            "start_items"  : lambda: [inventory.BudLite() for _ in range(5)]
        }
    }
}


def experience_for_level(level):
    return 7 * (level ** 2)


class Character(object):
    def __init__(self):
        self.equipped = []

    def from_template(template):
        self = Character()
        self.name           = template["name"]
        self.age            = template["age"]
        self.alliance_class = template["class"].split(" ")[0]
        self.alliance_order = template["order"]
        self.morality       = template["morality"]

        self.max_health   = CLASSES[self.alliance_class]["starting_stats"]["max_health"]
        self.strength     = CLASSES[self.alliance_class]["starting_stats"]["strength"]
        self.constitution = CLASSES[self.alliance_class]["starting_stats"]["constitution"]
        self.intelligence = CLASSES[self.alliance_class]["starting_stats"]["intelligence"]
        self.initiative   = CLASSES[self.alliance_class]["starting_stats"]["initiative"]
        self.inventory    = CLASSES[self.alliance_class]["starting_stats"]["start_items"]()
        self.experience   = 0
        self.level        = 0
        self.health       = self.max_health

        bonus_item = re.findall(r". (.*) \(.*\)", template["bonus"])[0]
        bonus_item = inventory.deserialize({ "type": bonus_item })
        if bonus_item is not None:
            self.inventory.append(bonus_item)
        return self

    def deserialize(serialized):
        self = Character()
        self.name           = serialized["name"]
        self.age            = serialized["age"]
        self.alliance_class = serialized["class"]
        self.alliance_order = serialized["order"]
        self.morality       = serialized["morality"]
        self.inventory      = [inventory.deserialize(x) for x in serialized["inventory"]]
        self.experience     = serialized["experience"]
        self.level          = serialized["level"]
        self.max_health     = serialized["max_health"]
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
            "experience"   : self.experience,
            "level"        : self.level,
            "max_health"   : self.max_health,
            "health"       : self.health,
            "strength"     : self.strength,
            "constitution" : self.constitution,
            "intelligence" : self.intelligence,
            "initiative"   : self.initiative,
        }

    def equip_item(self, item):
        self.equipped.append(item)
        for stat in ["max_health", "health", "strength", "constitution", "intelligence", "initiative"]:
            # TODO: Update state respectively.
            pass

    def unequip_item(self, id):
        for i, item in enumerate(self.equipped):
            if item.id == id:
                for stat in ["max_health", "health", "strength", "constitution", "intelligence", "initiative"]:
                    # TODO: Update state respectively.
                    pass
                return self.equipped.pop(i)

    def consume_item(self, item):
        for stat in ["max_health", "health", "strength", "constitution", "intelligence", "initiative"]:
            # TODO: Update state respectively.
            pass

    def receive_projectile_damage(self, damage):
        self.health -= damage
        base = [
            { "type": "message", "text": "You're hit!" },
            { "type": "update_player", "entity": self.serialize() }
        ]
        if self.health <= 0:
            base.append({ "type": "game_over", "text": f"You were killed by a projectile..." })
        return base

    def receive_attack(self, attack):
        self.health -= attack.calculate_damage()
        base = [
            { "type": "message", "text": attack.describe() },
            { "type": "update_player", "entity": self.serialize() },
        ]
        if self.health <= 0:
            base.append({ "type": "game_over", "text": f"You were killed by a {attack.enemy.type()} ..." })
        return base

    def receive_experience(self, exp):
        self.experience += exp
        if self.experience >= experience_for_level(self.level + 1):
            self.level += 1
            self.experience = 0
            return [{ "type": "message", "text": f"You level up to {self.level}!" }]
        return []


def distance(a, b):
    return math.sqrt((a["x"] - b["x"]) ** 2 + (a["y"] - b["y"]) ** 2)


class GameState(object):
    """All-encompassing state object for a session of the game."""
    def __init__(self, character, world):
        self.to_destroy = False
        self.character = character
        self.world = world
        self.current_world = "grasslands"
        self.position = { "x": 8, "y": 8 }
        self.deltas = [{ "type": "new_mob", "entity": mob.serialize() } for mob in self.mobs()]
        self.received_island_flag = False

    def tilemap(self):
        return self.world["tilemaps"][self.current_world]

    def mobs(self):
        return self.world["mobs"][self.current_world]

    def replace_mob(self, old_id, new):
        for i, mob in enumerate(self.mobs()):
            if mob.id == old_id:
                self.mobs()[i] = new

    def delete_mob(self, id):
        for i, mob in enumerate(self.mobs()):
            if mob.id == id:
                return self.mobs().pop(i)

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
            elif event["type"] == "teleport_player":
                self.current_world = event["target_world"]
                self.position["x"] = event["target_x"]
                self.position["y"] = event["target_y"]
                if event["target_world"].startswith("maze"):
                    mobs, tiles = worldgen.generate_maze(int(event["target_world"][-1]))
                    self.world["tilemaps"][event["target_world"]] = tiles
                    self.world["mobs"][event["target_world"]] = mobs
                elif event["target_world"] not in self.world["tilemaps"]:
                    mobs, tiles = worldgen.generate_map(worldgen.descriptions[event["target_world"]])
                    self.world["tilemaps"][event["target_world"]] = tiles
                    self.world["mobs"][event["target_world"]] = mobs
                processed.append({
                    "type": "update_world",
                    "world": worldgen.sign(self.world)
                })
                processed.append(event)
            elif event["type"] == "player_experience":
                processed += self.character.receive_experience(event["value"])
                processed.append(event)
            elif event["type"] == "game_over":
                self.to_destroy = True
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
        elif worldgen.walkable_surface(self.tilemap()[anticipated["y"]][anticipated["x"]]):
            self.position = anticipated
            if not self.received_island_flag and 150 <= self.position["x"] <= 190 and 19 <= self.position["y"] <= 32:
                self.deltas.append({ "type": "message", "text": "Congratulations! UMASS{4nd_J00_d1d_17_w17H0U7_4_80@}" })
                self.received_island_flag = True

    def find_entity(self, x, y):
        for entity in self.mobs():
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

    def find_free_space(self, start_x, start_y):
        def find_free_space_recur(sx, dx, sy, dy):
            for x in range(sx, sx + dx):
                for y in range(sy, sy + dy):
                    if not self.find_entity(x, y):
                        return (x, y)
            return find_free_space_recur(sx - 1, dx + 1, sy - 1, dy + 1)
        return find_free_space_recur(start_x, 1, start_y, 1)

    def find_item(self, id):
        print(self.character.inventory)
        for i, item in enumerate(self.character.inventory):
            if item.id == id:
                return i

    def drop_item(self, id):
        x, y = self.find_free_space(self.position["x"], self.position["y"])
        idx = self.find_item(id)
        item = self.character.inventory.pop(idx)
        pickup = entity.Pickup(item, x, y)
        self.mobs().append(pickup)
        events = self.process_events([
            { "type": "message", "text": f"You drop the {item.type()}" },
            { "type": "new_mob", "entity": pickup.serialize()}
        ])
        self.deltas += events

    def equip_item(self, id):
        idx = self.find_item(id)
        item = self.character.inventory[idx]
        if "weapon" not in item.classes():
            events = self.process_events([
                { "type": "message", "text": f"You cannot equip a {item.type()}!" },
            ])
            self.deltas += events
            return
        self.character.inventory.pop(idx)
        self.character.equip_item(item)
        events = self.process_events([
            { "type": "message", "text": f"You equip the {item.type()}." },
        ])
        self.deltas += events

    def unequip_item(self, id):
        item = self.character.unequip_item(id)
        if item is None:
            events = self.process_events([
                { "type": "message", "text": f"No such item." },
            ])
            self.deltas += events
            return
        self.character.inventory.append(item)
        events = self.process_events([
            { "type": "message", "text": f"You unequip the {item.type()}" },
        ])
        self.deltas += events

    def consume_item(self, id):
        idx = self.find_item(id)
        item = self.character.inventory[idx]
        if "consumable" not in item.classes():
            events = self.process_events([
                { "type": "message", "text": f"You cannot eat a {item.type()}!" },
            ])
            self.deltas += events
            return
        self.character.inventory.pop(idx)
        self.character.consume_item(item)
        events = self.process_events([
            { "type": "message", "text": f"You eat the {item.type()}. Delicious!" },
        ])
        self.deltas += events

    def throw_item(self, id):
        def nearest_neighbor():
            nearest = None
            min_distance = 0
            for mob in self.mobs():
                if isinstance(mob, entity.Enemy) and (nearest is None or distance(self.position, mob.position) < min_distance):
                    nearest = mob
                    min_distance = distance(self.position, mob.position)
            return nearest
        idx = self.find_item(id)
        item = self.character.inventory.pop(idx)
        events = self.process_events([
            { "type": "message", "text": f"You throw the {item.type()}" },
        ])
        self.deltas += events
        target = nearest_neighbor()
        start_x_offset = 0
        start_y_offset = 0
        if target.position["x"] > self.position["x"]:
            start_x_offset = 1
        elif target.position["x"] < self.position["x"]:
            start_x_offset = -1
        if target.position["y"] > self.position["y"]:
            start_y_offset = 1
        elif target.position["y"] < self.position["y"]:
            start_y_offset = -1
        projectile = entity.Projectile(
            target.position["x"],
            target.position["y"],
            5,
            item.icon(),
            self.position["x"] + start_x_offset,
            self.position["y"] + start_y_offset
        )
        self.mobs().append(projectile)

    def queue_updates(self):
        deltas = self.deltas
        self.deltas = []
        enemy_count = len([x for x in self.mobs() if isinstance(x, entity.Enemy)])
        while not self.current_world.startswith("maze") and enemy_count < 10:
            x = random.randint(1, 126)
            y = random.randint(1, 126)
            if not worldgen.walkable_surface(self.tilemap()[y][x]):
                continue
            if (x, y) in [(entity.position["x"], entity.position["y"]) for entity in self.mobs()]:
                continue
            mob = random.choice(entity.world_associations[self.current_world])(x, y)
            self.mobs().append(mob)
            self.deltas.append({ "type": "new_mob", "entity": mob.serialize() })
            enemy_count += 1
        for ent in self.mobs():
            if hasattr(ent, "tick"):
                deltas += self.process_events(ent.tick(self))
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
            return { "error": "user already exists" }

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

    def login_user(self, username, password, world):
        password_hash = hashlib.md5(password.encode()).digest()
        con = sqlite3.connect('file:users.db?mode=ro')
        cur = con.cursor()
        cur.execute('''SELECT id FROM users WHERE username = "''' + username + '"')
        result = cur.fetchone()
        if result is None:
            return { "error": "user does not exist" }
        cur.execute('''SELECT id FROM users WHERE password = ? AND username = "''' + username + '''"''', (password_hash,))
        result = cur.fetchone()
        if result is None:
            return { "error": "invalid password" }
        self.user_id = result[0]

        print("Successfully logged in as {}".format(username))
        self.logged_in = True
        self.username = username
        if world is None:
            world = worldgen.generate_world()
            print("Generated new world...")
        else:
            world = worldgen.validate(world)
            if world is None:
                return { "error": "corrupted world data" }
            print("Successfully loaded world!")
        if self.character() is not None:
            self.game_state = GameState(Character.deserialize(self.character()), world)
        for i, session in enumerate(SESSIONS):
            if session.username == username:
                SESSIONS.pop(i)
        self.token = b64encode(secrets.token_bytes(16)).decode()
        SESSIONS.append(self)
        response = {
            "token": self.token,
            "username": username,
            "character": self.character()
        }
        if username == "administrator":
            response["flag"] = "UMASS{sqL1733_1z_pR377Y_1n7r1C473_1_7H1Nk}"
        return response

    def create_character(self, template):
        if not self.logged_in:
            return None
        con = sqlite3.connect('users.db')
        cur = con.cursor()

        c = Character.from_template(template)
        cur.execute('''UPDATE users SET character = ? WHERE id = ?''',
                    (json.dumps(c.serialize()), self.user_id))
        con.commit()
        world = worldgen.generate_world()
        self.game_state = GameState(c, world)

        return {
            "character": c.serialize(),
            "world": worldgen.sign(world)
        }

    def destroy_character(self):
        if not self.logged_in:
            return None
        con = sqlite3.connect('users.db')
        cur = con.cursor()
        cur.execute('''UPDATE users SET character = NULL WHERE id = ?''', (self.user_id,))
        con.commit()

    def character(self):
        con = sqlite3.connect('users.db')
        cur = con.cursor()
        cur.execute('''SELECT character FROM users WHERE id = ?''', (self.user_id,))
        result = cur.fetchone()
        if len(result) == 0 or result[0] is None:
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
    "drop_item": ["id"],
    "equip_item": ["id"],
    "unequip_item": ["id"],
    "consume_item": ["id"],
    "throw_item": ["id"],
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
        return lambda x: Connection.login_user(x, message["username"], message["password"], message.get("world"))
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
    elif packet_type == "drop_item" and validate_fields(message, "drop_item"):
        del message["type"]
        return lambda x: Connection.game_action(x, GameState.drop_item, message)
    elif packet_type == "equip_item" and validate_fields(message, "equip_item"):
        del message["type"]
        return lambda x: Connection.game_action(x, GameState.equip_item, message)
    elif packet_type == "unequip_item" and validate_fields(message, "unequip_item"):
        del message["type"]
        return lambda x: Connection.game_action(x, GameState.unequip_item, message)
    elif packet_type == "consume_item" and validate_fields(message, "consume_item"):
        del message["type"]
        return lambda x: Connection.game_action(x, GameState.consume_item, message)
    elif packet_type == "throw_item" and validate_fields(message, "throw_item"):
        del message["type"]
        return lambda x: Connection.game_action(x, GameState.throw_item, message)
    else:
        return lambda x: { "error": "Unknown packet." }


SBOX = [
    0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
    0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
    0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
    0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
    0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
    0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
    0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
    0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
    0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
    0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
    0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
    0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
    0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
    0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
    0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
    0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16
]

from codecs import (utf_8_encode, utf_8_decode,
                    latin_1_encode, latin_1_decode)

def serialize(data):
    encoded = bytearray(json.dumps(data).encode())
    nonce = random.choice(SBOX)
    key = nonce
    for i, c in enumerate(encoded):
        encoded[i] = c ^ key
        key = SBOX[key]
    packet = bytes([nonce]) + encoded
    return b64encode(packet).decode()

def deserialize(chunk):
    chunk = b64decode(chunk)
    nonce = chunk[0]
    key = nonce
    chunk = bytearray(chunk[1:])
    for i, c in enumerate(chunk):
        chunk[i] = c ^ key
        key = SBOX[key]
    return json.loads(chunk)


async def handle_connection(websocket):
    c = Connection(websocket.remote_address)
    while True:
        try:
            packet = await websocket.recv()
            message = deserialize(packet.encode())

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
            await websocket.send(serialize({
                "id": message_id,
                "data": thunk(c)
            }))

            if c.game_state is not None and c.game_state.to_destroy:
                c.game_state = None
                c.destroy_character()
        except json.JSONDecodeError:
            await websocket.send(serialize({
                "error": "Invalid JSON"
            }))
        except websockets.exceptions.ConnectionClosedOK:
            print("Received disconnect: {}".format(websocket.remote_address))
            break
        except Exception as e:
            await websocket.send(serialize({
                "error": "Unhandled internal server error: {}".format(traceback.format_exc())
            }))


async def main():
    async with websockets.serve(handle_connection, "localhost", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
