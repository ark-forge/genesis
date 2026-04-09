"""
Actions — Registry et exécuteur.
Claude propose une action structurée, l'executor la lance.

Types d'actions disponibles:
  shell        — commande bash
  file_write   — écrire un fichier
  file_read    — lire un fichier
  web_fetch    — récupérer une URL (curl)
  llm_reason   — sous-tâche de raisonnement déléguée à Claude
  memory_query — interroger la mémoire sémantique
  self_modify  — proposer une mutation du génome (déclenche evolver)
"""

import json
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

import llm


def propose(
    objective: dict,
    sub_goal: str,
    genome: dict,
    memory_context: str,
    last_result: str = None,
    next_focus: str = None,
) -> dict:
    """
    Demande à Claude de proposer la prochaine action.
    Retourne un dict {type, params, rationale}.
    """
    system = genome["system_role"]
    strategies = json.dumps(genome["strategies"], indent=2)
    action_prefs = json.dumps(genome["action_preferences"], indent=2)

    prompt = f"""You are Genesis (generation {genome['generation']}).

OBJECTIVE: {objective['goal']}
CURRENT SUB-GOAL: {sub_goal}
NEXT FOCUS: {next_focus or "advance toward sub-goal"}

YOUR STRATEGIES: {strategies}
ACTION PREFERENCES: {action_prefs}

RECENT MEMORY:
{memory_context or "(none)"}

LAST ACTION RESULT:
{last_result[:2000] if last_result else "(first action)"}

Available action types:
- shell: run a bash command. params: {{"command": "..."}}
- file_write: write content to a file. params: {{"path": "...", "content": "..."}}
- file_read: read a file. params: {{"path": "..."}}
- web_fetch: fetch a URL. params: {{"url": "..."}}
- llm_reason: delegate reasoning to Claude. params: {{"prompt": "...", "context": "..."}}
- memory_query: search semantic memory. params: {{"query": "..."}}
- self_modify: request genome mutation. params: {{"reason": "...", "suggested_strategy": "..."}}

Choose ONE action that best advances the current sub-goal.
Prefer concrete actions (shell, file_write) over pure reasoning.

Respond with JSON:
{{
  "type": "<action_type>",
  "params": {{...}},
  "rationale": "why this action advances the sub-goal"
}}"""

    return llm.ask_json(prompt, system=system)


def execute(action: dict, genome: dict) -> str:
    """
    Exécute une action et retourne le résultat sous forme de texte.
    """
    atype = action.get("type")
    params = action.get("params", {})

    if atype == "shell":
        return _run_shell(params.get("command", ""))

    elif atype == "file_write":
        return _file_write(params.get("path", ""), params.get("content", ""))

    elif atype == "file_read":
        return _file_read(params.get("path", ""))

    elif atype == "web_fetch":
        return _web_fetch(params.get("url", ""))

    elif atype == "llm_reason":
        return _llm_reason(params.get("prompt", ""), params.get("context", ""), genome)

    elif atype == "memory_query":
        # Retourné comme signal — memory.py gère la recherche réelle
        return f"MEMORY_QUERY: {params.get('query', '')}"

    elif atype == "self_modify":
        # Signal pour le kernel — ne pas exécuter ici
        return f"SELF_MODIFY_REQUESTED: {params.get('reason', '')} | suggestion: {params.get('suggested_strategy', '')}"

    else:
        return f"ERROR: Unknown action type '{atype}'"


# ── Executors ──────────────────────────────────────────────────────────────────

def _run_shell(command: str) -> str:
    if not command.strip():
        return "ERROR: empty command"
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
            cwd="/tmp/genesis_workspace",
        )
        out = result.stdout + result.stderr
        return out[:4000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "ERROR: command timed out (60s)"
    except Exception as e:
        return f"ERROR: {e}"


def _file_write(path: str, content: str) -> str:
    if not path:
        return "ERROR: no path provided"
    # Sandbox: tout dans /tmp/genesis_workspace
    p = Path("/tmp/genesis_workspace") / path.lstrip("/")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Written {len(content)} chars to {p}"


def _file_read(path: str) -> str:
    if not path:
        return "ERROR: no path provided"
    p = Path("/tmp/genesis_workspace") / path.lstrip("/")
    if not p.exists():
        # Essayer chemin absolu (lecture seule pour exploration)
        p2 = Path(path)
        if p2.exists() and p2.is_file():
            return p2.read_text(encoding="utf-8")[:4000]
        return f"ERROR: file not found: {path}"
    return p.read_text(encoding="utf-8")[:4000]


def _web_fetch(url: str) -> str:
    if not url:
        return "ERROR: no URL provided"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Genesis/0.1"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode("utf-8", errors="replace")
            return content[:4000]
    except urllib.error.URLError as e:
        return f"ERROR fetching {url}: {e}"


def _llm_reason(prompt: str, context: str, genome: dict) -> str:
    if not prompt:
        return "ERROR: no prompt for llm_reason"
    full_prompt = f"{context}\n\n{prompt}" if context else prompt
    return llm.ask(full_prompt, system=genome["system_role"])
