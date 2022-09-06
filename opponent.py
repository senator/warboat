from random import shuffle
from termcolor import colored

from battle import BattleResult
from helpers import NiceEnum, gridloc_to_str


def _preshuffled_targets():
    targets = []

    for rowidx in range(10):
        for colidx in range(10):
            targets.append((rowidx, colidx))

    shuffle(targets)
    return targets


class _FollowUp:
    def __init__(self, ship, initial_loc):
        self.ship = ship
        self.locs = [initial_loc]

    def _scan_generically(self, player_board,
            get_starting_loc_fn, get_next_loc_fn, check_edge_fn):

        working_loc = get_starting_loc_fn(self.locs)
        length_to_go = self.ship.length - 1
        scan_result = []

        while length_to_go > 0:
            working_loc = get_next_loc_fn(working_loc)
            row, col = working_loc
            length_to_go -= 1

            if check_edge_fn(working_loc):
                break

            cell = player_board[row][col]
            if cell.hit:    # Be careful only to look at a cell on the
                            # player's board iff hit is True (else we're
                            # cheating).
                if cell.ship is not self.ship:
                    # This cell is either a known miss or a known hit
                    # on another ship, so there's no more to scan in
                    # this direction
                    break
                else:
                    # Hit on same ship.  Don't end the scan, but ignore this
                    # cell.
                    continue
            else:
                scan_result.append(working_loc)

        return scan_result

    def _scan_left(self, player_board):
        return self._scan_generically(player_board,
                max, lambda loc: (loc[0], loc[1] - 1), lambda loc: loc[1] < 0)

    def _scan_right(self, player_board):
        return self._scan_generically(player_board,
                min, lambda loc: (loc[0], loc[1] + 1), lambda loc: loc[1] > 9)

    def _scan_up(self, player_board):
        return self._scan_generically(player_board,
                max, lambda loc: (loc[0] - 1, loc[1]), lambda loc: loc[0] < 0)

    def _scan_down(self, player_board):
        return self._scan_generically(player_board,
                min, lambda loc: (loc[0] + 1, loc[1]), lambda loc: loc[0] > 9)

    def add_loc(self, loc):
        self.locs.append(loc)

    def get_possibilities_nearest_first(self, player_board):
        if len(self.locs) == 1:
            # could be 4 ways
            ghosts = [self._scan_up(player_board),
                    self._scan_down(player_board),
                    self._scan_left(player_board),
                    self._scan_right(player_board)]
        else:
            # could only be 2 ways
            first, second = self.locs[:2]
            if first[0] == second[0]:   # horizontal
                ghosts = [self._scan_left(player_board),
                        self._scan_right(player_board)]
            else:                       # vertical
                ghosts = [self._scan_up(player_board),
                        self._scan_down(player_board)]

        shuffle(ghosts) # This prevents whether we go left/right/up/down
                        # from being predictable, though we do work 'out'
                        # from the first hit.

        # At this point, ghosts is a list of either two or four lists of locs.
        # We transform this 2D list to a 1D result list.  The result list
        # will have all the first elements of the original inner lists first,
        # then the second elements of all the original inner lists next, and
        # so on.
        result = []

        while any(ghosts):
            for ghost in ghosts:
                try:
                    result.append(ghost.pop(0))
                except IndexError:
                    pass

        # The final transformation is just a trick to de-dupe but keep order.
        return list(dict.fromkeys(result))


class OpponentID(NiceEnum):
    BABY_BILLY = 1
    REGULAR_ROGER = 2
    CLEVER_CLAIRE = 3


class _Opponent:
    id_ = NotImplemented
    pronoun = NotImplemented

    @property
    def nicename(self):
        return self.id_.nicename

    def to_battlestations(self):
        raise NotImplementedError

    def fire(self, player_board):   # -> (str, BattleResult)
        raise NotImplementedError

    def communicate_firing_result(self, loc, ship_struck, player_board):
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

            if all([ship.has_sunk() for ship in player_board.ships]):
                battle_result = BattleResult.OPPONENT_WINS

            return (msg, battle_result)


class BabyBilly(_Opponent):
    """ Only fires at random. Simplest opponent implementation. """

    id_ = OpponentID.BABY_BILLY
    pronoun = 'his'

    def to_battlestations(self):
        self.targets = _preshuffled_targets()

    def fire(self, player_board):
        loc = self.targets.pop()
        ship_struck = player_board.fire(loc)

        return self.communicate_firing_result(loc, ship_struck, player_board)


class _Chaser:
    """ A mix-in for Roger and Claire, with the logic for chasing/following
    up when the opponent finds the player's ships in a missile strike. """

    def fire_blind(self, player_board):
        raise NotImplementedError

    def fire(self, player_board):
        t = self.keep_chasing(player_board) or \
            self.fire_blind(player_board)
        loc, ship_struck = t

        return self.communicate_firing_result(loc, ship_struck, player_board)

    def keep_chasing(self, player_board):   # -> Tuple[Tuple[int, int], Ship]
        try:
            follow_up = self.follow_ups[0]
        except IndexError:
            return None

        # The following method call should never return an empty list.
        loc = follow_up.get_possibilities_nearest_first(player_board)[0]

        # Remove `loc`from the pre-generated random `targets` list, so
        # we don't try it again later.
        self.targets.remove(loc)

        ship_struck = player_board.fire(loc)

        if ship_struck is follow_up.ship:
            if ship_struck.has_sunk():
                self.follow_ups.remove(follow_up)
            else:
                follow_up.add_loc(loc)
        elif ship_struck is not None:
            self.follow_ups.append(_FollowUp(ship_struck, loc))

        return (loc, ship_struck)


class RegularRoger(_Chaser, _Opponent):
    """ Medium-difficulty opponent. Fires randomly until hit, then chases. """

    id_ = OpponentID.REGULAR_ROGER
    pronoun = 'his'

    def to_battlestations(self):
        self.targets = _preshuffled_targets()
        self.follow_ups = []

    def fire_blind(self, player_board): # -> Tuple[Tuple[int, int], Ship]
        loc = self.targets.pop()
        ship_struck = player_board.fire(loc)

        if ship_struck:
            self.follow_ups.append(_FollowUp(ship_struck, loc))

        return (loc, ship_struck)


class CleverClaire(_Chaser, _Opponent):
    """ High-difficulty opponent.  Fires in pattern until hit, then chases.

    Specifically, if we have nothing to chase yet, we start like so:

    We get the length of the longest player ship we haven't struck so far.
    We call this value `max_boat_len`.

    Then we build a list of all gaps of at least max_boat_len, in rows
    and in columns (which overlap, but it doesn't matter) and sorting
    them by length.  We choose the longest gap in the result list,
    breaking ties randomly.

    (XXX would it not be better to pick targets that would hit multiple gaps?)

    Target the middle of the gap (rounding randomly) if gap length is less
    than 2 * max_boat_len.  Else target the max_boat_len-th space from either
    end (choose which end randomly).

    """

    id_ = OpponentID.CLEVER_CLAIRE
    pronoun = 'her'

    def to_battlestations(self):
        pass

    def fire_blind(self, player_board): # -> Tuple[Tuple[int, int], Ship]
        target_len = self._


def get_opponent_by_id(id_):
    return {
        OpponentID.BABY_BILLY: BabyBilly,
        OpponentID.REGULAR_ROGER: RegularRoger,
        OpponentID.CLEVER_CLAIRE: CleverClaire
    }[id_]()
