import unittest
import json
from .tool import SearchBingTool

class TestSearchBingTool(unittest.TestCase):
    def setUp(self):
        self.tool = SearchBingTool()

    def test_search(self):
        """测试Bing搜索功能"""
        result = self.tool.search(query="铁人三项 水质检测", limit=10)
        self.assertIsInstance(result, list)
        print(json.dumps(result, indent=4, ensure_ascii=False))
        
        if result:  # 如果有结果
            self.assertIn("title", result[0])
            self.assertIn("url", result[0])
            self.assertIn("snippet", result[0])

    def test_tool_invocation_search(self):
        """测试通过BaseTool接口调用搜索功能"""
        input_dict = {
            "query": "铁人三项",
            "limit": 10,
            "ensearch": False,
        }
        result_json = self.tool.invoke(input_dict)
        result = json.loads(result_json)
        self.assertIsInstance(result, list)

    def test_tool_invocation_missing_params(self):
        """测试错误处理 - 缺少必要参数"""
        input_dict = {}
        with self.assertRaises(Exception):
            self.tool.invoke(input_dict)


if __name__ == "__main__":
    unittest.main()