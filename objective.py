"""
Objective — Génération autonome et décomposition d'objectifs.
Le système génère ses propres objectifs si aucun n'est fourni.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import llm

OBJECTIVE_LOG = Path("brain/objective_log.jsonl")


def generate(genome: dict, memory_context: str = "") -> dict:
    """
    Génère un objectif autonome basé sur le génome et la mémoire.
    Retourne un dict avec 'goal', 'success_criteria', 'rationale'.
    """
    system = genome["system_role"]
    prompt = f"""You are Genesis (generation {genome['generation']}).
Your current strategies: {json.dumps(genome['strategies'], indent=2)}
Your objective style: {genome['objective_style']}

Recent memory context:
{memory_context or "(no prior memory — this is your first cycle)"}

Generate ONE objective for yourself to pursue RIGHT NOW.
The objective must be:
- Concrete and achievable within multiple action cycles
- Meaningful (produces real knowledge, code, insight, or artifact)
- Ambitious enough to require at least 5 action cycles
- Not previously completed (check memory context)

Respond with JSON:
{{
  "goal": "precise description of what you will achieve",
  "success_criteria": ["criterion 1", "criterion 2", ...],
  "rationale": "why this objective is valuable right now",
  "estimated_cycles": <integer>
}}"""

    result = llm.ask_json(prompt, system=system)
    result["generated_at"] = datetime.now(timezone.utc).isoformat()
    result["status"] = "active"
    result["genome_generation"] = genome["generation"]

    _log_objective(result)
    return result


def decompose(objective: dict, genome: dict, completed_sub_goals: list) -> list:
    """
    Décompose l'objectif en sous-buts ordonnés.
    Retourne une liste de sous-buts, en tenant compte de ce qui est déjà fait.
    """
    system = genome["system_role"]
    prompt = f"""Objective: {objective['goal']}
Success criteria: {json.dumps(objective.get('success_criteria', []))}
Already completed sub-goals: {json.dumps(completed_sub_goals)}

Decompose this objective into ordered sub-goals.
Each sub-goal should be completable in 1-3 action cycles.
Skip any already completed sub-goals.

Respond with JSON:
{{
  "sub_goals": [
    {{"id": "sg_1", "description": "...", "depends_on": []}},
    ...
  ],
  "next_sub_goal": "sg_1"
}}"""

    return llm.ask_json(prompt, system=system)


def mark_complete(objective: dict, outcome: str) -> None:
    """Marque un objectif comme terminé dans le log."""
    objective["status"] = "completed"
    objective["completed_at"] = datetime.now(timezone.utc).isoformat()
    objective["outcome"] = outcome
    _log_objective(objective)


def _log_objective(obj: dict) -> None:
    OBJECTIVE_LOG.parent.mkdir(parents=True, exist_ok=True)
    with OBJECTIVE_LOG.open("a") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")
