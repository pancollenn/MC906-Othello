import numpy as np
from minimax.heuristics import evaluate

MOVE_ORDER_WEIGHTS = {
    # Cantos (Melhor jogada possível)
    (0,0): 100, (0,7): 100, (7,0): 100, (7,7): 100,
    
    # X-Squares (Piores jogadas possíveis, dão o canto de graça)
    (1,1): -50, (1,6): -50, (6,1): -50, (6,6): -50,
    
    # C-Squares (Muito ruins)
    (0,1): -20, (1,0): -20, (0,6): -20, (1,7): -20,
    (6,0): -20, (7,1): -20, (6,7): -20, (7,6): -20,
    
    # Sweet-16 (O miolo central, neutro/bom no início)
    (2,2): 5, (2,3): 5, (2,4): 5, (2,5): 5,
    (3,2): 5, (3,5): 5, (4,2): 5, (4,5): 5,
    (5,2): 5, (5,3): 5, (5,4): 5, (5,5): 5,
}

def order_moves(valid_moves):
    """
    Ordenação ULTRARRÁPIDA. 
    Não faz cópias de tabuleiro, não simula jogadas.
    Apenas olha a coordenada do movimento e atribui uma prioridade estática.
    """
    move_scores = []
    
    for move in valid_moves:
        row, col = move
        # Pega a nota daquela coordenada. Se não estiver no dict, a nota é 0.
        score = MOVE_ORDER_WEIGHTS.get((row, col), 0)
        
        move_scores.append((score, move))
    
    # MAX quer os maiores scores primeiro. MIN quer os menores.
    # Mas no Move Ordering estático para Alpha-Beta, nós SEMPRE queremos testar
    # as jogadas "boas" (positivas) primeiro, não importa de quem seja a vez,
    # porque as jogadas boas do MIN também são as que cortam o MAX mais rápido.
    move_scores.sort(key=lambda x: x[0], reverse=True)
    
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

    valid_moves = order_moves(valid_moves)
    
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