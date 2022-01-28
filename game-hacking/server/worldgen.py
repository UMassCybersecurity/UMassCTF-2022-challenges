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
    


SECRET_KEY = b"1f_y0u'r3_r34d1ng_7h15,_1_h0p3_17'5_b3c4u53_y0u_unr0113d_MD5,_n07_b3c4u53_y0u_g07_RCE_0n_7h3_53rv3r"

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
        Tile.SANDSTONE
    ])


def natural_surface(surf):
    return surf in map(lambda x: x.value, [
        Tile.GRASS0, Tile.GRASS1, Tile.GRASS2, Tile.GRASS3,
        Tile.SAND0, Tile.SAND1, Tile.SAND2, Tile.SAND3
    ])


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

    entities = [entity.Sign(5, 5), entity.Zombie(4, 4), entity.Pickup(inventory.Bandaid(), 3, 4), entity.Portal("desert", 4, 4, 8, 8)]
    environmental_queued = random.randint(30, 50)
    while environmental_queued > 0:
        x = random.randint(1, 126)
        y = random.randint(1, 126)
        if not natural_surface(world[y][x]):
            continue
        entities.append(entity.Decoration(random.choice(description["decorations"]), x, y))
        environmental_queued -= 1

    return entities, world


def generate_signature(blob):
    m = hashlib.md5()
    m.update(SECRET_KEY)
    m.update(blob)
    return binascii.hexlify(m.digest()).decode()


def validate_signature(signature, blob):
    m = hashlib.md5()
    m.update(SECRET_KEY)
    m.update(blob)
    return signature == binascii.hexlify(m.digest()).decode()


def generate_world():
    grassland_mobs, grassland_tiles = generate_map({
        "bounding-wall": Tile.WALL,
        "ground": [Tile.GRASS0, Tile.GRASS1, Tile.GRASS2, Tile.GRASS3],
        "building-wall": [Tile.WALL],
        "building-floor": [Tile.FLOOR],
        "decorations": "🌲🌳🌿🌹🌷🌱"
    })
    desert_mobs, desert_tiles = generate_map({
        "bounding-wall": Tile.WALL,
        "ground": [Tile.SAND0, Tile.SAND1, Tile.SAND2, Tile.SAND3],
        "building-wall": [Tile.SANDSTONE_WALL],
        "building-floor": [Tile.SANDSTONE],
        "decorations": "🌾🌴🌵"
    })
    return {
        "tilemaps": {
            "grasslands": grassland_tiles,
            "desert": desert_tiles,
            # "snowland"
        },
        "mobs": {
            "grasslands": grassland_mobs,
            "desert": desert_mobs,
            # "snowland"
        }
    }


def sign(world):
    world = {
        "tilemaps": world["tilemaps"],
        "mobs": {
            "grasslands": [mob.serialize() for mob in world["mobs"]["grasslands"]],
            "desert": [mob.serialize() for mob in world["mobs"]["desert"]],
            # "snowland"
        }
    }
    encoded = b64encode(json.dumps(world).encode())
    signature = generate_signature(encoded)
    return {
        "signature": signature,
        "blob": encoded.decode()
    }
