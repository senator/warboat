from random import choice, randint
from termcolor import colored

from ship import Orientation, generate_ships

class PlacementError(Exception): pass
class Collision(PlacementError): pass
class OffEdge(PlacementError): pass


class Cell:
    def __init__(self):
        self.ship = None
        self.hit = False

    def draw(self, draw_all_ships):
        color = None
        on_color = None
        text = '  '

        if self.hit:
            text = '◀▶' # configurable '()' or '<>' or 'CↃ' or
                        # 'CꜾ' or '▒▒' or '░░' or '◖◗'.
            if self.ship:
                color = 'red'
            else:
                color = 'white'
        if self.ship and (draw_all_ships or self.ship.has_sunk()):
            on_color = 'on_' + self.ship.color

        return colored(text, color, on_color=on_color, attrs=['bold'])


class Board(list):
    def __init__(self):
        list.__init__(self)

        self.ships = []

        # The board will be a list of 10 lists.  The inner lists represent a
        # row of spots (A-J).  The outer list orders the rows as columns
        # (labeled 1-10).
        for rowidx in range(10):
            row = []
            for colidx in range(10):
                row.append(Cell())
            self.append(row)

    def draw(self, label='<NO LABEL>', highlight_player=False,
        draw_all_ships=True, show_legend=False):

        label = '%-16s' % label
        print(colored(label, attrs=['reverse']) if highlight_player else label,
            end='')
        print('   1 2 3 4 5 6 7 8 9 10', end='')
        if show_legend:
            print('        Legend:', end='')
        print()
        for row in range(10):
            print((' ' * 17) + chr(ord('A') + row) + ' ', end='')
            for col in range(10):
                print(self[row][col].draw(draw_all_ships), end='')
            if show_legend and row - 1 < len(self.ships):
                if row == 0:
                    print('        -------', end='')
                else:
                    lship = self.ships[row - 1]
                    print('        %s (%d)' %
                        (colored(lship.name, lship.color), lship.length),
                        end='')
            print()

    def is_cell_unhit(self, loc):
        row, col = loc

        return self[row][col].hit is False

    def fire(self, loc):
        """ Return ship that was struck, or None """
        row, col = loc

        cell = self[row][col]
        cell.hit = True
        if cell.ship:
            cell.ship.register_hit()
            return cell.ship

    def add_ship(self, ship):
        if ship.orientation == Orientation.HORIZONTAL:
            row = ship.start[0]
            col_start = ship.start[1]
            col_end = ship.start[1] + ship.length
            try:
                for col in range(col_start, col_end):
                    if self[row][col].ship:
                        raise Collision
            except IndexError as e:
                raise OffEdge from e
            for col in range(col_start, col_end):
                self[row][col].ship = ship
        else:   # vertical
            col = ship.start[1]
            row_start = ship.start[0]
            row_end = ship.start[0] + ship.length
            try:
                for row in range(row_start, row_end):
                    if self[row][col].ship:
                        raise Collision
            except IndexError as e:
                raise OffEdge from e
            for row in range(row_start, row_end):
                self[row][col].ship = ship

        self.ships.append(ship) # This list is only used to draw the legend.

    def add_ships_randomly(self):
        for ship in generate_ships():
            ship.orientation = choice(
                (Orientation.HORIZONTAL, Orientation.VERTICAL))

            while True:
                try:
                    ship.start = (randint(0, 9), randint(0, 9))
                    self.add_ship(ship)
                except (Collision, OffEdge):
                    continue
                else:
                    break
