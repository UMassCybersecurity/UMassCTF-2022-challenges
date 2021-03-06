from util import *

import copy
import json
import math
import random
import uuid

import combat
import inventory
import worldgen

def deserialize_entity(blob):
    mapping = {
        "projectile": Projectile,
        "itemprojectile": ItemProjectile,
        "pickup": Pickup,
        "decoration": Decoration,
        "sign": Sign,
        "corpse": Corpse,
        "zombie": Zombie,
        "magicman": MagicMan,
        "woodlandmonster": WoodlandMonster,
        "madsun": MadSun,
        "volcano": Volcano,
        "sentientstatue": SentientStatue,
        "gman": Gman,
        "snowboi": Snowboi,
        "pingu": Pingu,
        "santaclaus": SantaClaus,
        "portal": Portal,
        "correcthorsebatteryaward": CorrectHorseBatteryAward
    }
    return mapping[blob["type"]].deserialize(blob)


class Entity(object):
    def __init__(self, x, y):
        self.id = str(uuid.uuid4())
        self.position = { "x": x, "y": y }

    def construct_empty():
        return Entity(0, 0)

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

    @classmethod
    def deserialize(cls, blob):
        e = cls.construct_empty()
        for (field, value) in blob.items():
            if hasattr(e, field) and field != "type":
                e.__setattr__(field, value)
        return e


class Projectile(Entity):
    def __init__(self, target_x, target_y, damage, view, x, y):
        super().__init__(x, y)
        self.world_view = view
        self.target_x = target_x
        self.target_y = target_y
        self.damage = damage

    def construct_empty():
        return Projectile(0, 0, 0, ' ', 0, 0)

    def can_interact(self):
        return False

    def tick(self, game_state):
        max_steps = 10
        # angle = math.atan((self.target_y - self.y) / (self.target_x - self.x))
        azimuth_dx = (self.target_x - self.position["x"])
        azimuth_dy = (self.target_y - self.position["y"])
        normalizer = max(abs(azimuth_dx), abs(azimuth_dy))
        if normalizer > 1:
            azimuth_dx /= normalizer
            azimuth_dy /= normalizer
        base = [
            { "type": "new_mob", "entity": self.serialize() }
        ]
        while max_steps > 0:
            projected_x = round(self.position["x"] + azimuth_dx)
            projected_y = round(self.position["y"] + azimuth_dy)
            if not worldgen.walkable_surface(game_state.tilemap()[projected_y][projected_x]):
                break
            elif game_state.find_entity(projected_x, projected_y):
                ent = game_state.find_entity(projected_x, projected_y)
                if ent.can_interact():
                    base += ent.interact(game_state)
                break
            elif game_state.position["x"] == projected_x and \
                 game_state.position["y"] == projected_y:
                base += game_state.character.receive_projectile_damage(self.damage)
            self.position["x"] = projected_x
            self.position["y"] = projected_y
            base.append({
                "type": "move_mob_animate",
                "id": self.id,
                "new_position": dict(self.position),
            })
            max_steps -= 1
        base.append({ "type": "delete_mob", "id": self.id })
        game_state.delete_mob(self.id)
        return base
    # TODO: Need to process resultant effects

    def serialize(self):
        base = super().serialize()
        base.update({
            "world_view": self.world_view,
        })
        return base


class ItemProjectile(Projectile):
    def __init__(self, target_x, target_y, damage, item, x, y):
        super().__init__(target_x, target_y, damage, item.icon(), x, y)
        self.item = item

    def tick(self, game_state):
        events = super().tick(game_state)
        old_x = None
        old_y = None
        for event in events:
            if event["type"] == "move_mob_animate":
                old_x = event["new_position"]["x"]
                old_y = event["new_position"]["y"]
            elif event["type"] == "delete_mob" and old_x is not None and old_y is not None:
                x, y = game_state.find_free_space(old_x, old_y)
                pickup = Pickup(self.item, x, y)
                game_state.mobs().append(pickup)
                events.append({ "type": "new_mob", "entity": pickup.serialize() })
        return events


