import numpy as np

def evaluate(board, player_color):
    """
    Heurística: Saldo de peças relativo ao jogador da IA.
    Se a IA é branca, quer maximizar (Brancas - Pretas).
    """
    black, white = board.get_score()
    # Retorna o saldo do ponto de vista da cor da IA
    if player_color == 1: # Preto
        return black - white
    else: # Branco
        return white - black

def minimax(board, depth, max_player, player_color):
    """
    Algoritmo Minimax: player_color: 1 para Preto, -1 para Branco
    """
    # Caso base: profundidade alcançada ou fim de jogo
    valid_moves = board.get_valid_moves(player_color if max_player else -player_color)
    if depth == 0 or not valid_moves:
        return evaluate(board, player_color), None
    
    best_move = None
    if max_player:
        max_eval = float('-inf')
        for move in valid_moves:
            # Simula a jogada em uma cópia do tabuleiro
            temp_board = board.copy()
            temp_board.make_move(move[0], move[1], player_color)

            eval, _ = minimax(temp_board, depth-1, False, player_color)

            if eval > max_eval:
                max_eval = eval
                best_move = move

        return max_eval, best_move
    
    else:
        min_eval = float('inf')
        for move in valid_moves:
            temp_board = board.copy()
            temp_board.make_move(move[0], move[1], ~player_color)

            eval, _ = minimax(temp_board, depth-1, True, player_color)

            if eval < min_eval:
                min_eval = eval
                best_move = move
            
        return min_eval, best_move