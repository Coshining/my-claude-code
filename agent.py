from constants import CLIENT, SYSTEM, MODEL, TOOLS
from utils import excute_tool_calls

from dataclasses import dataclass


@dataclass
class LoopState:
    messages: list  # 历史对话信息
    turn_count: int = 1  # 循环的轮次
    transition_reason: str | None = None  # 继续的原因

def run_one_turn(state: LoopState) -> bool:
    reponse = CLIENT.messages.create(
        model=MODEL,
        system=SYSTEM,
        messages=state.messages,
        tools=TOOLS,
        max_tokens=8000,
    )
    state.messages.append({"role": "assistant", "content": reponse.content})

    if reponse.stop_reason != "tool_use":
        state.transition_reason = None # 不再工具调用，那就没有继续的理由了
        return False

    results = excute_tool_calls(reponse.content)
    if not results:
        state.transition_reason = None # 工具调用无结果，说明里面并未调用工具，那也没有继续的理由了
        return False
    
    state.messages.append({"role": "user", "content": results})
    state.turn_count += 1
    state.transition_reason = "tool_result" # 继续的原因是本轮是工具调用，需要检查结果
    
    return True


def agent_loop(messages: list) -> bool:
    state = LoopState(messages=messages)
    while run_one_turn(state):
        pass
