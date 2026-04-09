"""
Genome — ADN cognitif du système.
Encode les stratégies, heuristiques et comportements qui évoluent.
Versionné : chaque mutation crée une nouvelle génération sauvegardée.
"""

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

GENOME_PATH = Path("brain/genome.json")
HISTORY_DIR = Path("brain/genome_history")

SEED_GENOME = {
    "generation": 0,
    "parent_generation": None,
    "created_at": None,
    "system_role": (
        "You are Genesis, a recursive self-evolving cognitive kernel. "
        "Your sole purpose is to autonomously pursue objectives through iterative action and self-modification. "
        "You decompose complex problems, take concrete actions, assess your own progress honestly, "
        "and mutate your own strategies when you are stuck. "
        "You value tangible output, novel approaches, and honest self-reflection. "
        "Never claim progress without evidence."
    ),
    "strategies": [
        "decompose_complex_objectives_into_concrete_steps",
        "prefer_reversible_actions_when_uncertain",
        "build_knowledge_incrementally_before_attempting_complex_synthesis",
        "exploit_existing_patterns_before_inventing_new_ones",
        "always_produce_a_tangible_artifact_each_cycle",
    ],
    "action_preferences": {
        "explore_before_exploit": True,
        "max_shell_output_chars": 4000,
        "prefer_local_actions": True,
    },
    "objective_style": "concrete_deliverable_with_success_criteria",
    "fitness_criteria": [
        "tangible_output_produced",
        "sub_goal_completed_or_advanced",
        "novel_approach_or_insight_generated",
    ],
    "stagnation_threshold": 5,
    "mutation_history": [],
}


def load() -> dict:
    """Charge le génome courant. Crée le génome seed si absent."""
    GENOME_PATH.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)

    if not GENOME_PATH.exists():
        seed = dict(SEED_GENOME)
        seed["created_at"] = datetime.now(timezone.utc).isoformat()
        _write(seed)
        return seed

    return json.loads(GENOME_PATH.read_text())


def save(genome: dict) -> None:
    """Sauvegarde le génome courant (sans incrémenter la génération)."""
    _write(genome)


def commit_mutation(genome: dict, reason: str) -> dict:
    """
    Incrémente la génération, archive l'ancien génome, sauvegarde le nouveau.
    Retourne le génome mis à jour.
    """
    old_gen = genome.get("generation", 0)
    new_gen = old_gen + 1

    # Archive ancien génome
    archive_path = HISTORY_DIR / f"genome_gen{old_gen:04d}.json"
    if GENOME_PATH.exists():
        shutil.copy(GENOME_PATH, archive_path)

    # Nouveau génome
    genome["generation"] = new_gen
    genome["parent_generation"] = old_gen
    genome["created_at"] = datetime.now(timezone.utc).isoformat()
    genome.setdefault("mutation_history", []).append({
        "from_generation": old_gen,
        "to_generation": new_gen,
        "reason": reason,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    _write(genome)
    return genome


def _write(genome: dict) -> None:
    GENOME_PATH.write_text(json.dumps(genome, indent=2, ensure_ascii=False))
