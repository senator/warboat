from helpers import NiceEnum


class OpponentID(NiceEnum):
    BABY_BILLY = 1
    REGULAR_ROGER = 2
    CLEVER_CLAIRE = 3


class Opponent:
    id = NotImplemented

    @property
    def nicename(self):
        return self.id_.nicename

    def play_a_turn(self, own_board, player_board):
        raise NotImplementedError


class BabyBilly(Opponent):
    id_ = OpponentID.BABY_BILLY

    def play_a_turn(self, own_board, player_board):
        print('XXX wee billygoat takes a turn') # TODO


class RegularRoger(Opponent):
    id_ = OpponentID.REGULAR_ROGER

    def play_a_turn(self, own_board, player_board):
        print('XXX right, Roger takes a turn') # TODO


class CleverClaire(Opponent):
    id_ = OpponentID.CLEVER_CLAIRE

    def play_a_turn(self, own_board, player_board):
        print('XXX clever Claire takes a classy turn') # TODO


def get_opponent_by_id(id_):
    return {
        OpponentID.BABY_BILLY: BabyBilly,
        OpponentID.REGULAR_ROGER: RegularRoger,
        OpponentID.CLEVER_CLAIRE: CleverClaire
    }[id_]()
