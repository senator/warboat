from time import sleep

from helpers import NiceEnum


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

    def fire(self, player_board):
        # XXX once subclasses are done, replace the following with
        # raise NotImplementedError
        sleep(2)
        return ('Nothing specific happened.', None)


class BabyBilly(Opponent):
    id_ = OpponentID.BABY_BILLY
    pronoun = 'his'

#    def fire(self, player_board):
#        pass


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
