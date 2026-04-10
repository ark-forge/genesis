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
    current_phase: str = None,
) -> dict:
    """
    Évalue le résultat d'un cycle contre la phase développementale courante.
    Retourne: {status, score (0-10), reason, evidence, next_focus, capability_gained}
    """
    system = genome["system_role"]
    criteria = genome.get("fitness_criteria", [])

    # Phase courante
    phases = genome.get("developmental_phases", [])
    phase_id = current_phase or genome.get("current_phase", "orient")
    phase = next((p for p in phases if p["id"] == phase_id), None)

    # Inventaire de capacités actuel
    capability_inventory = genome.get("capability_inventory", {})

    # Novelty check — est-ce que cette action a déjà été tentée ?
    novelty_warning = _check_novelty(action_taken, cycle_history)

    history_summary = _summarize_history(cycle_history[-10:])

    prompt = f"""You are assessing your own progress as Genesis (generation {genome['generation']}).

═══ CURRENT PHASE: {phase_id.upper()} ═══
Question: {phase.get('question', '') if phase else ''}
Done when: {phase.get('done_when', '') if phase else ''}
ZPD constraint: {phase.get('zpd_constraint', '') if phase else ''}

OBJECTIVE (for this phase): {objective['goal']}
SUCCESS CRITERIA: {json.dumps(objective.get('success_criteria', []))}
CURRENT SUB-GOAL: {sub_goal}

FITNESS CRITERIA: {json.dumps(criteria)}

CAPABILITY INVENTORY (before this action):
{json.dumps(capability_inventory, indent=2) if capability_inventory else "(empty)"}

NOVELTY CHECK: {novelty_warning}

ACTION TAKEN:
{json.dumps(action_taken, indent=2)}

ACTION RESULT:
{action_result[:3000]}

RECENT HISTORY:
{history_summary}

Assess against the CURRENT PHASE done_when criterion — NOT the terminal goal directly.

Rules:
- DONE: the phase done_when criterion is fully met
- PROGRESS: the action concretely advanced toward done_when
- STAGNANT: no real advancement, OR action was already tried before
- BLOCKED: phase gate is unpassable with current capability_inventory

Be STRICT. Repetition of a known-failed action = STAGNANT immediately.

Respond with JSON:
{{
  "status": "PROGRESS|STAGNANT|BLOCKED|DONE",
  "score": <0-10, where 10=phase criterion fully met>,
  "reason": "honest one-sentence assessment against phase done_when",
  "evidence": "concrete evidence (or lack thereof)",
  "next_focus": "what to do differently next cycle",
  "capability_gained": "if a new capability was demonstrated, describe it for capability_inventory (null if none)"
}}"""

    result = llm.ask_json(prompt, system=system)

    if result.get("status") not in VALID_STATUSES:
        result["status"] = "STAGNANT"

    return result


def _check_novelty(action_taken: dict, cycle_history: list) -> str:
    """Vérifie si cette action a déjà été tentée dans les cycles récents."""
    if not cycle_history:
        return "First occurrence — novel."

    action_type = action_taken.get("type", "")
    action_params = json.dumps(action_taken.get("params", {}), sort_keys=True)

    repetitions = 0
    for c in cycle_history[-15:]:
        past_type = c.get("action_type", "")
        past_params = json.dumps(c.get("action_params", {}), sort_keys=True)
        if past_type == action_type and past_params == action_params:
            repetitions += 1

    if repetitions == 0:
        return "Novel action — not seen in recent history."
    elif repetitions == 1:
        return f"WARNING: This exact action was tried once before — consider a variation."
    else:
        return f"REPETITION DETECTED: This action was tried {repetitions} times — this is STAGNANT by definition."


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
