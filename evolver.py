"""
Evolver — Moteur de mutation du génome.
Déclenché quand la fitness stagne N cycles consécutifs.
Claude génère une mutation, on archive l'ancien génome et on adopte le nouveau.
"""

import json
import os
from pathlib import Path

import llm
import genome as genome_module
import reflect as reflect_module

# Canonical path for the persistent reflection log (written by reflect.py)
_REFLECTION_LOG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "genesis_workspace", "brain", "reflection_log.json"
)
# Fallback absolute path used when the relative resolution misses
_REFLECTION_LOG_FALLBACK = "/tmp/genesis_workspace/brain/reflection_log.json"

# Paths for fitness scoring artifacts (relative to this file's directory)
_BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
_SESSION_STATE_PATH = _BASE_DIR / "brain" / "session_state.json"
_REFLECTION_LOG_JSONL = _BASE_DIR / "brain" / "reflection_log.jsonl"
_FITNESS_SCORES_PATH = _BASE_DIR / "brain" / "fitness_scores.json"

FITNESS_THRESHOLD = 0.6


def _load_session_state() -> dict:
    """Load brain/session_state.json; return empty dict on failure."""
    try:
        if _SESSION_STATE_PATH.exists():
            return json.loads(_SESSION_STATE_PATH.read_text())
    except Exception:
        pass
    return {}


def _load_reflection_log_entries() -> list:
    """Load all JSONL entries from brain/reflection_log.jsonl."""
    entries = []
    try:
        if _REFLECTION_LOG_JSONL.exists():
            for line in _REFLECTION_LOG_JSONL.read_text().splitlines():
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except Exception:
                        pass
    except Exception:
        pass
    return entries


def _compute_history_metrics(history: list) -> dict:
    """
    Derive cycle_success_rate, blocked_rate, and done_rate from cycle history.
    history: list of cycle dicts with 'fitness_status' keys.
    """
    if not history:
        return {"cycle_success_rate": 0.5, "blocked_rate": 0.5, "done_rate": 0.0, "total": 0}

    total = len(history)
    progress = sum(1 for c in history if c.get("fitness_status") == "PROGRESS")
    blocked = sum(1 for c in history if c.get("fitness_status") in ("BLOCKED", "STAGNANT"))
    done = sum(1 for c in history if c.get("fitness_status") == "DONE")

    return {
        "cycle_success_rate": progress / total,
        "blocked_rate": blocked / total,
        "done_rate": done / total,
        "total": total,
    }


def score_proposal(proposal: dict, history: list) -> tuple:
    """
    Score a mutation proposal on a 0.0–1.0 scale.

    Sources of truth:
    - history (passed in) — current stagnation cycle records
    - brain/session_state.json — persistent session context
    - brain/reflection_log.jsonl — accumulated reflection patterns

    Scoring formula:
        base_score  = cycle_success_rate * 0.3
                    + (1 - blocked_rate)  * 0.3
                    + done_rate           * 0.2
        confidence_weight = proposal.get("confidence", 0.5)
        final = base_score * 0.7 + confidence_weight * 0.3

    Returns:
        (score: float, rationale: str)
    """
    # 1. Derive metrics from live history
    metrics = _compute_history_metrics(history)

    # 2. Supplement with session state if history is thin (<3 cycles)
    if metrics["total"] < 3:
        session = _load_session_state()
        # session_state carries stagnant_cycles as a proxy for blocked_rate
        stagnant = session.get("stagnant_cycles", 0)
        cycle_id = max(session.get("cycle_id", 1), 1)
        session_blocked_rate = min(stagnant / cycle_id, 1.0)
        # Blend: weight session less than direct history
        metrics["blocked_rate"] = (metrics["blocked_rate"] + session_blocked_rate) / 2
        metrics["cycle_success_rate"] = max(0.0, 1.0 - metrics["blocked_rate"])

    # 3. Supplement done_rate from reflection log (count productive entries)
    if metrics["done_rate"] == 0.0:
        entries = _load_reflection_log_entries()
        if entries:
            productive = sum(
                1 for e in entries
                if any(p.get("targets_pattern") for p in e.get("proposals", []))
            )
            metrics["done_rate"] = min(productive / max(len(entries), 1), 1.0) * 0.3

    # 4. Compute base score
    base_score = (
        metrics["cycle_success_rate"] * 0.3
        + (1.0 - metrics["blocked_rate"]) * 0.3
        + metrics["done_rate"] * 0.2
    )
    base_score = max(0.0, min(1.0, base_score))

    # 5. Blend with proposal confidence
    confidence = float(proposal.get("confidence", 0.5))
    confidence = max(0.0, min(1.0, confidence))
    final_score = base_score * 0.7 + confidence * 0.3
    final_score = round(max(0.0, min(1.0, final_score)), 4)

    # 6. Build rationale
    rationale = (
        f"Metrics over {metrics['total']} cycles — "
        f"success_rate={metrics['cycle_success_rate']:.2f}, "
        f"blocked_rate={metrics['blocked_rate']:.2f}, "
        f"done_rate={metrics['done_rate']:.2f}; "
        f"proposal confidence={confidence:.2f}; "
        f"base={base_score:.4f}, final={final_score:.4f}"
    )

    return final_score, rationale


