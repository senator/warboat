#!/usr/bin/env python3

import re
from board import Board, Collision, OffEdge
from ship import generate_ships, ShipOrientation
from prompt import PromptQuit, PromptEnum, PromptGridLoc

def main():
    print("Place ships")

    board = Board()

    for ship in generate_ships():
        board.draw()

        ship.orientation = PromptEnum(
            f'Will your {ship.name} ({ship.length} spots) be:',
            ShipOrientation).ask()

        if ship.orientation == ShipOrientation.HORIZONTAL:
            end = 'left'
        else:
            end = 'top'

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
