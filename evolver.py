"""
Evolver — Moteur de mutation du génome.
Déclenché quand la fitness stagne N cycles consécutifs.
Claude génère une mutation, on archive l'ancien génome et on adopte le nouveau.
"""

import json

import llm
import genome as genome_module


def mutate(genome: dict, stagnation_history: list, objective: dict) -> dict:
    """
    Génère une mutation du génome basée sur l'historique de stagnation.
    Retourne le nouveau génome (déjà sauvegardé).
    """
    system = genome["system_role"]

    failure_summary = _summarize_failures(stagnation_history)

    prompt = f"""You are Genesis (generation {genome['generation']}) and you are STUCK.

CURRENT OBJECTIVE: {objective['goal']}

STAGNATION HISTORY (last {len(stagnation_history)} cycles without progress):
{failure_summary}

CURRENT GENOME:
{json.dumps(genome, indent=2)}

You must EVOLVE. Generate a mutated genome that will break the stagnation.
You can:
- Change your strategies (remove failing ones, add new ones)
- Change your action_preferences
- Change your objective_style
- Change your fitness_criteria
- Change your system_role (be careful — small changes only)

Rules:
- Keep the JSON structure identical
- Do NOT change: generation, parent_generation, created_at, mutation_history
- At least 1 strategy must change
- Explain why each change will help

Respond with JSON containing the full mutated genome fields to UPDATE
(only include fields you want to change, except structural fields):
{{
  "system_role": "...",
  "strategies": [...],
  "action_preferences": {{...}},
  "objective_style": "...",
  "fitness_criteria": [...],
  "stagnation_threshold": <int>,
  "mutation_reason": "why these changes will break the stagnation"
}}"""

    mutation = llm.ask_json(prompt, system=system)
    reason = mutation.pop("mutation_reason", "stagnation-driven mutation")

    # Appliquer la mutation sur le génome courant
    protected = {"generation", "parent_generation", "created_at", "mutation_history"}
    for key, value in mutation.items():
        if key not in protected:
            genome[key] = value

    # Commit avec versioning
    new_genome = genome_module.commit_mutation(genome, reason)

    return new_genome


def _summarize_failures(history: list) -> str:
    if not history:
        return "(no history)"
    lines = []
    for c in history:
        lines.append(
            f"  Cycle {c.get('cycle_id', '?')}: "
            f"action={c.get('action_type', '?')}, "
            f"status={c.get('fitness_status', '?')}, "
            f"reason={c.get('fitness_reason', '?')}"
        )
    return "\n".join(lines)
