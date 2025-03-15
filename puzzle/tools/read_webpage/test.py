import unittest
import json
from tools import ReadWebpageTool, SearchBingTool, get_current_time
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langgraph.prebuilt import create_react_agent
from utils.timer import response_timer


class TestReadWebpageTool(unittest.TestCase):
    def setUp(self):
        self.tool = ReadWebpageTool()

    # @response_timer(description="测试基本网页读取功能")
    # def test_read_webpage(self):
    #     """测试基本网页读取功能"""
    #     result = self.tool.read_webpage(url="https://www.bbc.com/")
    #     # print(json.dumps(result, indent=4, ensure_ascii=False))
    #     # print("\n", result["content"])

    #     self.assertIsInstance(result, dict)
    #     self.assertIn("content", result)
    #     self.assertIn("title", result)
    #     self.assertIn("timing", result)
    #     print(f"Total time: {result['timing']['total']:.3f} seconds")

    @response_timer(description="测试读取JavaScript重度网页")
    def test_read_js_heavy_webpage(self):
        """测试读取JavaScript重度网页"""
        result = self.tool.read_webpage(
            url="https://www.nytimes.com/2025/02/26/us/politics/trump-ukraine-cabinet.html",
        )
        # print(json.dumps(result, indent=4, ensure_ascii=False))
        print("\n", result["content"])

        self.assertIsInstance(result, dict)


def test_llm_tool_invocation():
    """测试通过LLM调用工具"""
    tools = [
        SearchBingTool(), 
        ReadWebpageTool(save_results=True), 
        get_current_time
    ]

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
    )
    # llm = ChatDeepSeek(
    #     model="deepseek-chat",
    #     temperature=0.3,
    # )

    graph = create_react_agent(llm, tools=tools)

    message = {
        "messages": [
            (
                "system",
                """
你是一个精通多语言的网页浏览助手，你需要在互联网上检索用户需要的信息，并将结果总结给用户。
注意用户对检索时间的要求，例如“最近”、“最新”、“最近几天”、“最近一周”、“最近一个月”等，你可以通过 get_current_time 工具获取当前时间

在检索时：
- ！！！尽可能使用与目标消息最相关的语言进行检索
- 在使用搜索引擎时，你可以根据需求构造高级检索关键词以获得更准确的结果。
- ！！！尽可能寻找一手资料，例如官方报道，官方文档，当事人社交媒体账号等
- ！！！或寻找在某个领域最权威的资料，例如，MDN 文档、Science、Nature、Wikipedia 等
- ！！！不能仅依赖于转载内容和非权威内容，除非找不到更好的信源。

在回答时：
- ！！！请将你使用的信息的来源标注在相关回答的旁边。
- ！！！如果找不到信源支撑，请直接回答“没有找到相关信息”。不要自己生成或猜测。
你可能需要多次检索才能找到答案。
                """,
            ),
            ("user", "我想写一篇关于 LLM 在新闻事实核查中的应用的论文，请帮我找一些参考文献，并且阅读文献的摘要，确保这些文献的内容符合我的写作主题"),
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
