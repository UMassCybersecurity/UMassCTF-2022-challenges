from base64 import b64encode, b64decode
from enum import Enum
from perlin_noise import PerlinNoise
import binascii
import hashlib
import json
import random
import uuid

import entity
import inventory

class Tile(Enum):
    NOTHING        = 0
    GRASS0         = 1
    GRASS1         = 2
    GRASS2         = 3
    GRASS3         = 4
    WALL           = 5
    FLOOR          = 6
    SAND0          = 7
    SAND1          = 8
    SAND2          = 9
    SAND3          = 10
    SANDSTONE      = 11
    SANDSTONE_WALL = 12
    ICE0           = 13
    ICE1           = 14
    ICE2           = 15
    ICE3           = 16
    COBALT         = 17
    COBALT_WALL    = 18
    


SECRET_KEY = b"kEYlEN97H_12_14"

# High-level description of worldgen
#
# 1. Draw bounding box(es).
# 2. Fill with output of noise function.
# 3. Pick a random (x, y) coordinate as an anchor.
# 4. Draw one or more rectangles within bounding box.
# 5. Bound this shape
#    1. I _believe_ we can assume it to be contiguous, so we can use a line-scanning algorithm.
# 6. Add a door.
# 7. Go back to step (3.), repeat some number of times
# 8. Put down environmental tiles wherever buildings do not exist.

def walkable_surface(surf):
    return surf in map(lambda x: x.value, [
        Tile.GRASS0, Tile.GRASS1, Tile.GRASS2, Tile.GRASS3,
        Tile.FLOOR,
        Tile.SAND0, Tile.SAND1, Tile.SAND2, Tile.SAND3,
        Tile.SANDSTONE,
        Tile.ICE0, Tile.ICE1, Tile.ICE2, Tile.ICE3,
        Tile.COBALT
    ])


def natural_surface(surf):
    return surf in map(lambda x: x.value, [
        Tile.GRASS0, Tile.GRASS1, Tile.GRASS2, Tile.GRASS3,
        Tile.SAND0, Tile.SAND1, Tile.SAND2, Tile.SAND3,
        Tile.ICE0, Tile.ICE1, Tile.ICE2, Tile.ICE3
    ])


def generate_maze(n):
    world = []
    entities = [entity.Portal(0, "grasslands", 5, 5, 1, 1)]
    for y in range(127):
        world.append([])
        for x in range(127):
            world[y].append(Tile.WALL.value)
    
    for y in range(127):
        for x in range(127):
            if y % 2 == 1 and x % 2 == 1:
                world[y][x] = Tile.FLOOR.value
    
    def walls_of_point(x, y):
        walls = []
        if x - 1 != 0:
            walls.append(((x - 1, y), (x - 2, y)))
        if x + 1 != 126:
            walls.append(((x + 1, y), (x + 2, y)))
        if y - 1 != 0:
            walls.append(((x, y - 1), (x, y - 2)))
        if y + 1 != 126:
            walls.append(((x, y + 1), (x, y + 2)))
        return walls
    
    points = []
    walls = []
    while True:
        x, y = (random.randint(0, 127), random.randint(0, 127))
        if x % 2 == 1 and y % 2 == 1:
            points.append((x, y))
            walls += walls_of_point(x, y)
            break
    
    while len(walls) > 0:
        idx = random.randint(0, len(walls) - 1)
        wall, neighbor = walls.pop(idx)
        if neighbor in points:
            continue
        wx, wy = wall
        world[wy][wx] = Tile.FLOOR.value
        points.append(neighbor)
        nx, ny = neighbor
        walls += walls_of_point(nx, ny)

    while True:
        x, y = (random.randint(0, 127), random.randint(0, 127))
        if x % 2 == 1 and y % 2 == 1 and x != 1 and y != 1:
            # TODO: Small random chance of generating an "end" entity that will
            # give you the flag.
            if random.randint(1, 10) == 7:
                entities.append(entity.CorrectHorseBatteryAward(x, y))
            else:
                entities.append(entity.Portal(0, "maze2" if n == 1 else "maze1", 5, 5, x, y))
            break

    return entities, world


