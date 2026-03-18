import pygame

from .board import Board
from .constants import SQUARE_SIZE, BLUE, ROWS, COLS, RADIUS_VALID_MOVE

class Game:
    def __init__(self, win):
        self.win = win
        self._init()

    def _init(self):
        """Inicializa o estado interno do jogo."""
        self.board = Board()
        self.turn = 1
        self.valid_moves = self.board.get_valid_moves(self.turn)
        self.game_over = False

    def update(self):
        """Desenha o estado atual do jogo na tela."""
        self.board.draw_squares(self.win)
        self.board.draw_pieces(self.win)
        self._draw_valid_moves() # Desenha as bolinhas azuis
        pygame.display.update()

    def _draw_valid_moves(self):
        """Desenha bolinhas azuis pequenas nos quadrados onde o jogador pode jogar."""
        for move in self.valid_moves:
            row, col = move
            # Centro da bolinha azul
            center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
            center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
            # Desenha um círculo azul pequeno (raio 10)
            pygame.draw.circle(self.win, BLUE, (center_x, center_y), RADIUS_VALID_MOVE)

    def select(self, row, col):
        """Tenta realizar uma jogada na posição clicada."""
        if self.game_over:
            return False

        if (row, col) in self.valid_moves:
            self.board.make_move(row, col, self.turn)
            self._change_turn()
            return True
        
        return False
    
    def _change_turn(self):
        """Troca o turno e gerencia a regra de passar a vez."""
        self.turn *= -1
        self.valid_moves = self.board.get_valid_moves(self.turn)

        # Se o próximo jogador não tiver movimentos legais
        if not self.valid_moves:
            print(f"Jogador {self.turn} não tem movimentos. Passando a vez...")
            self.turn *= -1
            self.valid_moves = self.board.get_valid_moves(self.turn)
            
            # Se o jogador original também não tiver movimentos, fim de jogo
            if not self.valid_moves:
                self.game_over = True
                self._declare_winner()

    def _declare_winner(self):
        """Calcula o placar final e imprime o vencedor."""
        # Supondo que você adicionou get_score no board.py
        black, white = self._count_pieces()
        print("-" * 20)
        print("FIM DE JOGO!")
        print(f"Pretas: {black} | Brancas: {white}")
        if black > white: print("VENCEDOR: PRETAS!")
        elif white > black: print("VENCEDOR: BRANCAS!")
        else: print("EMPATE!")
        print("-" * 20)

    def _count_pieces(self):
        """Conta as peças na matriz do board."""
        black = 0
        white = 0
        for row in self.board.matrix:
            for val in row:
                if val == 1: black += 1
                elif val == -1: white += 1
        return black, white
