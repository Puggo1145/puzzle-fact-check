import unittest
from .tool import get_current_time
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent


class TestGetCurrentTimeTool(unittest.TestCase):
    def test_get_current_time_utc(self):
        """测试获取UTC时间"""
        result = get_current_time("UTC")
        print(f"UTC时间: {result}")
        self.assertIn("UTC", result)
    
    def test_get_current_time_shanghai(self):
        """测试获取上海时间"""
        result = get_current_time("Asia/Shanghai")
        print(f"上海时间: {result}")
        self.assertIn("CST", result)
    
    def test_invalid_timezone(self):
        """测试无效时区"""
        result = get_current_time("Invalid/Timezone")
        self.assertIn("错误", result)


def test_llm_tool_invocation():
    """测试通过LLM调用工具"""
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.0,
    )
    
    graph = create_react_agent(llm, tools=[get_current_time])

    message = {
        "messages": [
            (
                "system",
                """
你是一个有用的AI助手。当用户询问当前时间或日期时，请使用get_current_time工具获取准确信息。
                """,
            ),
            ("user", "现在是几点钟？请告诉我北京时间和纽约时间。"),
        ]
    }
    for s in graph.stream(message, stream_mode="values"):
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()


if __name__ == "__main__":
    # unittest.main()
    test_llm_tool_invocation() 