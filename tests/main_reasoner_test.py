import unittest
import json
from models.main_reasoner import MainReasoner, ModelConfig
from dotenv import load_dotenv
from utils.timer import response_timer

load_dotenv()

test_data = """
2021 年 7 月 26 日，东京奥运会男子铁人三项比赛结束后，
金牌得主挪威选手 Kristian Blummenfelt 和一些其他选手跪地
呕吐，中文网络流传说法称："铁人三项选手集体呕吐"因
为"赛场水中大肠杆菌严重超标"、"铁人三项选手在粪水
中游泳"等
"""

class TestMainReasoner(unittest.TestCase):
    def setUp(self):
        self.reasoner = MainReasoner(dev_mode=True)

    @response_timer("主模型 - 进行事实核查规划")
    def test_plan_fact_check(self):
        result = self.reasoner.plan_fact_check(test_data)

        # 格式化打印JSON，确保在终端中有正确的换行
        print(json.dumps(result, ensure_ascii=False, indent=2))

        # 验证结果不为空
        self.assertIsNotNone(result)
        self.assertIn("statements", result)


if __name__ == "__main__":
    unittest.main()
    
    # 测试流式输出（百炼平台不支持通过 langchain 封装输出流式数据）
    # stream_model_config = ModelConfig(
    #     model_name="gpt-4o-mini",
    #     temperature=0.0,
    #     api_key_name="OPENAI_API_KEY",
    # )
    # reasoner = MainReasoner(model_config=stream_model_config, dev_mode=True, stream=True)
    # reasoner.plan_fact_check(test_data)
