import math
import uuid

import worldgen


def distance(a, b):
    return math.sqrt((a["x"] - b["x"]) ** 2 + (a["y"] - b["y"]) ** 2)


class Entity(object):
    def __init__(self, x, y):
        self.id = str(uuid.uuid4())
        self.position = { "x": x, "y": y }

    def can_interact(self):
        """Return True iff the player can interact with this entity."""
        return True

    def interact():
        """Return a list of events arising from player interaction."""
        return [
            { "type": "message", "text": "You run into the entity." }
        ]

    def type(self):
        return self.__class__.__name__.lower()

    def serialize(self):
        return {
            "id": self.id,
            "position": self.position,
            "world_view": "❓",
            "type": self.type(),
        }


class Decoration(Entity):
    def __init__(self, view, x, y):
        super().__init__(x, y)
        self.view = view

    def can_interact(self):
        return False

    def serialize(self):
        return {
            "id": self.id,
            "position": self.position,
            "world_view": self.view,
            "type": self.type(),
        }


class Pickup(Entity):
    def __init__(self, item, x, y):
        super().__init__(x, y)
        self.item = item

    def can_interact(self):
        return False

    def serialize(self):
        base = super().serialize()
        base.update({
            "world_view": "🎁",
            "sign_id": 0
        })
        return base


class Sign(Entity):
    """A signpost that the player can read.

    This is a special kind of entity, having a packet type of its own for the
    sole purpose of enabling the `easteregg` flag.
    """
    def __init__(self, x, y):
        super().__init__(x, y)
        self.text = "This sign is a test."

    def interact(self, game_state):
        return [
            { "type": "message", "text": "You run into a sign." }
        ]

    def serialize(self):
        base = super().serialize()
        base.update({
            "world_view": "🪧",
            "sign_id": 0
        })
        return base


class Corpse(Entity):
    """A deceased enemy that the player can walk over and loot."""
    def can_interact(self):
        return False

    def serialize(self):
        base = super().serialize()
        base.update({
            "world_view": "☠️",
        })
        return base


# Code for A* gently lifted from the following article:
# <https://www.redblobgames.com/pathfinding/a-star/implementation.html>
#
# Slight modifications made, hard-coding the structure of our specific graph.

def heuristic(a, b) -> float:
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

from queue import PriorityQueue

def a_star_search(graph, start, goal):
    start = (start["x"], start["y"])
    goal  = (goal["x"], goal["y"])
    def neighbors(position):
        x, y = position
        res = []
        if worldgen.walkable_surface(graph[y - 1][x - 1]):
            res.append((x - 1, y - 1))
        if worldgen.walkable_surface(graph[y    ][x - 1]):
            res.append((x - 1, y    ))
        if worldgen.walkable_surface(graph[y + 1][x - 1]):
            res.append((x - 1, y + 1))
        if worldgen.walkable_surface(graph[y - 1][x    ]):
            res.append((x    , y - 1))
        if worldgen.walkable_surface(graph[y + 1][x    ]):
            res.append((x    , y + 1))
        if worldgen.walkable_surface(graph[y - 1][x + 1]):
            res.append((x + 1, y - 1))
        if worldgen.walkable_surface(graph[y    ][x + 1]):
            res.append((x + 1, y    ))
        if worldgen.walkable_surface(graph[y + 1][x + 1]):
            res.append((x + 1, y + 1))
        return res
    
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0
    
    while not frontier.empty():
        current = frontier.get()
        
        if current == goal:
            break
        
        for next in neighbors(current):
            new_cost = cost_so_far[current] + 1
            if new_cost >= 10:
                continue
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(next, goal)
                frontier.put(next, priority)
                came_from[next] = current

    # Walk back.
    cur = goal
    while came_from[cur] != start:
        cur = came_from[cur]
    return { "x": cur[0], "y": cur[1] }
    
    # return came_from, cost_so_far


class Enemy(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.health = 5

    def interact(self, game_state):
        self.health -= 1
        base = [
            { "type": "message", "text": f"You hit the {self.type()}." }
        ]
        if self.health == 0:
            return base + [
                { "type": "message", "text": f"The {self.type()} dies!" },
                {
                    "type": "become",
                    "id": self.id,
                    "replacement": Corpse(self.position["x"], self.position["y"])
                }
            ]
        return base

    def tick(self, game_state):
        dist = distance(self.position, game_state.position)
        if dist >= 10:
            return []
        elif dist < 2:
            return game_state.character.receive_attack(None, self)
        else:
            try:
                first_step = a_star_search(game_state.tilemap(), self.position, game_state.position)
                self.position = first_step
                return [
                    {
                        "type": "move_mob",
                        "id": self.id,
                        "new_position": first_step
                    }
                ]
            except Exception:
                return []

    def serialize(self):
        return super().serialize()


class Zombie(Enemy):
    def serialize(self):
        base = super().serialize()
        base.update({
            "world_view": "🧟",
        })
        return base
