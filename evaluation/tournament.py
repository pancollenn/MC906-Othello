
import random
import time
import concurrent.futures

from minimax.algorithm import minimax
from othello.board import Board

def play_match(heuristic_black, heuristic_white, random_openings=4, seed=None):
    """
    Roda UMA partida completa sem interface gráfica.
    Retorna 1 se Pretas venceram, -1 se Brancas venceram, 0 se empate.
    """
    if seed is not None:
        random.seed(seed)

    board = Board()
    current_player = 1 # 1 (Pretas) começam
    move_count = 0
    
    while True:
        valid_moves = board.get_valid_moves(current_player)
        
        # Regra do Passar a Vez e Fim de Jogo
        if not valid_moves:
            opponent_moves = board.get_valid_moves(-current_player)
            if not opponent_moves:
                break # Fim de jogo real
            else:
                current_player *= -1 # Passa a vez
                continue
                
        # Define qual IA vai jogar
        current_heuristic = heuristic_black if current_player == 1 else heuristic_white
        
        # Abertura Aleatória para gerar diversidade de partidas
        if move_count < random_openings:
            best_move = random.choice(valid_moves)
        else:
            # Chama o algoritmo de busca. 
            # Dica: Passar a heurística como string para o minimax decidir lá dentro.
            # Estamos usando uma profundidade fixa para o teste de win-rate puro.
            _, best_move = minimax(board, depth=4, alpha=float('-inf'), beta=float('inf'), 
                                   max_player=True, player_color=current_player, 
                                   heuristic_type=current_heuristic)
            
        # Executa a jogada
        board.make_move(best_move[0], best_move[1], current_player)
        current_player *= -1
        move_count += 1
        
    # Calcula quem ganhou
    black_score, white_score = board.get_score()
    if black_score > white_score: return 1
    elif white_score > black_score: return -1
    else: return 0

def run_tournament(agent_a, agent_b, num_matches=20):
    """
    Faz os agentes se enfrentarem. Eles devem alternar as cores, 
    pois começar jogando (Pretas) dá uma vantagem tática inicial.
    """
    wins_a = 0
    wins_b = 0
    draws = 0

    start_time = time.perf_counter()
    
    print(f"--- Torneio: {agent_a} vs {agent_b} ({num_matches} partidas) ---")
    
    for i in range(num_matches):
        # Alterna as cores para ser justo
        if i % 2 == 0:
            winner = play_match(agent_a, agent_b, seed=i)
            if winner == 1: wins_a += 1
            elif winner == -1: wins_b += 1
            else: draws += 1
        else:
            winner = play_match(agent_b, agent_a, seed=i)
            # Como agent_b jogou de pretas (1), se winner == 1, B venceu
            if winner == 1: wins_b += 1
            elif winner == -1: wins_a += 1
            else: draws += 1
            
        print(f"Partida {i+1}/{num_matches} concluída...")

    elapsed_s = time.perf_counter() - start_time
    avg_s = elapsed_s / num_matches if num_matches else 0.0
        
    print("\n=== RESULTADO FINAL ===")
    print(f"Vitórias {agent_a}: {wins_a} ({(wins_a/num_matches)*100:.1f}%)")
    print(f"Vitórias {agent_b}: {wins_b} ({(wins_b/num_matches)*100:.1f}%)")
    print(f"Empates: {draws}")
    print(f"Tempo total: {elapsed_s:.2f}s (média: {avg_s:.2f}s/partida)")
    print("=======================\n")

def run_tournament_parallel(agent_a, agent_b, num_matches=20):
    """
    Faz os agentes se enfrentarem rodando as partidas em PARALELO 
    usando todos os núcleos do processador.
    """
    wins_a = 0
    wins_b = 0
    draws = 0

    start_time = time.perf_counter()
    
    print(f"--- Torneio: {agent_a} vs {agent_b} ({num_matches} partidas) ---")
    print("Iniciando processamento paralelo... Os resultados aparecerão fora de ordem.")
    
    # 1. Preparamos a lista de confrontos, alternando as cores
    matches = []
    for i in range(num_matches):
        if i % 2 == 0:
            matches.append((agent_a, agent_b)) # A de Pretas
        else:
            matches.append((agent_b, agent_a)) # B de Pretas

    # 2. Iniciamos o Pool de Processos (usa 100% do seu processador)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Submete todas as partidas simultaneamente.
        # Guardamos um dicionário vinculando a "promessa" (future) aos agentes que estão jogando.
        futures = {executor.submit(play_match, black, white, seed=i): (black, white) for i, (black, white) in enumerate(matches)}
        
        partidas_concluidas = 0
        
        # 3. as_completed libera o resultado assim que qualquer partida terminar
        for future in concurrent.futures.as_completed(futures):
            black, white = futures[future] # Descobre quem estava jogando nesta partida
            try:
                winner = future.result() # Pega o resultado (1, -1 ou 0)
                
                # Contabiliza os pontos corretamente
                if winner == 1: # Pretas ganharam
                    if black == agent_a: wins_a += 1
                    else: wins_b += 1
                elif winner == -1: # Brancas ganharam
                    if white == agent_a: wins_a += 1
                    else: wins_b += 1
                else:
                    draws += 1
                    
                partidas_concluidas += 1
                print(f"Partida {partidas_concluidas}/{num_matches} concluída...")
                
            except Exception as exc:
                print(f"⚠️ Erro fatal em uma das partidas: {exc}")
                partidas_concluidas += 1
                draws +=1

    elapsed_s = time.perf_counter() - start_time
    avg_s = elapsed_s / num_matches if num_matches else 0.0
        
    print("\n=== RESULTADO FINAL ===")
    print(f"Vitórias {agent_a}: {wins_a} ({(wins_a/num_matches)*100:.1f}%)")
    print(f"Vitórias {agent_b}: {wins_b} ({(wins_b/num_matches)*100:.1f}%)")
    print(f"Empates: {draws}")
    print(f"Tempo total: {elapsed_s:.2f}s (média: {avg_s:.2f}s/partida)")
    print("=======================\n")

# Para testar (quando o minimax e as heurísticas estiverem integrados):
if __name__ == "__main__":
    # Teste 1: Nossa heurística top contra a burrinha
    run_tournament_parallel("dynamic", "greedy", num_matches=20)
    
    # Teste 2: Heurística posicional contra a burrinha
    run_tournament_parallel("static", "greedy", num_matches=20)
    
    # Teste 3: A batalha final (Qual das nossas estratégias é melhor?)
    run_tournament_parallel("dynamic", "static", num_matches=20)