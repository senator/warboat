from helpers import NiceEnum


class ShipOrientation(NiceEnum):
    VERTICAL = 1
    HORIZONTAL = 2


class Ship:
    def __init__(self, name, length, color):
        self.name = name
        self.length = length
        self.color = color

        self.start = None
        self.orientation = None

        self._hits_remaining = length

    def register_hit(self):
        self._hits_remaining -= 1

    def has_sunk(self):
        return self._hits_remaining < 1


def generate_ships():
    return (
        Ship('Carrier', 5, 'green'),
        Ship('Battleship', 4, 'yellow'), Ship('Destroyer', 3, 'blue'),
        Ship('Submarine', 3, 'magenta'), Ship('Patrol boat', 2, 'cyan'))
