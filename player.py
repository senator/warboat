from board import Board, Collision, OffEdge
from ship import generate_ships, ShipOrientation
from prompt import PromptEnum, PromptGridLoc


def configure_player_board():
    print("Place your ships")

    board = Board()
    board.draw()

    for ship in generate_ships():
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

        board.draw()

    return board
