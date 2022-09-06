from random import shuffle, choice
from termcolor import colored

from battle import BattleResult
from helpers import NiceEnum, gridloc_to_str
from ship import Orientation


def _preshuffled_targets():
    targets = []

    for rowidx in range(10):
        for colidx in range(10):
            targets.append((rowidx, colidx))

    shuffle(targets)
    return targets


def _gaps_in_row(row, player_board):
    start_loc = None
    for col in range(10):
        if player_board[row][col].hit is False:
            if start_loc is None:
                start_loc = (row, col)
        elif start_loc is not None:
            yield _Gap(start_loc, (row, col - 1))
            start_loc = None

    if start_loc is not None:
        yield _Gap(start_loc, (row, col))


def _gaps_in_col(col, player_board):
    start_loc = None
    for row in range(10):
        if player_board[row][col].hit is False:
            if start_loc is None:
                start_loc = (row, col)
        elif start_loc is not None:
            yield _Gap(start_loc, (row - 1, col))
            start_loc = None

    if start_loc is not None:
        yield _Gap(start_loc, (row, col))


class _GapIterator:
    def __init__(self, gap):
        self.gap = gap
        self.offset = 0

    def __next__(self):
        if self.gap.orientation == Orientation.HORIZONTAL:
            loc = (self.gap.start_loc[0], self.gap.start_loc[1] + self.offset)
        else:
            loc = (self.gap.start_loc[0] + self.offset, self.gap.start_loc[1])

        if loc <= self.gap.end_loc:
            self.offset += 1
            return loc
        else:
            raise StopIteration


class _Gap:
    def __init__(self, start_loc, end_loc):
        assert end_loc >= start_loc

        self.start_loc = start_loc
        self.end_loc = end_loc

    def __repr__(self):
        return self.__class__.__name__ + f'(start_loc={self.start_loc},end_loc={self.end_loc})'

    @property
    def orientation(self):
        if self.start_loc[0] == self.end_loc[0]:
            return Orientation.HORIZONTAL
        else:
            return Orientation.VERTICAL

    def __iter__(self):
        return _GapIterator(self)

    def __len__(self):
        if self.orientation == Orientation.HORIZONTAL:
            return abs(self.start_loc[1] - self.end_loc[1]) + 1
        else:
            return abs(self.start_loc[0] - self.end_loc[0]) + 1

    def get_center(self):
        """ Returns the center of a gap, choosing randomly between the
        two center points if gap length is even. """

        length = len(self)

        if length % 2 == 1:
            index = length // 2
        else:
            index = choice([length // 2, length // 2 - 1])

        return list(self)[index]

    def get_intersection(self, other_gap):
        try:
            return set(self).intersection(set(other_gap)).pop()
        except KeyError:
            return None


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
            up = self._scan_up(player_board)
            down = self._scan_down(player_board)
            left = self._scan_left(player_board)
            right = self._scan_right(player_board)
            ghosts = []

            # Sometimes we can rule out one orientation or the other
            # even knowing only one hit on the ship if available space
            # in one dimension is too small.
            if len(set(up + down)) >= self.ship.length - 1:
                ghosts.append(up)
                ghosts.append(down)
            if len(set(left + right)) >= self.ship.length - 1:
                ghosts.append(left)
                ghosts.append(right)
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
        if self.targets is not None:
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
    and in columns. We choose a gap that overlaps another gap if possible,
    otherwise we just pick any gap at random.

    If we picked just one gap: we target the middle of the gap (rounding
    randomly) if gap length is less than 2 * max_boat_len. Else target
    the max_boat_len-th space from either end (choose which end randomly).
    This can save shots compared with shooting the middle of long gaps.

    If we picked a gap that overlaps another, we target their intersection.
    """

    id_ = OpponentID.CLEVER_CLAIRE
    pronoun = 'her'

    def _get_longest_boat_afloat(self, player_board):
        return max(player_board.ships,
                key=lambda ship: ship.length if not ship.has_sunk() else 0)

    def to_battlestations(self):
        self.follow_ups = []
        self.targets = None

    def _find_best_gap(self, player_board, min_gap_len): # -> Tuple[_Gap, _Gap]
        horizontal_gaps = []
        for row in range(10):
            for gap in _gaps_in_row(row, player_board):
                if len(gap) >= min_gap_len:
                    horizontal_gaps.append(gap)

        vertical_gaps = []
        for col in range(10):
            for gap in _gaps_in_col(col, player_board):
                if len(gap) >= min_gap_len:
                    vertical_gaps.append(gap)

        pairs = []
        for horiz in horizontal_gaps:
            for vert in vertical_gaps:
                if horiz.get_intersection(vert) is not None:
                    pairs.append((horiz, vert))

        if len(pairs):
            return choice(pairs)
        else:
            return (choice(horizontal_gaps + vertical_gaps), None)

    def _target_within_gap(self, gap, max_boat_len):
        gap_length = len(gap)

        if gap_length < 2 * max_boat_len:
            loc = gap.get_center()
        else:
            gap_as_list = list(gap)
            loc = choice([
                gap_as_list[max_boat_len - 1],
                gap_as_list[-max_boat_len]
            ])

        return loc

    def fire_blind(self, player_board): # -> Tuple[Tuple[int, int], Ship]
        max_boat_len = self._get_longest_boat_afloat(player_board).length
        gap, intersecting_gap = self._find_best_gap(player_board, max_boat_len)

        if intersecting_gap is None:
            print("within", gap, max_boat_len)
            loc = self._target_within_gap(gap, max_boat_len)
        else:
            print("intersection", gap, intersecting_gap)
            loc = gap.get_intersection(intersecting_gap)

        ship_struck = player_board.fire(loc)
        if ship_struck:
            self.follow_ups.append(_FollowUp(ship_struck, loc))

        return (loc, ship_struck)


def get_opponent_by_id(id_):
    return {
        OpponentID.BABY_BILLY: BabyBilly,
        OpponentID.REGULAR_ROGER: RegularRoger,
        OpponentID.CLEVER_CLAIRE: CleverClaire
    }[id_]()
