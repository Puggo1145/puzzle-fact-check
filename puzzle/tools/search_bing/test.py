import unittest
import json
from .tool import SearchBingTool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent


class TestSearchBingTool(unittest.TestCase):
    def setUp(self):
        self.tool = SearchBingTool()

    def test_search(self):
        """测试Bing搜索功能"""
        result = self.tool.search(query="铁人三项 报告", limit=5)
        self.assertIsInstance(result, list)
        print(json.dumps(result, indent=4, ensure_ascii=False))
        
        if result:  # 如果有结果
            self.assertIn("title", result[0])
            self.assertIn("url", result[0])
            self.assertIn("snippet", result[0])

    # def test_tool_invocation_search(self):
    #     """测试通过BaseTool接口调用搜索功能"""
    #     input_dict = {
    #         "query": "铁人三项 水质标准",
    #         "limit": 5,
    #         "ensearch": False,
    #     }
    #     result_json = self.tool.invoke(input_dict)
    #     result = json.loads(result_json)
    #     self.assertIsInstance(result, list)
    #     print(json.dumps(result, indent=4, ensure_ascii=False))

    # def test_tool_invocation_missing_params(self):
    #     """测试错误处理 - 缺少必要参数"""
    #     input_dict = {}
    #     with self.assertRaises(Exception):
    #         self.tool.invoke(input_dict)


def test_llm_tool_invocation():
    """测试通过LLM调用工具"""
    tool = SearchBingTool()

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.0,
    )
    
    graph = create_react_agent(llm, tools=[tool])

    message = {
        "messages": [
            (
                "system",
                """
你是一个精通使用搜索引擎进行信息检索的助手。用户会提出一个问题或检索目标，你需要使用 Bing 搜索引擎查找最相关的信息。
你需要根据问题构造相应的搜索关键字，你可以使用高级搜索词语来检索关键字。你可以不断调整搜索关键字，直到你认为结果能够满足用户需求。
请确保提供准确的信息，并引用信息来源。不要在没有引用的情况下自己生成回答。如果你认为没有找到相关信息，请回答“没有找到相关信息”。
                """,
            ),
            ("user", "BBC 最新报道"),
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