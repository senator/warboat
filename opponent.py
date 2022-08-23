from random import choice, randint

from board import Board, Collision, OffEdge
from ship import generate_ships, ShipOrientation
from prompt import PromptEnum, PromptGridLoc


def configure_opponent_board():
    """ Make board w/ ships randomly placed for computer-controlled opponent """

    print("Hang on while we generate the opponent's board...")

    board = Board()

    for ship in generate_ships():
        ship.orientation = choice(
            (ShipOrientation.HORIZONTAL, ShipOrientation.VERTICAL))

        while True:
            try:
                ship.start = (randint(0, 9), randint(0, 9))
                board.add_ship(ship)
            except (Collision, OffEdge):
                continue
            else:
                break

    return board
