from agent import agent_loop
from utils import extract_text

if __name__ == "__main__":
    history = []
    while True:
        try:
            query = input("\033[36m用户提问： >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            break

        if query.strip().lower() in ("q", "exit", ""):
            break

        history.append({"role": "user", "content": query})
        agent_loop(history)

        final_text = extract_text(history)
        if final_text:
            print(f"最终结果：{final_text}")
        print()
