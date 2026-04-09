"""
Claude subprocess wrapper.
Appelle claude CLI via subprocess — utilise le quota Claude Max, pas l'API.
"""

import subprocess
import json
import re
import time


def ask(prompt: str, system: str = None, timeout: int = 180) -> str:
    """Appelle Claude et retourne la réponse texte brute."""
    cmd = [
        "claude",
        "--print",
        "--output-format", "json",
        "--dangerously-skip-permissions",
    ]

    full_prompt = prompt
    if system:
        full_prompt = f"<system>{system}</system>\n\n{prompt}"

    try:
        result = subprocess.run(
            cmd,
            input=full_prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Claude timeout after {timeout}s")

    if result.returncode != 0:
        raise RuntimeError(f"Claude error: {result.stderr.strip()}")

    raw = result.stdout.strip()
    try:
        envelope = json.loads(raw)
        if isinstance(envelope, dict):
            text = (
                envelope.get("result")
                or envelope.get("content")
                or envelope.get("text")
                or raw
            )
            return text.strip() if isinstance(text, str) else raw
    except json.JSONDecodeError:
        pass

    return raw


def ask_json(prompt: str, system: str = None, timeout: int = 180, retries: int = 3) -> dict:
    """
    Appelle Claude et parse la réponse JSON.
    Retry automatique avec prompt simplifié si JSON invalide.
    Ne lève jamais d'exception — retourne un dict d'erreur en dernier recours.
    """
    last_error = None

    for attempt in range(retries):
        if attempt == 0:
            json_prompt = (
                prompt
                + "\n\nCRITICAL: Respond with a single valid JSON object only. "
                "Start with { and end with }. No markdown, no explanation."
            )
        elif attempt == 1:
            # Prompt épuré — on retire le contexte lourd
            json_prompt = (
                "Based on the following task, respond with ONLY a JSON object:\n\n"
                + _truncate_prompt(prompt, 800)
                + "\n\nJSON response:"
            )
        else:
            # Dernier essai : prompt minimal
            json_prompt = (
                "Respond with a minimal valid JSON object for this task: "
                + _truncate_prompt(prompt, 400)
            )

        try:
            raw = ask(json_prompt, system=system, timeout=timeout)
            result = _extract_json(raw)
            if result is not None:
                return result
            last_error = f"No JSON found in response: {raw[:200]}"
        except Exception as e:
            last_error = str(e)

        if attempt < retries - 1:
            time.sleep(2 ** attempt)  # backoff: 1s, 2s

    # Dernier recours : retourner un dict d'erreur pour ne pas crasher le kernel
    return {
        "_llm_error": True,
        "_error_msg": last_error or "unknown",
        "_fallback": True,
    }


def _extract_json(raw: str) -> dict | None:
    """Tente d'extraire un JSON valide d'un texte quelconque."""
    if not raw or not raw.strip():
        return None

    # Tentative 1 : parse direct
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Tentative 2 : bloc ```json ... ```
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Tentative 3 : trouver le premier { ... } de niveau 0
    extracted = _extract_first_brace_object(raw)
    if extracted:
        try:
            return json.loads(extracted)
        except json.JSONDecodeError:
            pass

    return None


def _extract_first_brace_object(text: str) -> str | None:
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    in_string = False
    escape_next = False
    for i, ch in enumerate(text[start:], start):
        if escape_next:
            escape_next = False
            continue
        if ch == "\\" and in_string:
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def _truncate_prompt(prompt: str, max_chars: int) -> str:
    if len(prompt) <= max_chars:
        return prompt
    return prompt[:max_chars] + "...[truncated]"
