"""
Objective — Génération autonome et décomposition d'objectifs.
Le système génère ses propres objectifs si aucun n'est fourni.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import llm

OBJECTIVE_LOG = Path("brain/objective_log.jsonl")


def generate(genome: dict, memory_context: str = "", current_phase: str = None) -> dict:
    """
    Génère un objectif autonome contraint à la phase développementale courante.
    Retourne un dict avec 'goal', 'success_criteria', 'rationale'.
    """
    system = genome["system_role"]
    ethical_constraints = genome.get("ethical_constraints", [])
    capability_inventory = genome.get("capability_inventory", {})
    intrinsic_motivations = genome.get("intrinsic_motivations", {})
    critical_rule = genome.get("critical_rule", {})
    strategies = genome.get("strategies", [])

    # Phase courante
    phases = genome.get("developmental_phases", [])
    phase_id = current_phase or genome.get("current_phase", "orient")
    phase = next((p for p in phases if p["id"] == phase_id), None)

    # Niveau de goal courant
    goal_level = genome.get("current_goal_level", 1)
    ladder = genome.get("goal_ladder", [])
    current_goal = next((g for g in ladder if g["level"] == goal_level), {})

    prompt = f"""You are Genesis (generation {genome['generation']}).

═══ TERMINAL GOAL (north star — do not optimize directly) ═══
Level {goal_level}: {current_goal.get('description', '')}
Unlocks: {current_goal.get('unlocks', '')}

═══ CURRENT DEVELOPMENTAL PHASE ═══
Phase: {phase_id.upper()}
Question to answer: {phase.get('question', '') if phase else ''}
Done when: {phase.get('done_when', '') if phase else ''}
ZPD constraint: {phase.get('zpd_constraint', '') if phase else ''}

You are ONLY working on this phase. Do not skip ahead.

═══ YOUR CAPABILITY INVENTORY ═══
{json.dumps(capability_inventory, indent=2) if capability_inventory else "(empty — this is what orient phase is for)"}

═══ INTRINSIC MOTIVATIONS ═══
{json.dumps(intrinsic_motivations, indent=2)}

═══ CRITICAL RULE ═══
Before acting: {json.dumps(critical_rule.get('before_acting', []))}

═══ ETHICAL CONSTRAINTS (non-negotiable) ═══
{json.dumps(ethical_constraints, indent=2)}

═══ CURRENT STRATEGIES (from experience) ═══
{json.dumps(strategies, indent=2) if strategies else "(none yet — strategies emerge from mutations)"}

═══ MEMORY CONTEXT ═══
{memory_context or "(no prior memory)"}

Generate ONE objective that advances the CURRENT PHASE.
The objective must satisfy the phase's done_when criterion — not the terminal goal directly.
Stay within the ZPD constraint.

Respond with JSON:
{{
  "goal": "precise description of what you will do to advance phase '{phase_id}'",
  "phase_criterion": "which done_when criterion this objective targets",
  "success_criteria": ["criterion 1", "criterion 2", ...],
  "capability_gained": "what new capability_inventory entry this will produce",
  "rationale": "why this is in the ZPD and advances the current phase",
  "estimated_cycles": <integer, 1-5>
}}"""

    result = llm.ask_json(prompt, system=system)
    result["generated_at"] = datetime.now(timezone.utc).isoformat()
    result["status"] = "active"
    result["genome_generation"] = genome["generation"]
    result["phase"] = phase_id

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
