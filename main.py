#!/usr/bin/env python3

from prompt import PromptQuit, PromptDict
from player import configure_player_board
from battle import battle
from board import Board

def main():
    # User's step 1: choose number of battles to play
    num_battles = PromptDict('How many battles will you try to win? ', {
        1: 'One battles only',
        2: 'Best two out of three',
        3: 'Best three out of five'}).ask()

    # User's step 2: choose opponent (a proxy for difficulty level)
    # XXX TODO

    # User's step 3: choose who goes first
    # XXX TODO

    player_wins = 0
    opponent_wins = 0

    while player_wins < num_battles and opponent_wins < num_battles:
        player_board = configure_player_board()

        opponent_board = Board()
        opponent_board.add_ships_randomly()

        if battle(player_board, opponent_board) == 0:
            player_wins += 1
        else:
            opponent_wins += 1

    # XXX TODO: make nicer victory display, use opponent's name instead of
    # just 'computer'.
    print("Winner:",
        "You" if player_wins > opponent_wins else "computer", '!')

if __name__ == '__main__':
    try:
        main()
    except PromptQuit:
        print('Program aborted. Goodbye!')
