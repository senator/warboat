from prompt import PromptGridLoc


def battle(player_board, opponent_board):
    print("Let's play!")

    finished = False
    prompt_attack = PromptGridLoc('Attack where? ').ask

    while not finished:
        opponent_board.draw(label='Billy', draw_ships=False)
        player_board.draw(label='You', highlight_player=True)
        attack_loc = prompt_attack()

        # XXX temporary
        if attack_loc == (0, 0):
            finished = True
