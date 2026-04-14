import subprocess
import os
from pathlib import Path

from constants import WORKDIR, MAXCHARSIZE

TOOL_HANDLERS = {
    "bash":         lambda **kw: run_bash(kw["command"]),
    "read_file":    lambda **kw: run_read(kw["path"], kw.get("limit")),
    "write_file":   lambda **kw: run_write(kw["path"], kw["content"]),
    "edit_file":    lambda **kw: run_edit(kw["path"], kw["old_text"], kw["new_text"]),
}


def run_bash(command: str) -> str:
    dangerous_cmd = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
    if any(d in command for d in dangerous_cmd):
        return "Error: Dangerous command blocked"

    try:
        bash_result = subprocess.run(
            command,
            shell=True,
            cwd=WORKDIR,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"
    except (FileNotFoundError, OSError) as e:
        return f"Error: {e}"

    output = (bash_result.stdout + bash_result.stderr).strip()
    if len(output) > MAXCHARSIZE:
        output = output[:MAXCHARSIZE] + "...(more info be hidden)"

    return output if output else "(no output)"


def safe_path(p: str) -> Path:
    path = (WORKDIR / p).resolve()

    if not path.is_relative_to(WORKDIR):
        raise ValueError(f"Path escapes workspace: {p}")

    return path


def run_read(path: str, limit: int = None) -> str:
    try:
        text = safe_path(path).read_text()
        lines = text.splitlines()

        if limit and len(lines) > limit:
            lines = lines[:limit] + [f"...({len(lines) - limit} more lines be hidden)"]

        text = "\n".join(lines)
        if len(text) > MAXCHARSIZE:
            text = text[:MAXCHARSIZE] + "...(more info be hidden)"

        return text
    except Exception as e:
        return f"Error: {e}"


def run_write(path: str, content: str) -> str:
    try:
        file_path = safe_path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        file_path.write_text(content)

        return f"wrote {len(content)} bytes to {file_path}"
    except Exception as e:
        return f"Error: {e}"


def run_edit(path: str, old_text: str, new_text: str) -> str:
    try:
        file_path = safe_path(path)
        content = file_path.read_text()
        if old_text not in content:
            return f"Error: Text not found in {file_path}"

        file_path.write_text(content.replace(old_text, new_text, 1))

        return f"Edited {file_path}"
    except Exception as e:
        return f"Error: {e}"
