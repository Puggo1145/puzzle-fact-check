import unittest
import json
from .tool import SearchWikipediaTool
from langchain_openai import ChatOpenAI


class TestSearchWikipediaTool(unittest.TestCase):
    def setUp(self):
        self.tool = SearchWikipediaTool()

    def test_search_content(self):
        """测试内容搜索功能"""
        result = self.tool.search_content(query="人工智能", limit=2, language="zh")
        self.assertIsInstance(result, list)
        # print(json.dumps(result, indent=4, ensure_ascii=False))

        if result:  # 如果有结果
            self.assertIn("title", result[0])
            self.assertIn("snippet", result[0])

    def test_search_title(self):
        """测试标题搜索功能"""
        result = self.tool.search_title(query="人工智能", limit=2, language="zh")
        self.assertIsInstance(result, list)
        # print(json.dumps(result, indent=4, ensure_ascii=False))
        if result:  # 如果有结果
            self.assertIn("title", result[0])
            self.assertIn("description", result[0])

    def test_get_page(self):
        """测试获取页面内容功能"""
        result = self.tool.get_page(title="人工智能", language="zh")
        self.assertIsInstance(result, dict)
        print(json.dumps(result, indent=4, ensure_ascii=False))

        if "error" not in result:
            self.assertIn("title", result)
            self.assertIn("html", result)

    def test_get_page_source(self):
        """测试获取页面参考资料"""
        result = self.tool.get_page_source(
            title="Artificial_intelligence", language="en"
        )
        self.assertIsInstance(result, dict)
        # print(json.dumps(result, indent=4, ensure_ascii=False))

        if "error" not in result:
            self.assertIn("title", result)
            self.assertIn("source", result)

    def test_tool_invocation_search_content(self):
        """测试通过BaseTool接口调用搜索内容功能"""
        input_dict = {
            "action": "search_content",
            "query": "人工智能",
            "limit": 2,
            "language": "zh",
        }
        result_json = self.tool.invoke(input_dict)

        result = json.loads(result_json)
        self.assertIsInstance(result, list)

    def test_tool_invocation_search_titles(self):
        """测试通过BaseTool接口调用搜索标题功能"""
        input_dict = {
            "action": "search_titles",
            "query": "人工智能",
            "limit": 2,
            "language": "zh",
        }
        result_json = self.tool.invoke(input_dict)
        result = json.loads(result_json)
        self.assertIsInstance(result, list)

    def test_tool_invocation_missing_params(self):
        """测试错误处理 - 缺少必要参数"""
        input_dict = {"action": "search_content"}
        with self.assertRaises(Exception):
            self.tool.invoke(input_dict)

    def test_tool_invocation_invalid_json(self):
        """测试错误处理 - 无效的JSON"""
        with self.assertRaises(Exception):
            self.tool.invoke("{invalid json")


from langgraph.prebuilt import create_react_agent
from utils.get_env import get_env


# 经过初步测试，gpt-4o-mini 在这个任务中的表现最佳，又快又准
def test_llm_tool_invocation():
    """测试通过LLM调用工具"""
    tool = SearchWikipediaTool()

    # llm = ChatDeepSeek(
    #     model="deepseek-chat",
    #     temperature=0.0,
    # )
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.0,
    )
    # llm = ChatOpenAI(
    #     model="qwen-turbo",
    #     temperature=0.0,
    #     api_key=check_env("ALI_API_KEY"),
    #     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    # )
    graph = create_react_agent(llm, tools=[tool])

    message = {
        "messages": [
            (
                "system",
                """
你是一个精通多语言的知识检索专家，用户会提供一个知识元，你需要检索维基百科找到该知识元的定义。
注意，检索到的词条名称可能是知识元的同义词。
如果无法精确匹配到该知识元，请尝试更换检索语言和知识元的语言，或更换检索方式等尝试检索。
如果多次检索后仍然无法找到精确的定义，请直接回答 “无法找到知识元的精确定义”，请不要主动生成定义。
确定知识元的定义后，请按用户提问的语言返回定义。
                """,
            ),
            ("user", "铁人三项"),
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
