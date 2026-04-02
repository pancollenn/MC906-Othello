import os
# Silencia o Pygame ANTES de qualquer outro import acontecer
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

import random
import time
import concurrent.futures
from datetime import datetime
from pathlib import Path

from minimax.algorithm import iterative_deepening
from othello.board import Board

MAX_DEPTH_CAP = 60
RESULTS_DIR = Path(__file__).parent / "results"



def _cap_depth(depth, cap=MAX_DEPTH_CAP):
    """Normaliza profundidade para inteiro no intervalo [1, cap]."""
    return max(1, min(int(depth), cap))


def _ensure_results_dir():
    """Cria o diretório de resultados se não existir."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def _get_results_filename(agent_a, agent_b, depth_a, depth_b, pruning_a, pruning_b):
    """Gera um nome de arquivo único para os resultados."""
    #timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{agent_a}_vs_{agent_b}_{depth_a}vs{depth_b}_{pruning_a}vs{pruning_b}.txt"


def _save_results(agent_a, agent_b, depth_a, depth_b, pruning_a, pruning_b, wins_a, wins_b, draws, elapsed_s, num_matches, stats_a, stats_b):
    """Salva os resultados do torneio em um arquivo."""
    _ensure_results_dir()
    filepath = RESULTS_DIR / _get_results_filename(agent_a, agent_b, depth_a, depth_b, pruning_a, pruning_b)
    
    # Cálculos de médias para o Agente A
    avg_nodes_a = stats_a['nodes'] / stats_a['moves'] if stats_a['moves'] else 0
    avg_depth_a = stats_a['depths'] / stats_a['moves'] if stats_a['moves'] else 0
    avg_time_a = stats_a['time'] / stats_a['moves'] if stats_a['moves'] else 0

    # Cálculos de médias para o Agente B
    avg_nodes_b = stats_b['nodes'] / stats_b['moves'] if stats_b['moves'] else 0
    avg_depth_b = stats_b['depths'] / stats_b['moves'] if stats_b['moves'] else 0
    avg_time_b = stats_b['time'] / stats_b['moves'] if stats_b['moves'] else 0

    content = f"""=== TORNEIO: {agent_a}(d={depth_a}, p={pruning_a}) vs {agent_b}(d={depth_b}, p={pruning_b}) ===
Data: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Número de partidas: {num_matches}
Tempo total do torneio: {elapsed_s:.2f}s

--- RESULTADO FINAL ---
Vitórias {agent_a}: {wins_a} ({(wins_a/num_matches)*100:.1f}%)
Vitórias {agent_b}: {wins_b} ({(wins_b/num_matches)*100:.1f}%)
Empates: {draws}

--- MÉTRICAS EXPERIMENTAIS ({agent_a}) ---
Nós expandidos por jogada (Média): {avg_nodes_a:.2f}
Profundidade alcançada (Média): {avg_depth_a:.2f}
Tempo gasto por jogada (Média): {avg_time_a:.4f}s

--- MÉTRICAS EXPERIMENTAIS ({agent_b}) ---
Nós expandidos por jogada (Média): {avg_nodes_b:.2f}
Profundidade alcançada (Média): {avg_depth_b:.2f}
Tempo gasto por jogada (Média): {avg_time_b:.4f}s
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filepath


