import tools


def extract_text(context) -> str:
    if not isinstance(context, list):
        return ""

    texts = []
    for block in context:
        text = getattr(block, "text", None)
        if text:
            texts.append(text)

    return "\n".join(texts).strip()


def excute_tool_calls(response_context) -> list[dict]:
    results = []
    for block in response_context:
        if block.type != "tool_use":
            continue

        tool_name = block.name
        command = block.input["command"]
        print(f"\033[33m$ {tool_name}工具调用：{command}\033[0m")

        output = tools.run_bash(command)
        print(f"{tool_name}工具调用结果：{output[:200]}")

        results.append(
            {
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": output,
            }
        )

    return results
