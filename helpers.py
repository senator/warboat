from enum import Enum


class NiceEnum(Enum):
    @property
    def nicename(self):
        return self.name.title().replace('_', ' ')
