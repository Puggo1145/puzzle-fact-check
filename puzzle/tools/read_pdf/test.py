import unittest
import json
from .tool import ReadPDFTool


class TestReadPDFTool(unittest.TestCase):
    def setUp(self):
        self.tool = ReadPDFTool()
        
    def test_read_pdf_basic(self):
        """测试从真实URL读取PDF文件的基本功能"""
        # ArXiv论文PDF - Claude 3.5 Sonnet技术报告
        url = "https://arxiv.org/pdf/2502.12561"
        
        # 测试读取PDF前2页
        result = self.tool._run(url=url, start_page=1, end_page=2)
        result_dict = json.loads(result)
        print(result_dict)
        
        # 验证结果
        self.assertIn("total_pages", result_dict)
        self.assertIn("content", result_dict)
        self.assertEqual(result_dict["read_pages"]["start"], 1)
        self.assertEqual(result_dict["read_pages"]["end"], 2)
        self.assertEqual(len(result_dict["content"]), 2)
        # 确认内容非空
        self.assertTrue(len(result_dict["content"][0]["text"]) > 100)
        
    def test_invalid_pdf_url(self):
        """测试处理非PDF URL的情况"""
        # 使用HTML页面而非PDF
        url = "https://arxiv.org/abs/2402.17764"
        
        # 测试非PDF URL
        result = self.tool._run(url=url)
        result_dict = json.loads(result)
        
        # 验证错误信息
        self.assertIn("error", result_dict)
        self.assertIn("不是PDF文件", result_dict["error"])
        
    def test_page_limit(self):
        """测试页数限制功能"""
        url = "https://arxiv.org/pdf/2502.12561"
        
        # 尝试读取超过限制的页数
        result = self.tool._run(url=url, start_page=1, end_page=10)
        result_dict = json.loads(result)
        
        # 检查是否收到错误提示
        if "error" in result_dict:
            # 如果返回错误消息
            self.assertIn("最多允许读取5页", result_dict["error"])
        else:
            # 如果自动调整页数
            self.assertLessEqual(
                result_dict["read_pages"]["end"] - result_dict["read_pages"]["start"] + 1, 
                5
            )
            self.assertEqual(len(result_dict["content"]), 5)


if __name__ == "__main__":
    unittest.main()
