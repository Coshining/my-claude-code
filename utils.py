from tools import TOOL_HANDLERS

from constants import DENY_LIST, PERMISSION_RULES


def extract_text(history) -> str:
    if not isinstance(history, list):
        return ""

    texts = []
    for block in history[-1]["content"]:
        if getattr(block, "type", None) == "text":
            texts.append(block.text)

    return "\n".join(texts).strip()


def excute_tool_calls(response_context) -> list[dict]:
    results = []
    for block in response_context:
        if block.type != "tool_use":
            continue
        if not check_permission(block):
            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": "Permission denied.",
                }
            )
            continue

        tool_name = block.name
        handler = TOOL_HANDLERS.get(tool_name)
        output = handler(**block.input) if handler else f"Unknown tool: {tool_name}"
        print(f"> {tool_name}")
        if len(output) > 200:
            output = output[:200] + "...(more info be hidden)"
        print(output)

        results.append(
            {
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": output,
            }
        )

    return results


def check_deny_list(command: str) -> str | None:
    for pattern in DENY_LIST:
        if pattern in command:
            return f"Blocked: '{pattern}' is on the deny list"
    return None


def check_rules(tool_name: str, args: dict) -> str | None:
    for rule in PERMISSION_RULES:
        if tool_name in rule["tools"] and rule["check"](args):
            return rule["message"]
    return None


def ask_user(tool_name: str, args: dict, reason: str) -> str:
    print(f"\n⚠  {reason}")
    print(f"   Tool: {tool_name}({args})")
    choice = input("   Allow? [y/N] ").strip().lower()
    return "allow" if choice in ("y", "yes") else "deny"


def check_permission(block) -> bool:
    # 第一道闸门，拒绝高危命令
    if block.name == "bash":
        reason = check_deny_list(block.input.get("command", ""))
        print(f"\n⛔ {reason}")
        return False

    # 第二三闸门，需要询问用户确定的指令
    reason = check_rules(block.name, block.input)
    if reason:
        decision = ask_user(block.name, block.input, reason)
        if decision == "deny":
            return False
    return True
