import unittest
from .model import KnowledgeExtractor
from dotenv import load_dotenv

load_dotenv()

class TestKnowledgeExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = KnowledgeExtractor(dev_mode=True, stream=True)

    def test_extract_knowledge_elements(self):
        # 准备测试数据
        test_news = """
2021 年 7 月 26 日，东京奥运会男子铁人三项比赛结束后，
金牌得主挪威选手 Kristian Blummenfelt 和一些其他选手跪地
呕吐，中文网络流传说法称："铁人三项选手集体呕吐"因
为"赛场水中大肠杆菌严重超标"、"铁人三项选手在粪水
中游泳"等
"""
        # 调用被测试的方法
        result = self.extractor.extract_knowledge_elements(test_news)

        # 简单验证结果不为空
        self.assertIsNotNone(result)
        self.assertIn('elements', result)
        self.assertTrue(len(result['elements']) > 0)


if __name__ == "__main__":
    unittest.main() 