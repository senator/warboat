from board import Board, Collision, OffEdge
from ship import generate_ships, ShipOrientation
from prompt import PromptEnum, PromptGridLoc, PromptDict


def configure_player_board():
    board = Board()
    board.draw()

    use_auto = PromptDict(
        'Do you want to place your ships...', {
            1: 'Automatically',
            2: 'Manually'}).ask()

    if use_auto == 1:
        board.add_ships_randomly()
    else:
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
