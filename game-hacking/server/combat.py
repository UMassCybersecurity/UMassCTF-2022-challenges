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
        print("Debug: {}".format(round(lerp(1.0, 10000.0, max(characterizer, 0) / 1000.0))))
        return round(lerp(1.0, 1000.0, max(characterizer, 0) / 1000.0))

    def describe(self):
        return f"The {self.enemy.type()} slashes at you!"
