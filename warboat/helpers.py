from enum import Enum


class NiceEnum(Enum):
    @property
    def nicename(self):
        return self.name.title().replace('_', ' ')


def gridloc_to_str(loc):
    row, col = loc

    return chr(ord('A') + row) + str(col + 1)
