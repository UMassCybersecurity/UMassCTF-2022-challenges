import uuid

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


    def serialize(self):
        return super().serialize()


class Zombie(Enemy):
    def serialize(self):
        base = super().serialize()
        base.update({
            "world_view": "🧟",
        })
        return base
