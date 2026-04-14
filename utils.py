from tools import TOOL_HANDLERS


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
