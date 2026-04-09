"""
Fitness assessment — Évaluation LLM de la progression vers l'objectif.
Pour des tâches non-quantifiables, Claude juge lui-même si ça progresse.

Statuts possibles:
  PROGRESS   — avancement réel mesurable
  STAGNANT   — cycle sans avancement réel
  BLOCKED    — bloqué, besoin d'une nouvelle approche
  DONE       — objectif atteint
"""

import json

import llm

VALID_STATUSES = {"PROGRESS", "STAGNANT", "BLOCKED", "DONE"}


def assess(
    objective: dict,
    sub_goal: str,
    action_taken: dict,
    action_result: str,
    cycle_history: list,
    genome: dict,
) -> dict:
    """
    Évalue le résultat d'un cycle.
    Retourne: {status, score (0-10), reason, evidence, next_focus}
    """
    system = genome["system_role"]
    criteria = genome.get("fitness_criteria", [])

    history_summary = _summarize_history(cycle_history[-10:])  # derniers 10 cycles

    prompt = f"""You are assessing your own progress as Genesis (generation {genome['generation']}).

OBJECTIVE: {objective['goal']}
SUCCESS CRITERIA: {json.dumps(objective.get('success_criteria', []))}
CURRENT SUB-GOAL: {sub_goal}

FITNESS CRITERIA: {json.dumps(criteria)}

ACTION TAKEN:
{json.dumps(action_taken, indent=2)}

ACTION RESULT:
{action_result[:3000]}

RECENT HISTORY (last cycles):
{history_summary}

Assess honestly:
1. Did this action produce tangible progress toward the objective?
2. Is the sub-goal advancing or stuck?
3. Is the overall objective closer to completion?

Be STRICT. Do not claim PROGRESS unless there is concrete evidence.

Respond with JSON:
{{
  "status": "PROGRESS|STAGNANT|BLOCKED|DONE",
  "score": <0-10, where 10=objective complete>,
  "reason": "honest one-sentence assessment",
  "evidence": "concrete evidence of progress (or lack thereof)",
  "next_focus": "what to focus on next cycle"
}}"""

    result = llm.ask_json(prompt, system=system)

    # Validation du statut
    if result.get("status") not in VALID_STATUSES:
        result["status"] = "STAGNANT"

    return result


def _summarize_history(cycles: list) -> str:
    if not cycles:
        return "(no history yet)"
    lines = []
    for c in cycles:
        lines.append(
            f"  Cycle {c.get('cycle_id', '?')}: {c.get('action_type', '?')} → "
            f"{c.get('fitness_status', '?')} (score {c.get('fitness_score', '?')})"
        )
    return "\n".join(lines)
