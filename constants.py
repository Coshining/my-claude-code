import os, platform
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(override=True)  # 把.env里的配置放进了系统的环境变量里

# 如果实际上本机已经在系统变量里配了url就不需要.env里的token了
ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL")
if ANTHROPIC_BASE_URL:
    os.environ.pop("ANTHROPIC_AUTH_TOKEN", None)

CLIENT = Anthropic(base_url=ANTHROPIC_BASE_URL)  # 两种方式，要么url，要么key+token

MODEL = os.getenv("MODEL_ID")

# 系统角色prompt：你是指定路径，环境下的一个编码助手，使用命令行的形式解决问题。另外，不需要解释。
SYSTEM = (
    f"You are a coding agent at {os.getcwd()}, and the work environment is {platform.architecture()}."
    "Use bash to solve tasks, and use commands appropriate to the environment. Act, don't explain."
)

WORKDIR = Path.cwd()

# 工具
TOOLS = [
    {
        "name": "bash",
        "description": "Run a shell command.",
        "input_schema": {
            "type": "Object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"],
        },
    },
    {
        "name": "read_file",
        "description": "Read file content.",
        "input_schema": {
            "type": "Object",
            "properties": {
                "path": {"type": "string"},
                "limit": {"type": "integer"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write content to file.",
        "input_schema": {
            "type": "Object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "edit_file",
        "description": "Replace exact text in file.",
        "input_schema": {
            "type": "Object",
            "properties": {
                "path": {"type": "string"},
                "old_text": {"type": "string"},
                "new_text": {"type": "string"},
            },
            "required": ["path", "old_text", "new_text"],
        },
    },
]

MAXCHARSIZE = 50000

DENY_LIST = [
    "rm -rf /", "sudo", "shutdown", "reboot",
    "mkfs", "dd if=", "> /dev/sda",
]

PERMISSION_RULES = [
    {
        "tools": ["write_file", "edit_file"],
        "check": lambda args: not (WORKDIR / args.get("path", "")).resolve().is_relative_to(WORKDIR),
        "message": "Writing outside workspace",
    },
    {
        "tools": ["bash"],
        "check": lambda args: any(kw in args.get("command", "") for kw in ["rm ", "> /etc/", "chmod 777"]),
        "message": "Potentially destructive command",
    },
]
