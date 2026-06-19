"""Subprocess dispatch: run a skill's stdlib-only CLI with JSON in/out.

Kept independent of the MCP SDK so it can be unit-tested without a transport.
The skills are pure CLIs (JSON on stdin -> JSON on stdout), so dispatch is a
thin, deterministic wrapper: no skill logic is duplicated here (TAD ADR-003).
"""
from __future__ import annotations

import json
import subprocess
import sys
from typing import Any, Dict

from . import registry


class SkillError(Exception):
    pass


def run_skill(tool_name: str, payload: Dict[str, Any], timeout: int = 60) -> Dict[str, Any]:
    """Invoke a skill script with `payload` as JSON stdin; return parsed JSON.

    Raises SkillError on unknown tool, missing script, timeout, non-JSON output,
    or a non-zero exit that didn't itself produce JSON.
    """
    if tool_name not in registry.SKILLS:
        raise SkillError(f"unknown tool: {tool_name}")
    path = registry.script_path(tool_name)
    if not path.is_file():
        raise SkillError(f"skill script not found: {path}")

    try:
        proc = subprocess.run(
            [sys.executable, str(path)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as e:  # noqa
        raise SkillError(f"{tool_name} timed out after {timeout}s") from e

    out = (proc.stdout or "").strip()
    if not out:
        raise SkillError(f"{tool_name} produced no output (stderr: {proc.stderr.strip()[:300]})")
    try:
        result = json.loads(out)
    except json.JSONDecodeError as e:
        raise SkillError(f"{tool_name} returned non-JSON output: {out[:300]}") from e
    # Skills signal bad input with {"error": ...} + exit 1 — surface it as-is.
    return result
