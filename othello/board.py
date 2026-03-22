import numpy as np
import pygame
from .constants import WHITE, BLACK, LIGHT_SQUARE, DARK_SQUARE, ROWS, COLS, SQUARE_SIZE, RADIUS_PIECE

class Board:
    def __init__(self):
        # 0: Vazio; 1: Preto; -1: Branco 
        self.matrix = np.zeros((ROWS, COLS), dtype=int)
        self._init_board()
        
        # Definição das 8 direções de busca (Vertical, Horizontal e Diagonais)
        self.directions = [
            (-1, 0), (1, 0), (0, 1), (0, -1), # N, S, L, O
            (-1, -1), (-1, 1), (1, -1), (1, 1) # Diagonais
        ]
    def _init_board(self):
        """Configura as 4 peças iniciais no centro do tabuleiro."""
        self.matrix[3, 3], self.matrix[4, 4] = -1, -1 # Brancas
        self.matrix[3, 4], self.matrix[4, 3] = 1, 1  # Pretas

    def draw_squares(self, win):
        """Desenha o padrão de xadrez do fundo do tabuleiro."""
        win.fill(DARK_SQUARE)
        for row in range(ROWS):
            for col in range(row % 2, ROWS, 2):
                pygame.draw.rect(win, LIGHT_SQUARE, (col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    
    def draw_pieces(self, win):
        """Varre a matriz e desenha as peças presentes."""
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
                    pygame.draw.circle(win, (50, 50, 50), (center_x + 2, center_y + 2), RADIUS_PIECE)
                    # Desenha a peça principal
                    pygame.draw.circle(win, color, (center_x, center_y), RADIUS_PIECE)

    def get_valid_moves(self, player):
        """Retorna uma lista de tuplas (row, col) com todos os movimentos legais."""
        moves = []
        for row in range(ROWS):
            for col in range(COLS):
                if self.is_valid_move(row, col, player):
                    moves.append((row, col))
        return moves
    
    def is_valid_move(self, row, col, player):
        """Verifica se a posição está vazia e se 'ensanduicha' peças adversárias."""
        if self.matrix[row, col] != 0: return False
        directions = [(-1,0),(1,0),(0,1),(0,-1),(-1,-1),(-1,1),(1,-1),(1,1)]
        for dr, dc in directions:
            if self._check_direction(row, col, dr, dc, player): return True
        return False
    
    def _check_direction(self, row, col, dr, dc, player):
        """
        Lógica de busca direcional:
        1. Deve haver uma peça do oponente adjacente.
        2. Deve haver uma peça do próprio jogador fechando a linha.
        """
        opponent = -player
        curr_r, curr_c = row + dr, col + dc
        # Verifica se está dentro do tabuleiro e se a primeira peça adjacente é do oponente
        if not (0 <= curr_r < ROWS and 0 <= curr_c < COLS) or self.matrix[curr_r, curr_c] != opponent:
            return False
        
        # Continua caminhando na direção
        curr_r += dr
        curr_c += dc

        while 0 <= curr_r < ROWS and 0 <= curr_c < COLS:
            if self.matrix[curr_r, curr_c] == player:
                return True
            if self.matrix[curr_r, curr_c] == 0:
                return False # Espaço vazio quebra a sequência
            curr_r += dr
            curr_c += dc

        return False
    
    def make_move(self, row, col, player):
        """Executa a jogada: coloca a peça e vira as capturadas em todas as direções."""
        self.matrix[row, col] = player
        for dr, dc in self.directions:
            if self._check_direction(row, col, dr, dc, player):
                self._flip_pieces(row, col, dr, dc, player)

    def _flip_pieces(self, row, col, dr, dc, player):
        """Altera a cor das peças do oponente até encontrar a peça do jogador."""
        curr_r, curr_c = row + dr, col + dc
        opponent = -player
        while 0 <= curr_r < ROWS and 0 <= curr_c < COLS and self.matrix[curr_r, curr_c] == opponent:
            self.matrix[curr_r, curr_c] = player
            curr_r += dr
            curr_c += dc

    def get_score(self):
        """Retorna o número atual de peças (Pretas, Brancas)."""
        black = np.count_nonzero(self.matrix == 1)
        white = np.count_nonzero(self.matrix == -1)
        return black, white
    
    def copy(self):
        """
        Cria uma cópia profunda do tabuleiro.
        Essencial para o algoritmo Minimax simular jogadas futuras sem alterar o jogo real.
        """
        new_board = Board()
        new_board.matrix = np.copy(self.matrix)
        return new_board
