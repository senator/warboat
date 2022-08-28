#!/usr/bin/env python3

from termcolor import colored

from prompt import PromptQuit, PromptDict, enum_to_prompt_dict
from player import configure_player_board
from opponent import OpponentID, get_opponent_by_id
from battle import battle, BattleResult
from board import Board
from referee import Referee

def main():
    # User's step 1: choose number of battles to play
    num_battles = PromptDict('How many battles will you try to win? ', {
        1: 'One battle only',
        2: 'Best two out of three',
        3: 'Best three out of five'}).ask()

    # User's step 2: choose opponent (a proxy for difficulty level)
    opponent_id = OpponentID(
        PromptDict('Whom will you challenge? ',
            enum_to_prompt_dict(OpponentID)).ask())
    opponent = get_opponent_by_id(opponent_id)

    # User's step 3: choose who goes first
    # XXX TODO

    player_wins = 0
    opponent_wins = 0

    while player_wins < num_battles and opponent_wins < num_battles:
        player_board = configure_player_board()

        opponent_board = Board()
        opponent_board.add_ships_randomly()

        referee = Referee() # XXX tie to step 3 above
        if battle(referee, player_board, opponent_board, opponent) == \
            BattleResult.PLAYER_WINS:
            player_wins += 1
        else:
            opponent_wins += 1

    if player_wins > opponent_wins:
        print(colored(f'Congratulations! You beat {opponent.nicename}!',
            'green', attrs=['bold', 'blink']))
    else:
        print(colored(f'Tough luck! {opponent.nicename} beat you. :-(', 'red'))


if __name__ == '__main__':
    try:
        main()
    except PromptQuit:
        print('Program aborted. Goodbye!')
