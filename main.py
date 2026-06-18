from agent import agent_loop
from utils import extract_text


def setup(query: str):
    history = []
    while True:
        if query.strip().lower() in ("q", "exit", ""):
            break

        history.append({"role": "user", "content": query})
        agent_loop(history)

        final_text = extract_text(history)
        if final_text:
            print(f"最终结果：{final_text}")
        print()

        try:
            query = input("\033[36m用户提问： >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            break

def one_query_for_test(query: str) -> str:
    history = []
    history.append({"role": "user", "content": query})
    agent_loop(history)

    final_text = extract_text(history)
    return final_text if final_text else ""


if __name__ == "__main__":
    # setup(input("\033[36m用户提问： >> \033[0m"))
    setup("创建hello.py文件，文件里只有一个作用，打印出'hello world!'")
