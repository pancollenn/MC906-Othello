import numpy as np

# =====================================================================
# MATRIZ DE PESOS ESTÁTICOS (para o Modelo 2)
# Baseada em estratégias clássicas de Othello.
# =====================================================================
# Cantos (0,0 etc) são ultra valiosos (+120).
# X-squares (1,1 etc) dão o canto de graça, então são péssimos (-40).
# C-squares (0,1 etc) também são muito perigosos (-20).
# Bordas em geral são boas (+20), miolo é neutro/baixo.
STATIC_WEIGHTS = np.array([
    [ 120, -20,  20,   5,   5,  20, -20,  120],
    [ -20, -40,  -5,  -5,  -5,  -5, -40,  -20],
    [  20,  -5,  15,   3,   3,  15,  -5,   20],
    [   5,  -5,   3,   3,   3,   3,  -5,    5],
    [   5,  -5,   3,   3,   3,   3,  -5,    5],
    [  20,  -5,  15,   3,   3,  15,  -5,   20],
    [ -20, -40,  -5,  -5,  -5,  -5, -40,  -20],
    [ 120, -20,  20,   5,   5,  20, -20,  120]
])

def evaluate_greedy(board_matrix, player_color):
    """
    MODELO 1: Baseline (Guloso)
    Apenas conta a diferença material de peças.
    Bom para o final do jogo, péssimo para o começo/meio.
    """
    # Conta quantas peças o jogador tem e subtrai as do adversário
    player_pieces = np.count_nonzero(board_matrix == player_color)
    opponent_pieces = np.count_nonzero(board_matrix == -player_color)
    
    return float(player_pieces - opponent_pieces)

def evaluate_static(board_matrix, player_color):
    """
    MODELO 2: Heurística Posicional Estática
    Multiplica o tabuleiro atual pela matriz de pesos para dar
    uma nota estratégica à posição.
    """
    # board_matrix contém 1 para Pretas, -1 para Brancas e 0 para vazios.
    # Se multiplicarmos a matriz do jogo pela matriz de pesos, as casas
    # ocupadas pelas Pretas somarão o peso positivo, e as Brancas subtrairão.
    
    score = np.sum(board_matrix * STATIC_WEIGHTS)
    
    # O score atual reflete a vantagem das Pretas (já que Preto = 1).
    # Se a IA for a Branca (-1), precisamos inverter o sinal do score final
    # para que a função sempre retorne positivo quando a IA estiver ganhando.
    if player_color == -1:
        score = -score
        
    return float(score)

def evaluate_mobility(board, player_color):
    """
    Calcula a vantagem de mobilidade.
    Quanto mais movimentos válidos o MAX tiver e menos o MIN tiver, melhor.
    """
    # Usamos a função que vocês já construíram na classe Board
    my_moves = len(board.get_valid_moves(player_color))
    opp_moves = len(board.get_valid_moves(-player_color))
    
    # Se eu tenho 8 jogadas e o oponente tem 2, meu saldo é +6.
    # Se eu tenho 2 e ele tem 8, meu saldo é -6.
    return float(my_moves - opp_moves)

def evaluate_frontier(board_matrix, player_color):
    """
    Conta os discos de fronteira (peças adjacentes a casas vazias).
    Queremos MINIMIZAR os nossos e MAXIMIZAR os do oponente.
    """
    direcoes = [
        (-1, 0), (1, 0), (0, 1), (0, -1),
        (-1, -1), (-1, 1), (1, -1), (1, 1)
    ]
    
    my_frontiers = 0
    opp_frontiers = 0
    
    # Varre o tabuleiro
    for r in range(8):
        for c in range(8):
            peca = board_matrix[r, c]
            if peca != 0:
                is_frontier = False
                
                # Checa os 8 vizinhos da peça
                for dr, dc in direcoes:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < 8 and 0 <= nc < 8:
                        if board_matrix[nr, nc] == 0:
                            is_frontier = True
                            break # Achou um espaço vazio, já é fronteira, não precisa checar o resto
                
                if is_frontier:
                    if peca == player_color:
                        my_frontiers += 1
                    else:
                        opp_frontiers += 1
                        
    # Retornamos (Oponente - Minhas). 
    # Assim, se eu tenho menos fronteiras que o oponente, o valor fica positivo (bom para mim!).
    return float(opp_frontiers - my_frontiers)

def evaluate_dynamic(board, player_color):
    """
    MODELO 3: Heurística Dinâmica Avançada
    Combina controle de cantos (Static Weights), Mobilidade e Discos de Fronteira.
    """
    board_matrix = board.matrix
    
    # 1. Avaliação Posicional (Cantos e Bordas usando o código da mensagem anterior)
    score_posicional = np.sum(board_matrix * STATIC_WEIGHTS)
    if player_color == -1:
        score_posicional = -score_posicional
        
    # 2. Avaliação de Mobilidade
    score_mobility = evaluate_mobility(board, player_color)
    
    # 3. Avaliação de Fronteira
    score_frontier = evaluate_frontier(board_matrix, player_color)
    
    # =================================================================
    # CALIBRAÇÃO DE PESOS (Tuning)
    # Area de testes experimentais.
    # Exemplo: O posicional vale muito, a mobilidade vale razoavelmente, 
    # e a fronteira é um ajuste fino de segurança.
    # =================================================================
    
    # Pesos fixos (pode ser ajustado para melhorar o desempenho)
    POSITIONAL_WEIGHT = 10.0
    MOBILITY_WEIGHT = 5.0
    FRONTIER_WEIGHT = 2.0

    zeros = np.count_nonzero(board_matrix == 0)

    # Pesos dinâmicos
    if zeros > 40:
        # No início do jogo, a mobilidade é mais importante que o posicional
        POSITIONAL_WEIGHT = 5.0
        MOBILITY_WEIGHT = 10.0
    elif 13 < zeros <= 40:
        # No meio do jogo, o posicional ganha mais peso
        POSITIONAL_WEIGHT = 10.0
        MOBILITY_WEIGHT = 5.0
    else:
        # No final do jogo o que importa é numero de peças
        return evaluate_greedy(board_matrix, player_color)
    pontuacao_final = (score_posicional * POSITIONAL_WEIGHT) + \
                      (score_mobility * MOBILITY_WEIGHT) + \
                      (score_frontier * FRONTIER_WEIGHT)
                      
    return pontuacao_final

def evaluate(board, player_color, heuristic_type="dynamic"):
    """
    Função principal que roteia para a heurística desejada.
    heuristic_type pode ser: 'greedy', 'static', 'dynamic'.
    """
    if heuristic_type == "greedy":
        return evaluate_greedy(board.matrix, player_color)
    elif heuristic_type == "static":
        return evaluate_static(board.matrix, player_color)
    elif heuristic_type == "dynamic":
        return evaluate_dynamic(board, player_color)
    else:
        raise ValueError(f"Tipo de heurística '{heuristic_type}' desconhecido.")
