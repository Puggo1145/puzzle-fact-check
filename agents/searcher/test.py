from .graph import SearchAgentGraph
from .states import SearchAgentState
from agents.metadata_extractor.states import BasicMetadata
from langchain_openai import ChatOpenAI
from utils import check_env


def test_search_agent():
    example_input = SearchAgentState(
        basic_metadata=BasicMetadata(
            news_type="体育新闻",
            who=["挪威选手 Kristian Blummenfelt", "其他铁人三项选手"],
            what=[
                "东京奥运会男子铁人三项比赛结束",
                "金牌得主和其他选手跪地呕吐",
                "中文网络流传关于赛场水中大肠杆菌超标和粪水游泳的说法",
            ],
            when=["2021 年 7 月 26 日"],
            where=["东京奥运会赛场"],
            why=[],
            how=[],
        ),
        content="网络流传'赛场水中大肠杆菌严重超标'的说法",
        purpose="获取铁人三项赛出的水质检测原始数据",
        expected_sources=[
            "东京都环境局监测报告",
            "世界卫生组织检测记录",
            "事实核查组织对相关新闻的核查报告",
        ],
    )

    model = ChatOpenAI(
        model="qwen-plus-latest",
        temperature=0.4,
        api_key=check_env("ALI_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    search_agent = SearchAgentGraph(model=model, max_tokens=16000)
    search_agent.invoke(example_input)


if __name__ == "__main__":
    test_search_agent()