def generate_map(description):
    world = []
    for i in range(128):
        world.append([])
        for _ in range(128):
            world[i].append(Tile.NOTHING.value)

    # Phase 1.: Bounding box

    for x in range(128):
        world[0][x]   = description["bounding-wall"].value
        world[127][x] = description["bounding-wall"].value
    for y in range(128):
        world[y][0]   = description["bounding-wall"].value
        world[y][127] = description["bounding-wall"].value

    # Phase 2.: Noise function.

    def clamp(n, low, hi):
        return max(low, min(n, hi))

    noise = PerlinNoise(octaves=32, seed=1)
    for i in range(126):
        for j in range(126):
            x = i + 1
            y = j + 1
            n = clamp(round(abs(noise([i/126, j/126]) * 6)), 0, len(description["ground"]) - 1)
            world[y][x] = description["ground"][n].value

    # Phase 3.: Generate buildings

    def rectangle_conflicts(x, y, w, h):
        for i in range(w):
            for j in range(h):
                if y + j > len(world) or x + i > len(world[y + j]):
                    return True
                if not walkable_surface(world[y + j][x + i]):
                    return True
        return False

    
    # for _ in range(random.randint(6, 9)):
    buildings_queued = random.randint(6, 9)
    while buildings_queued > 0:
        wall = random.choice(description["building-wall"]).value
        floor = random.choice(description["building-floor"]).value
        
        # TODO: Need to keep track of bounding boxes.
        x = random.randint(1, 126)
        y = random.randint(1, 126)
        w = random.randint(4, 20)
        h = random.randint(4, 20)
        if rectangle_conflicts(x, y, w, h):
            continue
        for i in range(w):
            for j in range(h):
                world[y + j][x + i] = floor

        walls = set()
        for i in range(w + 1):
            walls.add((y    , x + i))
            walls.add((y + h, x + i))
        for j in range(h):
            walls.add((y + j, x    ))
            walls.add((y + j, x + w))
        while True:
            x1, y1 = random.choice(list(walls))
            if (x1 == x and y1 == y) or (x1 == x + w and y1 == y) or (x1 == x and y1 == y + h) or (x1 == x + w and y1 == y + h):
                continue
            walls.remove((x1, y1))
            break
        for position in walls:
            y, x = position
            world[y][x] = wall
        buildings_queued -= 1

    entities = []
    environmental_queued = random.randint(30, 50)
    while environmental_queued > 0:
        x = random.randint(1, 126)
        y = random.randint(1, 126)
        if not natural_surface(world[y][x]):
            continue
        if (x, y) in [(entity.position["x"], entity.position["y"]) for entity in entities]:
            continue
        entities.append(entity.Decoration(random.choice(description["decorations"]), x, y))
        environmental_queued -= 1

    if "extra" in description:
        description["extra"](entities, world)

    return entities, world

def find_entity(entities, x, y):
    for entity in entities:
        if entity.position["x"] == x and entity.position["y"] == y:
            return entity

import math
def distance(a, b):
    x1, y1 = a
    x2, y2 = b
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def generate_grasslands(entities, world):
    while True:
        x = random.randint(1, 126)
        y = random.randint(1, 126)
        if not natural_surface(world[y][x]):
            continue
        if find_entity(entities, x, y) is not None:
            continue
        if find_entity(entities, x, y + 1) is not None:
            continue
        if distance((x, y), (4, 4)) <= 30:
            continue
        entities.append(entity.Portal(25, "desert", 4, 4, x, y))
        entities.append(entity.Sign(2, x, y + 1))
        break
    while True:
        x = random.randint(1, 126)
        y = random.randint(1, 126)
        if not natural_surface(world[y][x]):
            continue
        if find_entity(entities, x, y) is not None:
            continue
        if find_entity(entities, x, y + 1) is not None:
            continue
        if distance((x, y), (4, 4)) <= 30:
            continue
        entities.append(entity.Portal(0, "maze1", 3, 3, x, y))
        entities.append(entity.Sign(1, x, y + 1))
        break
    while True:
        x = random.randint(1, 126)
        y = random.randint(1, 126)
        if not natural_surface(world[y][x]):
            continue
        if find_entity(entities, x, y) is not None:
            continue
        if distance((x, y), (4, 4)) >= 20:
            continue
        entities.append(entity.Sign(0, x, y))
        break

    # Time for an ittle wittle iswand uwu.
    for i in range(len(world)):
        world[i] += [Tile.NOTHING.value] * 128
    for y in range(19, 32):
        for x in range(150, 190):
            world[y][x] = Tile.GRASS0.value
    for x in range(150, 190):
        world[19][x] = Tile.WALL.value
        world[31][x] = Tile.WALL.value
    for y in range(19, 32):
        world[y][150] = Tile.WALL.value
        world[y][189] = Tile.WALL.value


def generate_desert(entities, world):
    while True:
        x = random.randint(1, 126)
        y = random.randint(1, 126)
        if not natural_surface(world[y][x]):
            continue
        if find_entity(entities, x, y) is not None:
            continue
        if find_entity(entities, x, y + 1) is not None:
            continue
        if distance((x, y), (4, 4)) >= 30:
            continue
        entities.append(entity.Portal(0, "grasslands", 4, 4, x, y))
        entities.append(entity.Sign(3, x, y + 1))
        break
    while True:
        x = random.randint(1, 126)
        y = random.randint(1, 126)
        if not natural_surface(world[y][x]):
            continue
        if find_entity(entities, x, y) is not None:
            continue
        if find_entity(entities, x, y + 1) is not None:
            continue
        if distance((x, y), (4, 4)) <= 30:
            continue
        entities.append(entity.Portal(50, "snowland", 3, 3, x, y))
        entities.append(entity.Sign(4, x, y + 1))
        break