def play_match(
    heuristic_black,
    heuristic_white,
    max_depth_black,
    max_depth_white,
    pruning_black=True,
    pruning_white=True,
    random_openings = 10,
    seed=None,
):
    """
    Roda UMA partida completa sem interface gráfica.
    Retorna 1 se Pretas venceram, -1 se Brancas venceram, 0 se empate.
    """
    if seed is not None:
        random.seed(seed)

    board = Board()
    max_depth_black = _cap_depth(max_depth_black)
    max_depth_white = _cap_depth(max_depth_white)
    current_player = 1 # 1 (Pretas) começam
    move_count = 0
    
    # Dicionário para guardar as estatísticas brutas DESTA partida
    match_stats = {
        1: {'nodes': 0, 'depths': 0, 'time': 0.0, 'moves': 0},
        -1: {'nodes': 0, 'depths': 0, 'time': 0.0, 'moves': 0}
    }
    
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
        current_max_depth = max_depth_black if current_player == 1 else max_depth_white
        current_pruning = pruning_black if current_player == 1 else pruning_white
        
        # Abertura Aleatória para gerar diversidade de partidas
        if move_count < random_openings:
            best_move = random.choice(valid_moves)
        else:
            # MARCA O TEMPO DE INÍCIO DA JOGADA
            start_move_time = time.perf_counter()
            
            _, best_move, depth, nodes = iterative_deepening(
                board, 
                player_color=current_player,
                time_limit=0.95,
                max_depth=current_max_depth,
                heuristic_type=current_heuristic,
                use_pruning=current_pruning
            )
            
            # MARCA O TEMPO DE FIM E ATUALIZA AS ESTATÍSTICAS
            elapsed_move_time = time.perf_counter() - start_move_time
            
            match_stats[current_player]['nodes'] += nodes
            match_stats[current_player]['depths'] += depth
            match_stats[current_player]['time'] += elapsed_move_time
            match_stats[current_player]['moves'] += 1
            
        board.make_move(best_move[0], best_move[1], current_player)
        current_player *= -1
        move_count += 1
        
    # Calcula quem ganhou
    black_score, white_score = board.get_score()
    if black_score > white_score: winner = 1
    elif white_score > black_score: winner = -1
    else: winner = 0
    
    return winner, match_stats

def run_tournament_parallel(
        agent_a, 
        agent_b, 
        depth_a=60, 
        depth_b=60,
        pruning_a=True, 
        pruning_b=True, 
        num_matches=20):
    """
    Faz os agentes se enfrentarem. Eles devem alternar as cores, 
    pois começar jogando (Pretas) dá uma vantagem tática inicial.
    Faz os agentes se enfrentarem rodando as partidas em PARALELO 
    usando todos os núcleos do processador.
    """
    wins_a = 0
    wins_b = 0
    draws = 0
    
    # Acumuladores globais do torneio para o Agente A e B
    stats_a = {'nodes': 0, 'depths': 0, 'time': 0.0, 'moves': 0}
    stats_b = {'nodes': 0, 'depths': 0, 'time': 0.0, 'moves': 0}

    start_time = time.perf_counter()
    print(f"[Iniciando] {agent_a}(Poda={pruning_a}) vs {agent_b}(Poda={pruning_b})")
    
    matches = []
    for i in range(num_matches):
        if i % 2 == 0:
            matches.append((agent_a, depth_a, pruning_a, agent_b, depth_b, pruning_b, "A", "B")) 
        else:
            matches.append((agent_b, depth_b, pruning_b, agent_a, depth_a, pruning_a, "B", "A")) 

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = {
            executor.submit(play_match, black, white, d_black, d_white, p_black, p_white, 10, i): (owner_black, owner_white)
            for i, (black, d_black, p_black, white, d_white, p_white, owner_black, owner_white) in enumerate(matches)
        }
        
        partidas_concluidas = 0
        for future in concurrent.futures.as_completed(futures):
            owner_black, owner_white = futures[future] 
            try:
                winner, match_stats = future.result() 
                
                # Desempacota estatísticas da partida
                if owner_black == "A":
                    for key in stats_a: stats_a[key] += match_stats[1][key]
                    for key in stats_b: stats_b[key] += match_stats[-1][key]
                else:
                    for key in stats_b: stats_b[key] += match_stats[1][key]
                    for key in stats_a: stats_a[key] += match_stats[-1][key]

                if winner == 1: 
                    if owner_black == "A": wins_a += 1
                    else: wins_b += 1
                elif winner == -1: 
                    if owner_white == "A": wins_a += 1
                    else: wins_b += 1
                else: draws += 1
                    
                partidas_concluidas += 1
                print(f"  Partida {partidas_concluidas}/{num_matches} concluída")
                
            except Exception as exc:
                print(f"  ⚠️ Erro fatal em uma das partidas: {exc}")
                partidas_concluidas += 1
                draws +=1

    elapsed_s = time.perf_counter() - start_time
    
    # Salva resultados em arquivo
    filepath = _save_results(
        agent_a,
        agent_b,
        depth_a,
        depth_b,
        pruning_a,
        pruning_b,
        wins_a,
        wins_b,
        draws,
        elapsed_s,
        num_matches,
        stats_a,
        stats_b,
    )
    print(f"[Concluído] Resultados salvos em: {filepath}\n")

