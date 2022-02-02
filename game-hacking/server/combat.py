class Attack(object):
    def __init__(self, enemy):
        self.enemy = enemy

    def calculate_damage(self):
        return 0

    def describe(self):
        return f"The {self.enemy.type()} strikes!"


class SharpAttack(Attack):
    def calculate_damage(self):
        return self.enemy.strength

    def describe(self):
        return f"The {self.enemy.type()} slashes at you!"
