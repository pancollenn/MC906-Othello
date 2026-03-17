import numpy as np
import pygame
from .constants import WHITE, BLACK, LIGHT_SQUARE, DARK_SQUARE, ROWS, COLS, SQUARE_SIZE, RADIUS

class Board:
    def __init__(self):
        # 0: Vazio; 1: Preto; -1: Branco 
        self.matrix = np.zeros((8, 8), dtype=int)
        # Posições iniciais do Othello:
        self.matrix[3, 3], self.matrix[4, 4] = -1, -1
        self.matrix[3, 4], self.matrix[4, 3] = 1, 1

    def draw_squares(self, win):
        win.fill(DARK_SQUARE)
        for row in range(ROWS):
            for col in range(row % 2, ROWS, 2):
                pygame.draw.rect(win, LIGHT_SQUARE, (col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    
    def draw_pieces(self, win):
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.matrix[row, col]

                if piece != 0:
                    # Define a cor da peça
                    color = BLACK if piece == 1 else WHITE
                
                    # Calcula o centro do círculo
                    # Importante: No Pygame, o primeiro argumento é X (coluna) e o segundo é Y (linha)
                    center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
                    center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2

                    # Desenha sombra ao redor da peça
                    pygame.draw.circle(win, (50, 50, 50), (center_x + 2, center_y + 2), RADIUS)
                    # Desenha a peça principal
                    pygame.draw.circle(win, color, (center_x, center_y), RADIUS)