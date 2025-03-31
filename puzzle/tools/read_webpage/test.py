import unittest
import json
from .tool import ReadWebpageTool
from dotenv import load_dotenv

load_dotenv()

class TestReadWebpageTool(unittest.TestCase):
    def setUp(self):
        self.tool = ReadWebpageTool()

    def test_read_webpage(self):
        """测试基本网页读取功能"""
        result = self.tool.read_webpage(url="https://www.bbc.com/")
        # print(json.dumps(result, indent=4, ensure_ascii=False))
        # print("\n", result["content"])

        self.assertIsInstance(result, dict)
        self.assertIn("content", result)
        self.assertIn("title", result)

    def test_read_js_heavy_webpage(self):
        """测试读取JavaScript重度网页"""
        result = self.tool.read_webpage(
            url="https://www.nytimes.com/2025/02/26/us/politics/trump-ukraine-cabinet.html",
        )
        print(json.dumps(result, indent=4, ensure_ascii=False))
        print("\n", result["content"])

        self.assertIsInstance(result, dict)
        
    def test_read_pdf_url(self):
        """测试读取PDF文件URL"""
        # 测试明确的PDF URL
        pdf_url = "https://arxiv.org/pdf/2503.22481"
        result = self.tool.read_webpage(url=pdf_url)
        
        print("\nPDF URL测试结果:", json.dumps(result, indent=4, ensure_ascii=False))
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["title"], "PDF Document")
        self.assertIn("PDF", result["content"])
        self.assertIn("PDF files cannot be processed", result["error"])
        
        # 测试嵌入PDF查看器的HTML页面
        html_wrapped_pdf = "https://arxiv.org/abs/2503.22481"  # arXiv的HTML包装页面
        result2 = self.tool.read_webpage(url=html_wrapped_pdf)
        
        print("\nHTML包装PDF测试结果:", json.dumps(result2, indent=4, ensure_ascii=False))
        
        self.assertIsInstance(result2, dict)
        # 验证是否被正确识别为PDF相关内容
        # 如果检测为PDF查看器页面，则会有PDF相关消息
        self.assertEqual(result2["title"], "PDF Document")
        self.assertIn("PDF", result2["content"])
        
if __name__ == "__main__":
    unittest.main()
