from .graph import PlanAgentGraph
from langchain_deepseek import ChatDeepSeek
from langchain_openai import ChatOpenAI
from langgraph.types import Command
from langgraph.graph.state import START
from utils.llm_callbacks import ReasonerStreamingCallback
import readchar
import sys
import os


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
    
    # 首先打印提示信息，只打印一次
    print(prompt)
    
    def print_options():
        # 清除当前行
        sys.stdout.write('\r' + ' ' * 100 + '\r')
        
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
            sys.stdout.write('\n')
            return options[selected]


def get_user_feedback(question):
    """处理用户交互，返回用户反馈"""
    print(question)
    
    choice = cli_select_option(["continue", "revise"], "请选择操作：")
    
    if choice == "continue":
        return {
            "action": "continue"
        }
    else:
        print("\n请输入您的修改建议：")
        feedback = input("> ")
        return {
            "action": "revise",
            "feedback": feedback
        }


def test_plan_agent():
    model = ChatDeepSeek(
        model="deepseek-reasoner",
        temperature=0.6,
        streaming=True,
        callbacks=[ReasonerStreamingCallback()],
    )

    example_initial_state = {
        "news_text": """
2021 年 7 月 26 日，东京奥运会男子铁人三项比赛结束后，
金牌得主挪威选手 Kristian Blummenfelt 和一些其他选手跪地
呕吐，中文网络流传说法称："铁人三项选手集体呕吐"因
为"赛场水中大肠杆菌严重超标"、"铁人三项选手在粪水
中游泳"等
"""
    }

    plan_agent = PlanAgentGraph(model=model)
    thread_config = {"thread_id": "some_id"}
    
    plan_agent.graph.invoke(
        example_initial_state, 
        {"configurable": thread_config},
        stream_mode="updates"
    )
    
    # 需要反复捕获 interrups 才能不断进行 agent-human loop ！！！
    while True:
        states = plan_agent.graph.get_state({"configurable": thread_config})
        interrupts = states.tasks[0].interrupts if len(states.tasks) > 0 else False
        if interrupts:
            question = interrupts[0].value.get('question', '')

            result = get_user_feedback(question)
            
            plan_agent.graph.invoke(
                Command(resume=result),
                config={"configurable": thread_config},
            )
        else:
            break
        
    

if __name__ == "__main__":
    test_plan_agent()
