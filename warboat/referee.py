from helpers import NiceEnum


class Turn(NiceEnum):
    PLAYER = 0
    OPPONENT = 1


class Referee:
    def __init__(self):
        # XXX TODO options about choosing start condition
        self._current_turn = 0

    def turn(self):
        """ Return current turn, alternating for every call """
        result = Turn(self._current_turn)
        self._current_turn ^= 1

        return result
