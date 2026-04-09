"""
Memory — Mémoire épisodique + sémantique.

Épisodique : log de tous les cycles (ce qui s'est passé)
Sémantique  : patterns extraits de l'histoire (ce qui marche)
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import llm

EPISODIC_LOG = Path("brain/memory.jsonl")
SEMANTIC_PATH = Path("brain/semantic_memory.json")


def record(cycle: dict) -> None:
    """Enregistre un cycle dans la mémoire épisodique."""
    EPISODIC_LOG.parent.mkdir(parents=True, exist_ok=True)
    with EPISODIC_LOG.open("a") as f:
        f.write(json.dumps(cycle, ensure_ascii=False) + "\n")


def reinforce(action: dict, result: str, fitness: dict, genome: dict) -> None:
    """
    Extrait un pattern sémantique d'un cycle réussi et l'ajoute à la mémoire sémantique.
    Appelé uniquement quand fitness.status == PROGRESS.
    """
    semantic = _load_semantic()

    prompt = f"""A successful action was taken. Extract a reusable pattern.

Action: {json.dumps(action)}
Result (excerpt): {result[:1000]}
Fitness assessment: {json.dumps(fitness)}

Extract ONE reusable pattern or heuristic that future cycles should remember.
Keep it concise (1-2 sentences).

Respond with JSON:
{{
  "pattern": "...",
  "applies_when": "...",
  "confidence": <0.0-1.0>
}}"""

    try:
        pattern = llm.ask_json(prompt, system=genome["system_role"])
        pattern["recorded_at"] = datetime.now(timezone.utc).isoformat()
        pattern["genome_generation"] = genome.get("generation", 0)
        semantic.setdefault("patterns", []).append(pattern)
        # Garder les 100 patterns les plus récents
        semantic["patterns"] = semantic["patterns"][-100:]
        _save_semantic(semantic)
    except Exception:
        pass  # Mémoire sémantique non critique


def get_context(objective: dict, n_recent: int = 5, n_patterns: int = 5) -> str:
    """
    Retourne un résumé du contexte mémoire pertinent pour l'objectif courant.
    """
    lines = []

    # Cycles récents
    recent = _load_recent_episodes(n_recent)
    if recent:
        lines.append("=== Recent cycles ===")
        for ep in recent:
            lines.append(
                f"Cycle {ep.get('cycle_id', '?')}: {ep.get('action_type', '?')} "
                f"[{ep.get('fitness_status', '?')}] — {ep.get('fitness_reason', '')}"
            )

    # Patterns sémantiques
    semantic = _load_semantic()
    patterns = semantic.get("patterns", [])[-n_patterns:]
    if patterns:
        lines.append("\n=== Learned patterns ===")
        for p in patterns:
            lines.append(f"• {p.get('pattern', '')} (when: {p.get('applies_when', '')})")

    return "\n".join(lines) if lines else ""


def query(query_str: str, genome: dict) -> str:
    """Recherche sémantique dans la mémoire (pour l'action memory_query)."""
    semantic = _load_semantic()
    patterns = semantic.get("patterns", [])
    if not patterns:
        return "No semantic memory yet."

    prompt = f"""Query: {query_str}

Available patterns:
{json.dumps(patterns, indent=2)}

Which patterns are relevant to this query? Summarize the most useful ones in 3-5 sentences."""

    return llm.ask(prompt, system=genome["system_role"])


def _load_recent_episodes(n: int) -> list:
    if not EPISODIC_LOG.exists():
        return []
    lines = EPISODIC_LOG.read_text().strip().splitlines()
    recent = lines[-n:]
    return [json.loads(l) for l in recent if l.strip()]


def _load_semantic() -> dict:
    if not SEMANTIC_PATH.exists():
        return {"patterns": []}
    return json.loads(SEMANTIC_PATH.read_text())


def _save_semantic(data: dict) -> None:
    SEMANTIC_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))
