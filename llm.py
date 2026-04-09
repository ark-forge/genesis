"""
Claude subprocess wrapper.
Appelle claude CLI via subprocess — utilise le quota Claude Max, pas l'API.
"""

import subprocess
import json
import re


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

    # --output-format json retourne un objet JSON avec le champ "result"
    raw = result.stdout.strip()
    try:
        envelope = json.loads(raw)
        if isinstance(envelope, dict):
            # Extraire le champ texte selon la structure retournée
            text = envelope.get("result") or envelope.get("content") or envelope.get("text") or raw
            return text.strip() if isinstance(text, str) else raw
    except json.JSONDecodeError:
        pass

    return raw


def ask_json(prompt: str, system: str = None, timeout: int = 180) -> dict:
    """Appelle Claude et parse la réponse JSON."""
    json_prompt = (
        prompt
        + "\n\nCRITICAL INSTRUCTION: Your entire response must be a single valid JSON object. "
        "Do not include any text, explanation, markdown, or code blocks. "
        "Start your response with { and end with }."
    )
    raw = ask(json_prompt, system=system, timeout=timeout)

    # Tentative 1 : parse direct
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Tentative 2 : extraire bloc ```json ... ```
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Tentative 3 : extraire premier { ... } de profondeur 0
    extracted = _extract_first_json_object(raw)
    if extracted:
        try:
            return json.loads(extracted)
        except json.JSONDecodeError:
            pass

    raise RuntimeError(
        f"Claude returned invalid JSON.\nRaw (first 600 chars): {raw[:600]}"
    )


def _extract_first_json_object(text: str) -> str | None:
    """Extrait le premier objet JSON valide d'un texte quelconque."""
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