class Decoration(Entity):
    def __init__(self, view, x, y):
        super().__init__(x, y)
        self.world_view = view

    def construct_empty():
        return Decoration(' ', 0, 0)

    def can_interact(self):
        return False

    def serialize(self):
        base = super().serialize()
        base.update({
            "world_view": self.world_view,
        })
        return base


class Pickup(Entity):
    def __init__(self, item, x, y):
        super().__init__(x, y)
        self.item = item

    def construct_empty():
        return Pickup(None, 0, 0)

    def can_interact(self):
        return False

    def serialize(self):
        base = super().serialize()
        base.update({
            "world_view": "🎁",
            "item": self.item.serialize() if self.item else None
        })
        return base

    @classmethod
    def deserialize(cls, blob):
        e = cls.construct_empty()
        for (field, value) in blob.items():
            if field == "item" and value is not None:
                e.item = inventory.deserialize(value)
            elif hasattr(e, field) and field != "type":
                e.__setattr__(field, value)
        return e


class Sign(Entity):
    """A signpost that the player can read.

    This is a special kind of entity, having a packet type of its own for the
    sole purpose of enabling the `easteregg` flag.
    """
    def __init__(self, idx, x, y):
        super().__init__(x, y)
        self.idx = idx

    def construct_empty():
        return Sign(0, 0, 0)

    def interact(self, game_state):
        return [
            { "type": "message", "text": "You run into a sign." }
        ]

    def serialize(self):
        base = super().serialize()
        base.update({
            "world_view": "🪧",
            "sign_id": self.idx
        })
        return base


class Corpse(Entity):
    """A deceased enemy that the player can walk over and loot."""
    def construct_empty():
        return Corpse(0, 0)

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

def pre_process_tilemap(game_state, graph):
    for mob in game_state.mobs():
        graph[mob.position["y"]][mob.position["x"]] = worldgen.Tile.NOTHING.value

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
        self.agility = 0
        self.experience = 5
        self.strength = 1
        self.accuracy = 1
        self.drop = [inventory.Bandaid()]
        self.lock = False
        self.attack_type = combat.SharpAttack

    def construct_empty():
        return Enemy(0, 0)

    def interact(self, game_state):
        self.health -= game_state.character.attack_value(self)
        base = [
            { "type": "message", "text": f"You hit the {self.type()}." }
        ]
        if self.health <= 0:
            base += [
                { "type": "message", "text": f"The {self.type()} disappears!" },
                { "type": "player_experience", "value": self.experience },
                {
                    "type": "become",
                    "id": self.id,
                    "replacement": Corpse(self.position["x"], self.position["y"])
                }
            ]
            if random.choice([1, 2]) == 1 and len(self.drop) > 0:
                x, y = game_state.find_free_space(self.position["x"], self.position["y"])
                item = random.choice(self.drop)
                pickup = Pickup(item, x, y)
                game_state.mobs().append(pickup)
                base.append({ "type": "new_mob", "entity": pickup.serialize()})
        return base

    def tick(self, game_state):
        if self.lock:
            return []
        dist = distance(self.position, game_state.position)
        if dist >= 10:
            return []
        elif dist < 2:
            if random.randint(1, round(lerp(10, 1, self.accuracy / 100.0))) == 1:
                return game_state.character.receive_attack(self.attack_type(self))
            else:
                return [{ "type": "message", "text": f"The {self.type()} misses!" }]
        else:
            try:
                graph = copy.deepcopy(game_state.tilemap())
                pre_process_tilemap(game_state, graph)
                first_step = a_star_search(graph, self.position, game_state.position)
                return [
                    {
                        "type": "move_mob",
                        "id": self.id,
                        "new_position": first_step,
                        "tu": lerp(64, 4, self.agility / 10.0)
                    }
                ]
            except Exception:
                return []

    def serialize(self):
        base = super().serialize()
        base.update({
            "world_view": "🎁",
            "health": self.health,
            "experience": self.experience,
            "strength": self.strength,
            "agility": self.agility,
            "accuracy": self.accuracy,
            "drop": [x.serialize() for x in self.drop]
        })
        return base

    @classmethod
    def deserialize(cls, blob):
        e = cls.construct_empty()
        for (field, value) in blob.items():
            if field == "drop" and value is not None:
                e.drop = []
                for item in value:
                    e.drop.append(inventory.deserialize(item))
            elif hasattr(e, field) and field != "type":
                e.__setattr__(field, value)
        return e



class ThrowingEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.projectile = '🧱'

    def construct_empty():
        return ThrowingEnemy(0, 0)

    def tick(self, game_state):
        dist = distance(self.position, game_state.position)
        if dist >= 10:
            return []
        elif dist < 2:
            return game_state.character.receive_attack(self.attack_type(self))
        else:
            try:
                if random.choice([1, 2]) == 1:
                    start_x_offset = 0
                    start_y_offset = 0
                    if game_state.position["x"] > self.position["x"]:
                        start_x_offset = 1
                    elif game_state.position["x"] < self.position["x"]:
                        start_x_offset = -1
                    if game_state.position["y"] > self.position["y"]:
                        start_y_offset = 1
                    elif game_state.position["y"] < self.position["y"]:
                        start_y_offset = -1
                    game_state.mobs().append(Projectile(
                        game_state.position["x"],
                        game_state.position["y"],
                        1,
                        self.projectile,
                        self.position["x"] + start_x_offset,
                        self.position["y"] + start_y_offset
                    ))
                    return []
                graph = copy.deepcopy(game_state.tilemap())
                pre_process_tilemap(game_state, graph)
                first_step = a_star_search(graph, self.position, game_state.position)
                return [
                    {
                        "type": "move_mob",
                        "id": self.id,
                        "new_position": first_step,
                        "tu": lerp(64, 4, self.agility / 10.0)
                    }
                ]
            except Exception as e:
                print("Exception encountered, but dropped: {}".format(e))
                return []


class Zombie(Enemy):
    def construct_empty():
        return Zombie(0, 0)

    def serialize(self):
        base = super().serialize()
        base.update({
            "world_view": "🧟",
        })
        return base


