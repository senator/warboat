from termcolor import colored

from ship import ShipOrientation

class PlacementError(Exception): pass
class Collision(PlacementError): pass
class OffEdge(PlacementError): pass


class Board(list):
    def __init__(self, blank_value=None):
        list.__init__(self)

        self.ships = []

        # The board will be a list of 10 lists.  The inner lists represent a
        # row of spots (A-J).  The outer list orders the rows as columns
        # (labeled 1-10).
        for i in range(10):
            self.append([blank_value, ] * 10)

    def draw(self, label='<NO LABEL>', highlight_player=False, draw_ships=True):
        label = '%-16s' % label
        print(
            colored(label, attrs=['reverse']) if highlight_player else label,
            end='')
        print('   1 2 3 4 5 6 7 8 9 10')
        for row in range(10):
            print((' ' * 17) + chr(ord('A') + row) + ' ', end='')
            for col in range(10):
                ship = self[row][col]
                if ship is None or (not draw_ships): # XXX TODO still draw hits
                    s = '  '
                else:
                    s = colored('  ', on_color='on_' + ship.color)
                print(s, end='')
            print('')


    def add_ship(self, ship):
        if ship.orientation == ShipOrientation.HORIZONTAL:
            row = ship.start[0]
            col_start = ship.start[1]
            col_end = ship.start[1] + ship.length
            try:
                for col in range(col_start, col_end):
                    if self[row][col]:
                        raise Collision
            except IndexError as e:
                raise OffEdge from e
            for col in range(col_start, col_end):
                self[row][col] = ship
        else:   # vertical
            col = ship.start[1]
            row_start = ship.start[0]
            row_end = ship.start[0] + ship.length
            try:
                for row in range(row_start, row_end):
                    if self[row][col]:
                        raise Collision
            except IndexError as e:
                raise OffEdge from e
            for row in range(row_start, row_end):
                self[row][col] = ship
