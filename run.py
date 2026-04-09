"""
Genesis — Entrypoint.

Usage:
  python run.py                         # objectif auto-généré
  python run.py "your objective here"   # objectif fourni
  python run.py --cycles 20             # limite de cycles
  python run.py "objective" --cycles 50
"""

import argparse
import sys
from pathlib import Path

# S'assurer qu'on est dans le bon répertoire
REPO_ROOT = Path(__file__).parent
import os
os.chdir(REPO_ROOT)

from kernel import Kernel


def main():
    parser = argparse.ArgumentParser(description="Genesis — Self-evolving cognitive kernel")
    parser.add_argument("objective", nargs="?", default=None, help="Objective to pursue (auto-generated if omitted)")
    parser.add_argument("--cycles", type=int, default=None, help="Max cycles (infinite if omitted)")
    args = parser.parse_args()

    k = Kernel(
        initial_objective=args.objective,
        max_cycles=args.cycles,
    )
    k.run()


if __name__ == "__main__":
    main()
