"""
Claude subprocess wrapper.
Appelle claude CLI via subprocess — utilise le quota Claude Max, pas l'API.
"""

import subprocess
import json
import re


def ask(prompt: str, system: str = None, timeout: int = 180) -> str:
    """Appelle Claude et retourne la réponse texte brute."""
    cmd = ["claude", "--print", "--dangerously-skip-permissions"]
    if system:
        cmd += ["--system-prompt", system]

    try:
        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Claude timeout after {timeout}s")

    if result.returncode != 0:
        raise RuntimeError(f"Claude error: {result.stderr.strip()}")

    return result.stdout.strip()


def ask_json(prompt: str, system: str = None, timeout: int = 180) -> dict:
    """Appelle Claude et parse la réponse JSON."""
    json_prompt = prompt + "\n\nIMPORTANT: Respond with valid JSON only. No markdown, no explanation, no code blocks."
    raw = ask(json_prompt, system=system, timeout=timeout)

    # Strip markdown si présent
    raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    raw = re.sub(r"\s*```$", "", raw.strip())

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Claude returned invalid JSON: {e}\nRaw: {raw[:500]}")
