from .graph import SearchAgentGraph
from .states import SearchAgentState
from agents.metadata_extractor.states import BasicMetadata
from models import ChatQwen
from utils.llm_callbacks import ReasonerStreamingCallback


def test_search_agent():
    example_input = SearchAgentState(
        check_point_id="1",
        retrieval_step_id="1",
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
        purpose="获取铁人三项赛出的相关水质事实核查报告",
        expected_source="事实核查组织对相关新闻的核查报告",
    )

    model = ChatQwen(
        model="qwq-plus-0305",
        streaming=True,
        callbacks=[ReasonerStreamingCallback()]
    )
    
    SearchAgentGraph(
        model=model,
        max_search_tokens=5000,
    ).graph.invoke(example_input)

if __name__ == "__main__":
    test_search_agent()