def generate_bossfight(entities, world):
    while True:
        x = random.randint(1, 126)
        y = random.randint(1, 126)
        if not natural_surface(world[y][x]):
            continue
        if find_entity(entities, x, y) is not None:
            continue
        if find_entity(entities, x, y + 1) is not None:
            continue
        if distance((x, y), (4, 4)) >= 30:
            continue
        entities.append(entity.Portal(0, "grasslands", 4, 4, x, y))
        entities.append(entity.Sign(5, x, y + 1))
        break
    while True:
        x = random.randint(1, 126)
        y = random.randint(1, 126)
        if not natural_surface(world[y][x]):
            continue
        if find_entity(entities, x, y) is not None:
            continue
        if distance((x, y), (4, 4)) >= 20:
            continue
        entities.append(entities.append(entity.Sign(6, x, y)))
        break
    while True:
        x = random.randint(1, 126)
        y = random.randint(1, 126)
        if not natural_surface(world[y][x]):
            continue
        if find_entity(entities, x, y) is not None:
            continue
        if find_entity(entities, x, y + 1) is not None:
            continue
        if distance((x, y), (4, 4)) <= 50:
            continue
        entities.append(entity.SantaClaus(x, y))

def generate_signature(blob):
    m = hashlib.md5()
    m.update(SECRET_KEY + blob)
    # m.update(SECRET_KEY)
    # m.update(blob)
    return binascii.hexlify(m.digest()).decode()


def validate_signature(signature, blob):
    m = hashlib.md5()
    m.update(SECRET_KEY + blob)
    return signature == binascii.hexlify(m.digest()).decode()


descriptions = {
    "grassland": {
        "bounding-wall": Tile.WALL,
        "ground": [Tile.GRASS0, Tile.GRASS1, Tile.GRASS2, Tile.GRASS3],
        "building-wall": [Tile.WALL],
        "building-floor": [Tile.FLOOR],
        "decorations": "🌲🌳🌿🌹🌷🌱",
        "extra": generate_grasslands,
    },
    "desert": {
        "bounding-wall": Tile.WALL,
        "ground": [Tile.SAND0, Tile.SAND1, Tile.SAND2, Tile.SAND3],
        "building-wall": [Tile.SANDSTONE_WALL],
        "building-floor": [Tile.SANDSTONE],
        "decorations": "🌾🌴🌵",
        "extra": generate_desert,
    },
    "snowland": {
        "bounding-wall": Tile.WALL,
        "ground": [Tile.ICE0, Tile.ICE1, Tile.ICE2, Tile.ICE3],
        "building-wall": [Tile.COBALT_WALL],
        "building-floor": [Tile.COBALT],
        "decorations": "❄🎄🌲",
        "extra": generate_bossfight,
    },
}


def generate_world():
    grassland_mobs, grassland_tiles = generate_map(descriptions["grassland"])
    return {
        "tilemaps": {
            "grasslands": grassland_tiles,
        },
        "mobs": {
            "grasslands": grassland_mobs,
        }
    }

import re
import urllib.parse
import zlib

def sign(world):
    blobs = []
    worldp = { "tilemaps": dict(), "mobs": dict() }
    for location in world["mobs"]:
        obj = {
            "location": location,
            "tilemap": b64encode(
                zlib.compress(
                    json.dumps(world["tilemaps"][location]).encode()
                )
            ).decode(),
            "mobs": [mob.serialize() for mob in world["mobs"][location]],
        }
        blobs.append(b64encode(json.dumps(obj).encode()))
    encoded = b" ".join(blobs)
    signature = generate_signature(encoded)
    return {
        "signature": signature,
        "blob": urllib.parse.quote(encoded.decode())
    }

def split_base64_chunks(bin):
    chunks = []
    while len(bin) > 0:
        for i in range(len(bin)):
            if bin[i] not in b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=":
                chunks.append(bin[:i])
                bin = bin[i + 1:]
                break
        else:
            break
    chunks.append(bin)
    return chunks


def validate(packet):
    try:
        packet = json.loads(packet)
        signature = packet["signature"]
        if generate_signature(urllib.parse.unquote_to_bytes(packet.get("blob"))) != signature:
            return None
        world = { "tilemaps": dict(), "mobs": dict() }
        for encoded in split_base64_chunks(urllib.parse.unquote_to_bytes(packet.get("blob"))):
            try:
                obj = json.loads(b64decode(encoded))
                world["tilemaps"][obj["location"]] = json.loads(
                    zlib.decompress(
                        b64decode(obj["tilemap"])
                    ).decode()
                )
                world["mobs"][obj["location"]] = [entity.deserialize_entity(x) for x in obj["mobs"]]
            except Exception as e:
                print(e)
                pass
        return world
    except Exception as e:
        raise e
        return None
