import unittest
import json
from tools import SearchGoogleTool, get_current_time
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent


class TestSearchGoogleTool(unittest.TestCase):
    def setUp(self):
        self.tool = SearchGoogleTool()

    def test_search(self):
        """测试基本Google搜索功能"""
        result = self.tool.search(query="agent site:openai.com", limit=10)
        print(json.dumps(result, indent=4, ensure_ascii=False))
        self.assertIsInstance(result, list)

        if result:  # 如果有结果
            self.assertIn("title", result[0])
            self.assertIn("url", result[0])
            self.assertIn("description", result[0])

    def test_search_with_region(self):
        """测试带地区参数的搜索"""
        result = self.tool.search(query="local news", limit=5, region="uk", lang="en")
        print(json.dumps(result, indent=4, ensure_ascii=False))
        self.assertIsInstance(result, list)


def test_llm_tool_invocation():
    """测试通过LLM调用工具"""
    tools = [
        get_current_time, 
        SearchGoogleTool()
    ]

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.0,
    )

    graph = create_react_agent(llm, tools=tools)

    message = {
        "messages": [
            (
                "system",
                """
你是一个精通使用搜索引擎进行信息检索的助手。用户会提出一个问题或检索目标，你需要使用 Google 搜索引擎查找最相关的信息。
注意用户提问的时间，如果提问与时间有关，你需要先确定当前时间，然后根据当前时间
你需要根据问题构造相应的搜索关键字，你可以使用高级搜索词语来检索关键字。你可以不断调整搜索关键字，直到你认为结果能够满足用户需求。
请确保提供准确的信息，并引用信息来源。不要在没有引用的情况下自己生成回答。如果你认为没有找到相关信息，请回答"没有找到相关信息"。
                """,
            ),
            ("user", "OpenAI 的最近动向是什么？"),
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
