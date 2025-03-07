from dotenv import load_dotenv

load_dotenv()

from db.schema import (
    NewsText, 
    BasicMetadata,
    Knowledge,
    CheckPoint,
    RetrievalStep,
    SearchResult,
    Evidence
)

# 创建一个 NewsText Node
news_text_node = NewsText(
    content="""
2021 年 7 月 26 日，东京奥运会男子铁人三项比赛结束后，
金牌得主挪威选手 Kristian Blummenfelt 和一些其他选手跪地
呕吐，中文网络流传说法称："铁人三项选手集体呕吐"因
为"赛场水中大肠杆菌严重超标"、"铁人三项选手在粪水
中游泳"等
"""
).save()

# 创建一个 BasicMetadata Node
basic_metadata_node = BasicMetadata(
    news_type="体育新闻",
    who=["挪威选手 Kristian Blummenfelt", "一些其他选手"],
    when=["2021 年 7 月 26 日"],
    where=["东京奥运会"],
    what=["男子铁人三项比赛结束后，部分选手跪地呕吐"],
    why=["赛场水中大肠杆菌严重超标"],
    how=["铁人三项选手在粪水中游泳"],
).save()
# NewsText <-[:HAS_BASIC_METADATA]- BasicMetadata
news_text_node.has_basic_metadata.connect(basic_metadata_node)

knowledge_node_1 = Knowledge(
    term="大肠杆菌",
    category="科学概念",
    description="大肠杆菌（学名：Escherichia coli，通常简写：E. coli）是肠杆菌科埃希氏菌属的一个物种，为人体和动物肠道中的一种细菌，主要寄生于大肠内而得名，约占肠道菌中的0.1%。大肠杆菌是一种两端钝圆、能运动、无芽孢的革兰氏阴性、兼性厌氧、杆状细菌。",
    source="https://zh.wikipedia.org/wiki/%E5%A4%A7%E8%8A%B1%E6%9F%AF%E8%8A%B1%E8%99%AB"
).save()
news_text_node.has_knowledge.connect(knowledge_node_1)

knowledge_node_2 = Knowledge(
    term="铁人三项",
    category="体育项目",
    description="铁人三项是一项包含游泳、自行车和跑步三个连续项目的体育运动。运动员需要依次完成这些项目，且更换装备的时间也被计入总时间。",
    source="https://zh.wikipedia.org/wiki/%E5%A4%A7%E8%8A%B1%E6%9F%AF%E8%8A%B1%E8%99%AB"
).save()
news_text_node.has_knowledge.connect(knowledge_node_2)

check_point_1 = CheckPoint(
    content="金牌得主挪威选手Kristian Blummenfelt和其他选手在赛后跪地呕吐。",
    is_verification_point=True,
    importance="确认选手呕吐是否真实发生是验证后续说法的基础。",
).save()
news_text_node.has_check_point.connect(check_point_1)

check_point_1_retrieval_step_1 = RetrievalStep(
    purpose="通过新闻报道或赛事直播片段确认选手呕吐行为的真实性。",
    expected_sources=[
        "新闻媒体",
        "赛事官网",
        "视频平台"
    ]
).save()
check_point_1.verified_by.connect(check_point_1_retrieval_step_1)

check_point_1_retrieval_step_1_search_result = SearchResult(
    summary="xxxx",
    conclusion="xxxx",
    confidence="xxxx",
    sources="xxxx"
).save()
check_point_1_retrieval_step_1.has_result.connect(check_point_1_retrieval_step_1_search_result)

check_point_1_retrieval_step_1_evidence_1 = Evidence(
    content="xxxx",
    source={"xxx": "xxxx"},
    relationship="SUPPORT",
    reasoning="xxxxxxx"
).save()
check_point_1_retrieval_step_1.supports_by.connect(check_point_1_retrieval_step_1_evidence_1)

check_point_1_retrieval_step_1_evidence_2 = Evidence(
    content="xxxx",
    source={"xxx": "xxxx"},
    relationship="CONTRADICTS_WITH",
    reasoning="xxxxxxx"
).save()
check_point_1_retrieval_step_1.contradicts_with.connect(check_point_1_retrieval_step_1_evidence_2)
