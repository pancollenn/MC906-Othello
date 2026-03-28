import pygame

from othello.constants import WIDTH, HEIGHT, SQUARE_SIZE
from othello.game import Game
from minimax.algorithm import minimax

FPS = 60

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Othello')

def main():
    run = True
    clock = pygame.time.Clock()
    game = Game(WIN)
    
    while run:
        clock.tick(FPS)

        if not game.game_over and game.turn == -1: # Se for a vez do Branco (IA)
            pygame.time.wait(1000)
            # Chama o minimax com profundidade 3 (ajuste conforme a performance)
            _, move = minimax(game.board, 3, float('-inf'), float('inf'), True, -1)
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

    pygame.quit()

main()
