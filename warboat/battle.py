import sys
from time import sleep
from random import choice
from termcolor import colored

from helpers import NiceEnum, gridloc_to_str
from prompt import PromptGridLoc, PromptAlternate, enter_to_continue
from referee import Turn


jibes = (
    'Your cowardice is unbecoming.',
    'Fine, be a quitter then.',
    'What, have somewhere better to be?',
    'Live to fight another day, eh?',
    "Couldn't take the heat?",
    'Okay, run home to Momma.',
    'Outta here? See if I care!'
)


class BattleResult(NiceEnum):
    PLAYER_WINS = 1
    OPPONENT_WINS = 2


def fire(loc, board, opponent): # -> Tuple[str, BattleResult]
    ship_struck = board.fire(loc)
    battle_result = None

    if ship_struck is None:
        return (f'You missed at {gridloc_to_str(loc)}.', battle_result)
    elif not ship_struck.has_sunk():
        return (f"You hit {opponent.nicename}'s " +
            colored(ship_struck.name, ship_struck.color, attrs=["reverse"]) +
            f" at {gridloc_to_str(loc)}.", battle_result)
    else:
        msg = 'You ' + colored('SANK', 'white', attrs=["bold"]) + \
            f" {opponent.nicename}'s " + \
            colored(ship_struck.name, ship_struck.color, attrs=["reverse"]) + \
            f' at {gridloc_to_str(loc)}.'

        if all([ship.has_sunk() for ship in board.ships]):
            battle_result = BattleResult.PLAYER_WINS

        return (msg, battle_result)


def battle(referee, player_board, opponent_board, opponent):
    turn_message = "Let's play!"
    battle_result = None

    opponent.to_battlestations()

    while True:
        whose_turn = referee.turn()

        opponent_board.draw(label=opponent.nicename,
            highlight_player=(whose_turn is Turn.OPPONENT),
            draw_all_ships=False)
        player_board.draw(label='You',
            highlight_player=(whose_turn is Turn.PLAYER),
            show_legend=True)

        if battle_result is not None:
            print(turn_message, end=' ')

            if battle_result == BattleResult.PLAYER_WINS:
                print('You won the battle.', end=' ')
            else:
                print(f'{opponent.nicename} won the battle.', end=' ')

            break

        if whose_turn is Turn.PLAYER:
            prompt_attack = PromptGridLoc(
                turn_message + " Ctrl-C/'surrender'/target", ['surrender'],
                validate=opponent_board.is_cell_unhit).ask
            try:
                fire_loc = prompt_attack()
            except PromptAlternate as e:
                if e.alternate == 'surrender':
                    turn_message = choice(jibes)
                    battle_result = BattleResult.OPPONENT_WINS
                    continue
                else:
                    raise RuntimeError(f'Unexpected "{e.alternate}"') from e

            turn_message, battle_result = \
                fire(fire_loc, opponent_board, opponent)

            if battle_result:
                continue
        else:
            print(turn_message,
                f'{opponent.nicename} takes {opponent.pronoun} turn...', end='')
            sys.stdout.flush()

            sleep(2)
            turn_message, battle_result = opponent.fire(player_board)
            print()
            if battle_result:
                continue

    enter_to_continue()
    return battle_result