class MagicMan(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.attack_type = combat.MagicAttack
        self.agility = 1
        self.experience = 10

    def construct_empty():
        return MagicMan(0, 0)

    def serialize(self):
        base = super().serialize()
        base.update({
            "world_view": "🧞",
        })
        return base


class WoodlandMonster(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.attack_type = combat.MagicAttack
        self.strength = 2
        self.experience = 10

    def construct_empty():
        return WoodlandMonster(0, 0)

    def serialize(self):
        base = super().serialize()
        base.update({
            "world_view": "👹",
        })
        return base

class MadSun(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.attack_type = combat.BurningAttack
        self.strength = 2
        self.accuracy = 20
        self.agility = 3
        self.experience = 30

    def construct_empty():
        return MadSun(0, 0)

    def serialize(self):
        base = super().serialize()
        base.update({
            "world_view": "🌞",
        })
        return base


class Volcano(ThrowingEnemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.attack_type = combat.BurningAttack
        self.health = 10
        self.accuracy = 10
        self.experience = 50

    def construct_empty():
        return Volcano(0, 0)

    def __init__(self, x, y):
        super().__init__(x, y)
        self.projectile = '🪨'

    def serialize(self):
        base = super().serialize()
        base.update({
            "world_view": "🌋",
        })
        return base


class SentientStatue(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.attack_type = combat.BurningAttack
        self.health = 20
        self.accuracy = 30
        self.experience = 70

    def construct_empty():
        return SentientStatue(0, 0)

    def serialize(self):
        base = super().serialize()
        base.update({
            "world_view": "🗿",
        })
        return base


class Gman(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.attack_type = combat.MagicAttack
        self.health = 20
        self.accuracy = 50
        self.agility = 3
        self.experience = 150

    def construct_empty():
        return Gman(0, 0)

    def serialize(self):
        base = super().serialize()
        base.update({
            "world_view": "🕴️",
        })
        return base


class Snowboi(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.attack_type = combat.FreezeAttack
        self.accuracy = 50
        self.strength = 100
        self.agility = 3
        self.experience = 300

    def construct_empty():
        return Snowboi(0, 0)

    def serialize(self):
        base = super().serialize()
        base.update({
            "world_view": "☃️",
        })
        return base


class Pingu(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.attack_type = combat.FreezeAttack
        self.health = 100
        self.accuracy = 50
        self.strength = 100
        self.agility = 5
        self.experience = 500

    def construct_empty():
        return Pingu(0, 0)

    def serialize(self):
        base = super().serialize()
        base.update({
            "world_view": "🐧",
        })
        return base


class SantaClaus(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.health = 9999
        self.experience = 9999
        self.agility = 10
        self.strength = 100
        self.accuracy = 80

    def construct_empty():
        return SantaClaus(0, 0)

    def serialize(self):
        base = super().serialize()
        base.update({
            "world_view": "🎅",
        })
        return base

    def interact(self, game_state):
        self.health -= 1
        base = [
            { "type": "message", "text": f"You hit the {self.type()}." }
        ]
        if self.health <= 0:
            base += [
                { "type": "message", "text": f"The {self.type()} dies!" },
                { "type": "message", "text": "Congratulations! Flag is UMASS{n1c3_901N_j3rk_N0w_Y0U_RU1n3D_CHr157m42}" },
                {
                    "type": "become",
                    "id": self.id,
                    "replacement": Corpse(self.position["x"], self.position["y"])
                }
            ]
            if random.choice([1, 2]) == 1 and len(self.drop) > 0:
                x, y = game_state.find_free_space(self.position["x"], self.position["y"])
                item = random.choice(self.drop)()
                pickup = Pickup(item, x, y)
                game_state.mobs().append(pickup)
                base.append({ "type": "new_mob", "entity": pickup.serialize()})
        return base



class Portal(Entity):
    def __init__(self, minimum_level, target_world, target_x, target_y, x, y):
        super().__init__(x, y)
        self.minimum_level = minimum_level
        self.target_world = target_world
        self.target_x = target_x
        self.target_y = target_y

    def construct_empty():
        return Portal(0, "grasslands", 0, 0, 0, 0)

    def interact(self, game_state):
        if game_state.character.level < self.minimum_level:
            return [
                { "type": "message", "text": f"You are too weak! You need at least level {self.minimum_level}..." },
            ]
        return [
            { "type": "message", "text": "You enter the wormhole..." },
            {
                "type": "teleport_player",
                "target_x": self.target_x,
                "target_y": self.target_y,
                "target_world": self.target_world
            }
        ]

    def serialize(self):
        base = super().serialize()
        base.update({
            "world_view": "🕳️",
            "minimum_level": self.minimum_level,
            "target_world": self.target_world,
            "target_x": self.target_x,
            "target_y": self.target_y
        })
        return base


class CorrectHorseBatteryAward(Entity):
    def construct_empty():
        return CorrectHorseBatteryAward(0, 0)

    def interact(self, game_state):
        return [
            { "type": "message", "text": "Congratulations! Flag is UMASS{84d_m3mOR135_OF_l457_Y34R_H4h4H4H4}" },
            {
                "type": "teleport_player",
                "target_x": 1,
                "target_y": 1,
                "target_world": "grasslands"
            }
        ]

    def serialize(self):
        base = super().serialize()
        base.update({
            "world_view": "🏆",
        })
        return base


world_associations = {
    "grasslands": [Zombie, MagicMan, WoodlandMonster],
    "desert": [MadSun, Volcano, SentientStatue],
    "snowland": [Gman, Snowboi, Pingu],
}
