from util import *

class Attack(object):
    def __init__(self, enemy):
        self.enemy = enemy

    def calculate_damage(self):
        return 0

    def describe(self):
        return f"The {self.enemy.type()} strikes!"


class SharpAttack(Attack):
    def calculate_damage(self, player):
        characterizer = self.enemy.strength - player.constitution * 0.25
        return round(lerp(1.0, 1000.0, max(characterizer, 0) / 1000.0))

    def describe(self):
        return f"The {self.enemy.type()} slashes at you!"


class MagicAttack(Attack):
    def calculate_damage(self, player):
        characterizer = self.enemy.strength - player.intelligence * 0.5
        return round(lerp(1.0, 1000.0, max(characterizer, 0) / 1000.0))

    def describe(self):
        return f"The {self.enemy.type()} hexes you!"


class BurningAttack(Attack):
    def calculate_damage(self, player):
        characterizer = self.enemy.strength - player.strength * 0.5
        return round(lerp(1.0, 1000.0, max(characterizer, 0) / 1000.0))

    def describe(self):
        return f"The {self.enemy.type()} burns you!"


class FreezeAttack(Attack):
    def calculate_damage(self, player):
        characterizer = self.enemy.strength - player.strength * 0.5
        return round(lerp(1.0, 1000.0, max(characterizer, 0) / 1000.0))

    def describe(self):
        return f"The {self.enemy.type()} freezes you!"