def _write_fitness_scores(scored_entries: list):
    """
    Append scored proposals to brain/fitness_scores.json.
    MUT-G36-003: atomic_write_then_verify_same_cycle — immediately
    reads back the written file and confirms entry count matches expectation.
    Raises RuntimeError if verification fails, preventing silent corruption.
    """
    existing = []
    if _FITNESS_SCORES_PATH.exists():
        try:
            existing = json.loads(_FITNESS_SCORES_PATH.read_text())
        except Exception:
            existing = []
    expected_count = len(existing) + len(scored_entries)
    existing.extend(scored_entries)
    _FITNESS_SCORES_PATH.parent.mkdir(parents=True, exist_ok=True)
    _FITNESS_SCORES_PATH.write_text(json.dumps(existing, indent=2, ensure_ascii=False))

    # MUT-G36-003: verify immediately in same cycle — never trust the write blindly
    try:
        verified = json.loads(_FITNESS_SCORES_PATH.read_text())
        if len(verified) != expected_count:
            raise RuntimeError(
                f"Atomic write verification failed: expected {expected_count} entries, "
                f"got {len(verified)} in {_FITNESS_SCORES_PATH}"
            )
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Atomic write verification failed — JSON parse error: {exc}") from exc


def _load_pending_proposals() -> list:
    """Read mutation_proposals from the reflection log and clear them after consumption."""
    for candidate in (_REFLECTION_LOG_PATH, _REFLECTION_LOG_FALLBACK):
        path = os.path.normpath(candidate)
        if not os.path.exists(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            proposals = data.get("mutation_proposals", [])
            if proposals:
                # Mark proposals consumed so they are not replayed next cycle
                data["mutation_proposals"] = []
                data["proposals_consumed_at"] = (
                    __import__("datetime").datetime.utcnow().isoformat() + "Z"
                )
                with open(path, "w", encoding="utf-8") as fh:
                    json.dump(data, fh, indent=2)
            return proposals
        except Exception:
            pass
    return []


def mutate(genome: dict, stagnation_history: list, objective: dict, reflection: dict = None) -> dict:
    """
    Génère une mutation du génome basée sur l'historique de stagnation.
    Fusionne les proposals en mémoire (reflection) avec ceux stockés dans
    reflection_log.json avant de construire le prompt.
    Score chaque proposal via score_proposal() et n'applique que ceux
    dépassant FITNESS_THRESHOLD (0.6).
    Retourne le nouveau génome (déjà sauvegardé).
    """
    system = genome["system_role"]

    failure_summary = _summarize_failures(stagnation_history)

    # Merge in-memory proposals with any pending ones from the persistent log
    in_memory_proposals = (reflection or {}).get("proposals", [])
    stored_proposals = _load_pending_proposals()
    all_proposals = in_memory_proposals + [p for p in stored_proposals if p not in in_memory_proposals]

    # --- Fitness gate: score each proposal and record results ---
    import datetime as _dt
    scored_records = []
    accepted_proposals = []
    for i, prop in enumerate(all_proposals):
        score, rationale = score_proposal(prop, stagnation_history)
        accepted = score >= FITNESS_THRESHOLD
        scored_records.append({
            "proposal_id": f"prop_{_dt.datetime.utcnow().strftime('%Y%m%dT%H%M%S')}_{i}",
            "score": score,
            "rationale": rationale,
            "accepted": accepted,
            "proposal_summary": prop.get("description", "")[:120],
            "targets_pattern": prop.get("targets_pattern", ""),
            "confidence": prop.get("confidence", 0.5),
        })
        if accepted:
            accepted_proposals.append(prop)

    if scored_records:
        _write_fitness_scores(scored_records)
        n_accepted = len(accepted_proposals)
        n_total = len(scored_records)
        print(f"  [Fitness gate] {n_accepted}/{n_total} proposals accepted (threshold={FITNESS_THRESHOLD})")

    # Use only accepted proposals for the LLM hint; fall back to all if none pass
    filtered_proposals = accepted_proposals if accepted_proposals else all_proposals

    reflection_hint = ""
    if filtered_proposals:
        gate_note = ""
        if scored_records and not accepted_proposals:
            gate_note = " [all below threshold — included as reference only]"
        source_note = f" ({len(stored_proposals)} from reflection_log.json)" if stored_proposals else ""
        reflection_hint = (
            f"\n\nSELF-REFLECTION PROPOSALS (from analyze_history{source_note}{gate_note} — prioritize these):\n"
            + json.dumps(filtered_proposals, indent=2)
        )

    # Bias strategy selection toward historically high-success strategies
    strategy_weights = genome.get("strategy_weights", {})
    if strategy_weights:
        top_weighted = sorted(strategy_weights.items(), key=lambda x: x[1], reverse=True)[:5]
        reflection_hint += (
            "\n\nSTRATEGY WEIGHTS (from self-reflection history — prefer high-weight strategies):\n"
            + "\n".join(f"  {s}: {w:.4f}" for s, w in top_weighted)
        )

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
- Explain why each change will help{reflection_hint}

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
    # Protéger les champs structurels ET l'immutable_core
    immutable_core_keys = set(genome.get("immutable_core", []))
    protected = {"generation", "parent_generation", "created_at", "mutation_history"} | immutable_core_keys
    mutation_scope = genome.get("mutation_scope", "strategies_only")

    # En mode strategies_only, seuls strategies et system_role peuvent muter
    if mutation_scope == "strategies_only":
        allowed_mutation_keys = {"strategies", "system_role", "stagnation_threshold",
                                 "action_preferences", "fitness_criteria", "strategy_weights",
                                 "mutation_reason"}
    else:
        allowed_mutation_keys = None  # tout sauf protected

    for key, value in mutation.items():
        if key in protected:
            continue
        if allowed_mutation_keys is not None and key not in allowed_mutation_keys:
            continue
        genome[key] = value

    # Distill reflection insights and update strategy_weights before committing
    try:
        insights = reflect_module.distill_insights()
        genome["strategy_weights"] = insights.get("strategy_weights", {})
    except Exception:
        pass  # distillation is non-blocking

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
