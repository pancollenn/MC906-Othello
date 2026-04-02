import pygame

from othello.constants import WIDTH, HEIGHT, SQUARE_SIZE
from othello.game import Game
from minimax.algorithm import iterative_deepening

FPS = 60
AI_TIME_LIMIT_SECONDS = 0.95
AI_MAX_DEPTH = 60

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Othello')
HEURISTIC = "dynamic" # "dynamic", "static" ou "greedy"

def main():
    run = True
    clock = pygame.time.Clock()
    game = Game(WIN)
    depths = []
    while run:
        clock.tick(FPS)

        if not game.game_over and game.turn == -1: # Se for a vez do Branco (IA)
            #pygame.time.wait(1000)
            _, move, depth = iterative_deepening(
                game.board,
                -1,
                time_limit=AI_TIME_LIMIT_SECONDS,
                max_depth=AI_MAX_DEPTH,
                heuristic_type=HEURISTIC,
            )
            print(f"IA concluiu profundidade {depth}")
            depths.append(depth)
            if move:
                game.select(move[0], move[1])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos() # pos = (coordenada col, coordenada row)
                # Converte coordenadas de pixels para (row, col)
                row, col = pos[1] // SQUARE_SIZE, pos[0] // SQUARE_SIZE
                game.select(row, col)

        game.update()


    depths.sort()

    print("Profundidade mediana", depths[len(depths) // 2])  # Imprime a mediana das profundidades alcançadas pela IA
    print("Profundidade média", sum(depths) / len(depths))
    pygame.quit()


main()
