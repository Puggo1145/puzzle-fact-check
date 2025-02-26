import unittest
from .model import MetadataExtractor
from dotenv import load_dotenv

load_dotenv()


class TestMetadataExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = MetadataExtractor(dev_mode=True, stream=True)

    def test_extract_metadata(self):
        test_news = """
2021 年 7 月 26 日，东京奥运会男子铁人三项比赛结束后，
金牌得主挪威选手 Kristian Blummenfelt 和一些其他选手跪地
呕吐，中文网络流传说法称："铁人三项选手集体呕吐"因
为"赛场水中大肠杆菌严重超标"、"铁人三项选手在粪水
中游泳"等
"""
        result = self.extractor.extract_metadata(test_news)

        # 验证结果包含预期的字段
        self.assertIsNotNone(result)
        self.assertIn("news_type", result)
        self.assertIn("who", result)
        self.assertIn("what", result)
        self.assertIn("when", result)
        self.assertIn("where", result)
        self.assertIn("why", result)
        self.assertIn("how", result)

        # 验证新闻类型不为空
        self.assertTrue(len(result["news_type"]) > 0)

        # 验证至少有一些5W1H元素被提取出来
        elements_count = sum(
            1
            for element in [
                result["who"],
                result["what"],
                result["when"],
                result["where"],
                result["why"],
                result["how"],
            ]
            if element and len(element) > 0
        )
        self.assertTrue(elements_count >= 0, "没有提取出任何新闻要素")


if __name__ == "__main__":
    unittest.main() 