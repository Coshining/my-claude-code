from constants import CLIENT, SYSTEM, MODEL, TOOLS
from utils import excute_tool_calls

def agent_loop(messages: list):
    while True:
        reponse = CLIENT.messages.create(
            model=MODEL,
            system=SYSTEM,
            messages=messages,
            tools=TOOLS,
            max_tokens=8000,
        )
        messages.append({"role": "assistant", "content": reponse.content})

        if reponse.stop_reason != "tool_use":
            return
        
        results = excute_tool_calls(reponse.content)
        messages.append({"role": "user", "content": results})
    
