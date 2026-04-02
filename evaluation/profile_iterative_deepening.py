import cProfile
import os
import random
import sys
from pathlib import Path

# Silence pygame import banner used transitively by othello.board.
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

# Allow running this file directly (python evaluation/profile_iterative_deepening.py)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from minimax.algorithm import iterative_deepening
from othello.board import Board


HEURISTICS = ("dynamic", "static", "greedy")
TIME_LIMIT = 0.95
MAX_DEPTH = 60
PLAYER_COLOR = -1
REPEATS = 20
OPENING_PLIES = 12
SEED = 42
OUTPUT_DIR = Path("evaluation/results/profiles")


def build_board(opening_plies: int, seed: int) -> Board:
    random.seed(seed)
    board = Board()
    current_player = 1

    for _ in range(max(0, opening_plies)):
        valid_moves = board.get_valid_moves(current_player)
        if not valid_moves:
            opponent_moves = board.get_valid_moves(-current_player)
            if not opponent_moves:
                break
            current_player *= -1
            continue

        move = random.choice(valid_moves)
        board.make_move(move[0], move[1], current_player)
        current_player *= -1

    return board


def profile_iterative_deepening(heuristic_type: str, output_path: Path) -> Path:
    board = build_board(OPENING_PLIES, SEED)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    profiler = cProfile.Profile()

    profiler.enable()
    for _ in range(max(1, REPEATS)):
        iterative_deepening(
            board,
            player_color=PLAYER_COLOR,
            time_limit=TIME_LIMIT,
            max_depth=MAX_DEPTH,
            heuristic_type=heuristic_type,
        )
    profiler.disable()

    profiler.dump_stats(str(output_path))
    return output_path


def main() -> None:
    saved_profiles = []
    for heuristic_type in HEURISTICS:
        output_path = OUTPUT_DIR / f"iterative_deepening_{heuristic_type}.prof"
        saved_profiles.append(profile_iterative_deepening(heuristic_type, output_path))

    print("Profiles saved to:")
    for output_path in saved_profiles:
        print(f"- {output_path}")
    print("Open with:")
    for output_path in saved_profiles:
        print(f"snakeviz {output_path}")


if __name__ == "__main__":
    main()

