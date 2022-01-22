import math
import uuid


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
        # FIXME: This should be pathfinding.
        # FIXME: Should be 30, not 3
        dist = distance(self.position, game_state.position)
        if dist >= 30:
            return []
        elif dist < 2:
            return game_state.character.receive_attack(None, self)
        else:
            dx, dy = (0, 0)
            if self.position["x"] > game_state.position["x"]:
                dx = -1
            elif self.position["x"] < game_state.position["x"]:
                dx = 1
            if self.position["y"] > game_state.position["y"]:
                dy = -1
            elif self.position["y"] < game_state.position["y"]:
                dy = 1
            self.position["x"] += dx
            self.position["y"] += dy
            return [
                {
                    "type": "move_mob",
                    "id": self.id,
                    "new_position": self.position
                }
            ]

    def serialize(self):
        return super().serialize()


class Zombie(Enemy):
    def serialize(self):
        base = super().serialize()
        base.update({
            "world_view": "🧟",
        })
        return base
