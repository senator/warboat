from random import shuffle
from termcolor import colored

from battle import BattleResult
from helpers import NiceEnum, gridloc_to_str


class OpponentID(NiceEnum):
    BABY_BILLY = 1
    REGULAR_ROGER = 2
    CLEVER_CLAIRE = 3


class Opponent:
    id_ = NotImplemented
    pronoun = NotImplemented

    @property
    def nicename(self):
        return self.id_.nicename

    def to_battlestations(self):
        raise NotImplementedError

    def fire(self, player_board):   # -> (str, BattleResult)
        raise NotImplementedError

    def _communicate_firing_result(self, loc, ship_struck):
        battle_result = None

        if ship_struck is None:
            return (f'{self.nicename} missed at {gridloc_to_str(loc)}.',
                battle_result)
        elif not ship_struck.has_sunk():
            return (f"{self.nicename} hit your " +
                colored(ship_struck.name, ship_struck.color, attrs=["reverse"]) +
                f" at {gridloc_to_str(loc)}.", battle_result)
        else:
            msg = f'{self.nicename} ' + \
                colored('SANK', 'white', attrs=["bold"]) + \
                f' your ' + \
                colored(ship_struck.name, ship_struck.color,
                    attrs=["reverse"]) + \
                f' at {gridloc_to_str(loc)}.'

            if all([ship.has_sunk() for ship in board.ships]):
                battle_result = BattleResult.OPPONENT_WINS

            return (msg, battle_result)


class BabyBilly(Opponent):
    id_ = OpponentID.BABY_BILLY
    pronoun = 'his'

    def to_battlestations(self):
        self.targets = []
        for rowidx in range(10):
            for colidx in range(10):
                self.targets.append((rowidx, colidx))

        shuffle(self.targets)

    def fire(self, player_board):
        loc = self.targets.pop()
        ship_struck = player_board.fire(loc)

        return self._communicate_firing_result(loc, ship_struck)


class RegularRoger(Opponent):
    id_ = OpponentID.REGULAR_ROGER
    pronoun = 'his'

#    def fire(self, player_board):
#        pass


class CleverClaire(Opponent):
    id_ = OpponentID.CLEVER_CLAIRE
    pronoun = 'her'

#    def fire(self, player_board):
#        pass


def get_opponent_by_id(id_):
    return {
        OpponentID.BABY_BILLY: BabyBilly,
        OpponentID.REGULAR_ROGER: RegularRoger,
        OpponentID.CLEVER_CLAIRE: CleverClaire
    }[id_]()
