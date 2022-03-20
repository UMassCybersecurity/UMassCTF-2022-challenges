import uuid

class Item(object):
    def __init__(self, id=None):
        if id is None:
            self.id = str(uuid.uuid4())
        else:
            self.id = id

    def type(self):
        return self.__class__.__name__.lower()

    def classes(self):
        return [x.__name__.lower() for x in self.__class__.__bases__]

    def icon(self):
        return "❓"

    def inventoryView(self):
        return f"{self.icon()} {self.type()} ({'; '.join(self.classes())})"

    def serialize(self):
        return {
            "id": self.id,
            "type": self.type(),
            "inventory_view": self.inventoryView()
        }


# How do we model temporary effects?
class Usable(Item):
    def consume(self):
        return [
            { "type": "message", "text": f"You use the {self.type()}" }
        ]


# How do we model temporary effects?
class Consumable(Item):
    def __init__(self, id=None):
        super().__init__(id)
        self.max_health = 0
        self.health = 0
        self.strength = 0
        self.constitution = 0
        self.intelligence = 0
        self.initiative = 0

    def consume(self):
        return [
            { "type": "message", "text": f"You consume the {self.type()}" }
        ]


class Equippable(Item):
    def __init__(self, id=None):
        super().__init__(id)
        self.max_health = 0
        self.health = 0
        self.strength = 0
        self.constitution = 0
        self.intelligence = 0
        self.intelligence_bonus = 0
        self.initiative = 0


class Umbrella(Equippable):
    def __init__(self, id=None):
        super().__init__(id)
        self.strength = 4
        self.constitution = 1

    def icon(self):
        return "🌂"


class Purse(Equippable):
    def __init__(self, id=None):
        super().__init__(id)
        self.constitution = 3
        self.max_health = 1

    def icon(self):
        return "👝"

class Torch(Equippable):
    def __init__(self, id=None):
        super().__init__(id)
        self.strength = 5

    def icon(self):
        return "🪔"

class Axe(Equippable):
    def __init__(self, id=None):
        super().__init__(id)
        self.strength = 5

    def icon(self):
        return "🪓"

class Raygun(Equippable):
    def __init__(self, id=None):
        super().__init__(id)
        self.strength = 3
        self.intelligence = 3

    def icon(self):
        return "📡"

class Bandaid(Consumable):
    def __init__(self, id=None):
        super().__init__(id)
        self.health = 3

    def icon(self):
        return "🩹"

class Fentanyl(Consumable):
    def __init__(self, id=None):
        super().__init__(id)
        self.health = 5

    def icon(self):
        return "💊"

class BudLite(Consumable):
    def __init__(self, id=None):
        super().__init__(id)
        self.health = 2

    def icon(self):
        return "🍺"

class Guitar(Usable):
    def icon(self):
        return "🎸"

class Banjo(Usable):
    def icon(self):
        return "🪕"

class Aphrodisiac(Consumable):
    def icon(self):
        return "💋"


def deserialize(serialized):
    jump_table = {
        "umbrella": Umbrella,
        "purse": Purse,
        "torch": Torch,
        "axe": Axe,
        "raygun": Raygun,
        "bandaid": Bandaid,
        "fentanyl": Fentanyl,
        "budlite": BudLite,
        "guitar": Guitar,
        "banjo": Banjo,
        "aphrodisiac": Aphrodisiac,
    }
    if "type" in serialized and serialized["type"] in jump_table:
        if "id" in serialized:
            return jump_table[serialized["type"]](serialized["id"])
        return jump_table[serialized["type"]]()
