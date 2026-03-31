import numpy as np
from minimax.heuristics import evaluate


def order_moves(board, valid_moves, current_turn_color, is_maximizing, ai_color, heuristic_type="dynamic"):
    """
    Ordena os movimentos avaliando a posição resultante de cada um.
    """
    move_scores = []
    
    for move in valid_moves:
        temp_board = board.copy()
        temp_board.make_move(move[0], move[1], current_turn_color)
        
        # Avalia o tabuleiro resultante do ponto de vista da IA
        score = evaluate(temp_board, ai_color, heuristic_type)
        move_scores.append((score, move))
    
    move_scores.sort(key=lambda x: x[0], reverse=is_maximizing)
    
    # Extrai apenas as coordenadas ordenadas
    return [item[1] for item in move_scores]

def minimax(board, depth, alpha, beta, max_player, player_color, heuristic_type="dynamic"):
    """
    Algoritmo Minimax: player_color: 1 para Preto, -1 para Branco
    Algoritmo Minimax com Poda Alpha-Beta.
    alpha: Melhor opção já garantida para o Maximizador (inicialmente float('-inf'))
    beta: Melhor opção já garantida para o Minimizador (inicialmente float('inf'))
    """
    # Define de quem é o turno na simulação atual
    current_turn_color = player_color if max_player else -player_color
    
    # Casos base: profundidade alcançada ou fim de jogo
    valid_moves = board.get_valid_moves(current_turn_color)

    # Caso precise passar a vez
    if not valid_moves:
        # Verifica se o oponente tem movimentos
        opponent_color = -current_turn_color
        opponent_moves = board.get_valid_moves(opponent_color)
        
        if not opponent_moves:
            # Fim de jogo real: Nenhum dos dois tem jogadas válidas
            return evaluate(board, player_color, heuristic_type), None
        else:
            # Passa a vez: Chama o minimax com o MESMO tabuleiro, mas inverte o max_player
            # Menor profundidade para evitar loops infinitos caso fiquem passando a vez
            eval_score, _ = minimax(board, depth - 1, alpha, beta, not max_player, player_color, heuristic_type)
            return eval_score, None # None porque não há jogada a ser feita, apenas passa a vez

    if depth == 0:
        return evaluate(board, player_color, heuristic_type), None

    valid_moves = order_moves(board, valid_moves, current_turn_color, max_player, player_color, heuristic_type)
    
    best_move = None
    
    if max_player:
        max_eval = float('-inf')
        for move in valid_moves:
            # Simula a jogada em uma cópia do tabuleiro
            temp_board = board.copy()
            temp_board.make_move(move[0], move[1], player_color)

            eval, _ = minimax(temp_board, depth-1, alpha, beta, False, player_color, heuristic_type)

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
            temp_board.make_move(move[0], move[1], -player_color)

            eval, _ = minimax(temp_board, depth-1, alpha, beta, True, player_color, heuristic_type)

            if eval < min_eval:
                min_eval = eval
                best_move = move
            
            # Atualiza o Beta e verifica a Poda
            beta = min(beta, eval)
            if beta <= alpha:
                break # Poda Alpha-Beta: o maximizador nunca vai escolher este ramo
            
        return min_eval, best_move