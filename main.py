import sys
import readchar
from dotenv import load_dotenv
from agents import MainAgent
from models import ChatQwen

load_dotenv()

def cli_select_option(options, prompt):
    """
    实现命令行选择功能，用户可以通过左右箭头键选择选项

    Args:
        options: 选项列表
        prompt: 提示信息

    Returns:
        选中的选项
    """
    selected = 0

    print(prompt)

    def print_options():
        # 清除当前行
        sys.stdout.write("\r" + " " * 100 + "\r")

        # 只打印选项，不打印提示
        for i, option in enumerate(options):
            if i == selected:
                sys.stdout.write(f"[•] {option}  ")
            else:
                sys.stdout.write(f"[ ] {option}  ")

        sys.stdout.flush()

    print_options()

    while True:
        key = readchar.readkey()

        if key == readchar.key.LEFT and selected > 0:
            selected -= 1
            print_options()
        elif key == readchar.key.RIGHT and selected < len(options) - 1:
            selected += 1
            print_options()
        elif key == readchar.key.ENTER:
            sys.stdout.write("\n")
            return options[selected]


def get_user_feedback():
    """处理用户交互，返回用户反馈"""
    choice = cli_select_option(["continue", "revise"], "请选择操作：")

    if choice == "continue":
        return {"action": "continue"}
    else:
        print("\n请输入您的修改建议：")
        feedback = input("> ")
        return {"action": "revise", "feedback": feedback}

def main():
    model = ChatQwen(model="qwq-32b")
    search_model = ChatQwen(model="qwq-32b")
    metadata_extract_model = ChatQwen(model="qwen-plus-latest")
    
    agent = MainAgent(
        model=model,
        search_model=search_model,
        metadata_extract_model=metadata_extract_model
    )
    
    example_input = {
        "news_text": """
        
        """
    }
    thread_config = {"thread_id": "some_id"}
    
    agent.invoke(
        initial_state=example_input,
        config={"configurable": thread_config}
    )
    
    while True:
        states = agent.graph.get_state({"configurable": thread_config})
        interrupts = states.tasks[0].interrupts if len(states.tasks) > 0 else False
        if interrupts:
            # question = interrupts[0].value.get('question', '')
            result = get_user_feedback()

            if result["action"] == "continue":
                agent.invoke(
                    Command(resume="continue"),
                    config={"configurable": thread_config},
                )
            else:
                agent.invoke(
                    Command(
                        resume="revise",
                        update={
                            "human_feedback": result["feedback"],
                        },
                    ),
                    config={"configurable": thread_config},
                )
        else:
            break


if __name__ == "__main__":
    main()
