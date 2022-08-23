#!/usr/bin/env python3

from prompt import PromptQuit
from player import configure_player_board
from opponent import configure_opponent_board
from battle import battle

def main():
    player_board = configure_player_board()
    opponent_board = configure_opponent_board()
    battle(player_board, opponent_board)

if __name__ == '__main__':
    try:
        main()
    except PromptQuit:
        print('Program aborted. Goodbye!')
