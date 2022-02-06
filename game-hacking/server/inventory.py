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
    def consume(self):
        return [
            { "type": "message", "text": f"You consume the {self.type()}" }
        ]


# How do we model the player slots; temporary additions that will be changed by unequipping?
class Weapon(Item):
    pass


class Umbrella(Weapon):
    def icon(self):
        return "🌂"


class Purse(Weapon):
    def icon(self):
        return "👝"

class Torch(Weapon):
    def icon(self):
        return "🪔"

class Axe(Weapon):
    def icon(self):
        return "🪓"

class Raygun(Weapon):
    def icon(self):
        return "📡"

class Bandaid(Consumable):
    def icon(self):
        return "🩹"

class Fentanyl(Consumable):
    def icon(self):
        return "💊"

class BudLite(Consumable):
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
