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

def order_moves(board, valid_moves, current_turn_color, is_maximizing, ai_color):
    """
    Ordena os movimentos avaliando a posição resultante de cada um.
    """
    move_scores = []
    
    for move in valid_moves:
        temp_board = board.copy()
        temp_board.make_move(move[0], move[1], current_turn_color)
        
        # Avalia o tabuleiro resultante do ponto de vista da IA
        score = evaluate(temp_board, ai_color)
        move_scores.append((score, move))
    
    move_scores.sort(key=lambda x: x[0], reverse=is_maximizing)
    
    # Extrai apenas as coordenadas ordenadas
    return [item[1] for item in move_scores]

def minimax(board, depth, alpha, beta, max_player, player_color):
    """
    Algoritmo Minimax: player_color: 1 para Preto, -1 para Branco
    Algoritmo Minimax com Poda Alpha-Beta.
    alpha: Melhor opção já garantida para o Maximizador (inicialmente float('-inf'))
    beta: Melhor opção já garantida para o Minimizador (inicialmente float('inf'))
    """
    # Define de quem é o turno na simulação atual
    current_turn_color = player_color if max_player else ~player_color
    
    # Caso base: profundidade alcançada ou fim de jogo
    valid_moves = board.get_valid_moves(current_turn_color)
    if depth == 0 or not valid_moves:
        return evaluate(board, player_color), None
    
    valid_moves = order_moves(board, valid_moves, current_turn_color, max_player, player_color)
    
    best_move = None
    
    if max_player:
        max_eval = float('-inf')
        for move in valid_moves:
            # Simula a jogada em uma cópia do tabuleiro
            temp_board = board.copy()
            temp_board.make_move(move[0], move[1], player_color)

            eval, _ = minimax(temp_board, depth-1, alpha, beta, False, player_color)

            if eval > max_eval:
                max_eval = eval
                best_move = move
            
            # Atualiza o Alpha e verifica a Poda
            alpha = max(alpha, eval)
            if beta <= alpha:
                break # Poda Alpha-Beta: o minimizador nunca vai permitir chegar neste ramo
                
        return max_eval, best_move
    
    else:
        min_eval = float('inf')
        for move in valid_moves:
            temp_board = board.copy()
            temp_board.make_move(move[0], move[1], ~player_color)

            eval, _ = minimax(temp_board, depth-1, alpha, beta, True, player_color)

            if eval < min_eval:
                min_eval = eval
                best_move = move
            
            # Atualiza o Beta e verifica a Poda
            beta = min(beta, eval)
            if beta <= alpha:
                break # Poda Alpha-Beta: o maximizador nunca vai escolher este ramo
            
        return min_eval, best_move