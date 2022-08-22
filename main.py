#!/usr/bin/env python3

import re
from game import Board, Ship, Orientation, Collision, OffEdge
from prompts import PromptQuit, PromptEnum, PromptGridLoc

def main():
    print("Place ships")

    board = Board()
    ships = (
        Ship('Carrier', 5, 'green'),
        Ship('Battleship', 4, 'yellow'), Ship('Destroyer', 3, 'blue'),
        Ship('Submarine', 3, 'magenta'), Ship('Patrol boat', 2, 'cyan'))

    for ship in ships:
        board.draw()

        ship.orientation = PromptEnum(
            f'Will your {ship.name} ({ship.length} spots) be:',
            Orientation).ask()

        end = 'left' if ship.orientation == Orientation.HORIZONTAL else 'top'
        while True:
            try:
                ship.start = PromptGridLoc(
                    f'Where will its {end} end be [for ex. "A5"]').ask()

                board.add_ship(ship)
            except Collision:
                print("That overlaps another ship you've placed!")
                continue
            except OffEdge:
                print("That would stick off the edge of the map!")
                continue
            else:
                break


    print('Final configuration')
    board.draw()

if __name__ == '__main__':
    try:
        main()
    except PromptQuit:
        print('Program aborted. Goodbye!')
