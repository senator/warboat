import sys

from helpers import NiceEnum
from prompt import PromptGridLoc, PromptAlternate, enter_to_continue
from referee import Turn


class BattleResult(NiceEnum):
    PLAYER_WINS = 1
    OPPONENT_WINS = 2


def fire(loc, board): # -> tuple[str, BattleResult]:
    return('You hit yourself in the foot.', None) # XXX TODO


def battle(referee, player_board, opponent_board, opponent):
    turn_message = "Let's play!"
    battle_result = None

    while True:
        opponent_board.draw(label=opponent.nicename,
            draw_ships=(battle_result is not None))
        player_board.draw(label='You', highlight_player=True, show_legend=True)

        if battle_result is not None:
            print(turn_message, end=' ')

            if battle_result == BattleResult.PLAYER_WINS:
                print('You won the battle.', end=' ')
            else:
                print(f'{opponent.nicename} won the battle.', end=' ')

            break

        if referee.turn() is Turn.PLAYER:
            prompt_attack = PromptGridLoc(
                turn_message + " Ctrl-C/'surrender'/target", ('surrender')).ask
            try:
                fire_loc = prompt_attack()
            except PromptAlternate as e:
                if e.alternate == 'surrender':
                    turn_message = 'Your cowardice is unbecoming.'
                    battle_result = BattleResult.OPPONENT_WINS
                    continue
                else:
                    raise RuntimeError('Unexpected') from e

            turn_message, battle_result = fire(fire_loc, opponent_board)
            if battle_result:
                continue
        else:
            print(turn_message,
                f'{opponent.nicename} takes {opponent.pronoun} turn...', end='')
            sys.stdout.flush()

            turn_message, battle_result = opponent.fire(player_board)
            print()
            if battle_result:
                continue

    enter_to_continue()
    return battle_result
