"""
Audit — Log structuré de chaque cycle.
Format JSONL pour permettre parsing, grep, visualisation.
Chaque événement est aussi affiché en console pour suivi temps réel.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG_PATH = Path("logs/cycles.jsonl")
EVENT_LOG = Path("logs/events.jsonl")


def log_cycle(cycle: dict) -> None:
    """Enregistre un cycle complet dans le log d'audit."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    cycle["logged_at"] = datetime.now(timezone.utc).isoformat()
    with LOG_PATH.open("a") as f:
        f.write(json.dumps(cycle, ensure_ascii=False) + "\n")


def log_event(event_type: str, data: dict) -> None:
    """Enregistre un événement système (mutation, objectif, erreur...)."""
    EVENT_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event_type,
        **data,
    }
    with EVENT_LOG.open("a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    _print_event(event_type, entry)


def _print_event(event_type: str, data: dict) -> None:
    ts = data.get("timestamp", "")[:19]
    print(f"\n[{ts}] ◆ {event_type.upper()}", flush=True)


def print_cycle(cycle: dict) -> None:
    """Affiche un résumé lisible du cycle en console."""
    cid = cycle.get("cycle_id", "?")
    gen = cycle.get("genome_generation", "?")
    atype = cycle.get("action_type", "?")
    status = cycle.get("fitness_status", "?")
    score = cycle.get("fitness_score", "?")
    reason = cycle.get("fitness_reason", "")
    stagnant = cycle.get("stagnant_cycles", 0)
    mutated = " [GENOME MUTATED]" if cycle.get("genome_mutated") else ""

    status_icon = {"PROGRESS": "✓", "STAGNANT": "~", "BLOCKED": "✗", "DONE": "★"}.get(status, "?")

    print(
        f"\n{'─'*60}\n"
        f"Cycle {cid:>4} | Gen {gen} | Action: {atype}\n"
        f"Fitness: {status_icon} {status} (score {score}/10) | Stagnant: {stagnant}\n"
        f"Reason: {reason}{mutated}\n",
        flush=True,
    )


def print_header(objective: dict, genome: dict) -> None:
    print(
        f"\n{'═'*60}\n"
        f"GENESIS — Generation {genome.get('generation', 0)}\n"
        f"Objective: {objective.get('goal', '?')}\n"
        f"{'═'*60}",
        flush=True,
    )