# Para testar (quando o minimax e as heurísticas estiverem integrados):
if __name__ == "__main__":
    num_matches = 24 # tentar colocar multiplos de 12
    tournaments_to_run = [
        # # Teste 1: Nossa heurística top contra a burrinha
        # ("dynamic", "greedy", 60, 60, num_matches),
        # # Teste 2: Heurística posicional contra a burrinha
        # ("static", "greedy", 60, 60, num_matches),
        # # Teste 3: A batalha final (Qual das nossas estratégias é melhor?)
        # ("dynamic", "static", 60, 60, num_matches),

        # # Teste 4: heurística inteligente, mas com profundidade limita vs heurística burra, mas com profundidade máxima (Será que a profundidade compensa a burrice?)
        # ("dynamic", "greedy", 4, 6, num_matches),

        # # Teste 5: heurística inteligente 2, mas com profundidade limita vs heurística burra, mas com profundidade máxima (Será que a profundidade compensa a burrice?)
        # ("static", "greedy", 4, 6, num_matches),

        # # Teste 6: Duas heurísticas fortes, mas com profundidade limita.
        # # Será que o resultado muda com relação ao teste 3?
        # ("static", "dynamic", 4, 4, num_matches),

        # ("static", "dynamic", 4, 6, num_matches),

        # ("static", "dynamic", 6, 4, num_matches),


        # #Testar com profundidade 1. A ideia é avaliar as heuristicas de maneira bruta
        # # Teste 7
        # ("dynamic", "greedy", 1, 1, num_matches),
        # # Teste 8:
        # ("static", "greedy", 1, 1, num_matches),
        # # Teste 9:
        # ("dynamic", "static", 1, 1, num_matches),

        # ("static", "static", 4, 6, num_matches),
        # ("dynamic", "dynamic", 4, 6, num_matches),
        # ("greedy", "greedy", 4, 6, num_matches),


        # COMPARAÇÕES EXIGIDAS PELO EDITAL:
        # Teste de Poda: Minimax vs Alpha-Beta (Mesma heurística para ser justo)
        ("static", "static", 60, 60, False, True, num_matches), 
        ("dynamic", "dynamic", 60, 60, False, True, num_matches),
        ("greedy", "greedy", 60, 60, False, True, num_matches),
        
        # Teste de Heurísticas
        ("dynamic", "static", 60, 60, True, True, num_matches),
        ("dynamic", "greedy", 60, 60, True, True, num_matches),
        ("static", "greedy", 60, 60, True, True, num_matches),
    ]

    print("=== TORNEIOS PROGRAMADOS ===")
    print(f"Total: {len(tournaments_to_run)} torneios")
    for i, (agent_a, agent_b, depth_a, depth_b, pruning_a, pruning_b, num_matches) in enumerate(tournaments_to_run, start=1):
        print(f"{i}. {agent_a}(d={depth_a}, p={pruning_a}) vs {agent_b}(d={depth_b}, p={pruning_b}) - {num_matches} partidas")
    print("============================\n")

    for agent_a, agent_b, depth_a, depth_b, pruning_a, pruning_b, num_matches in tournaments_to_run:
        run_tournament_parallel(agent_a, agent_b, depth_a, depth_b, pruning_a, pruning_b, num_matches)