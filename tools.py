import subprocess
import os


def run_bash(command: str) -> str:
    dangerous_cmd = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
    if any(d in command for d in dangerous_cmd):
        return "Error: Dangerous command blocked"

    try:
        bash_result = subprocess.run(
            command,
            shell=True,
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"
    except (FileNotFoundError, OSError) as e:
        return f"Error: {e}"

    output = (bash_result.stdout + bash_result.stderr).strip()
    return output[:50000] if output else "(no output)"
