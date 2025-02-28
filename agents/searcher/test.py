from .graph import search_agent
from utils.llm_callbacks import AgentStateCallback

agent_callback = AgentStateCallback(verbose=True)

def test_search_agent():
    example_input = {
        "news_metadata": {
            "news_type": "体育新闻",
            "who": ["挪威选手 Kristian Blummenfelt", "其他铁人三项选手"],
            "what": [
                "东京奥运会男子铁人三项比赛结束",
                "金牌得主和其他选手跪地呕吐",
                "中文网络流传关于赛场水中大肠杆菌超标和粪水游泳的说法",
            ],
            "when": ["2021 年 7 月 26 日"],
            "where": ["东京奥运会赛场"],
            "why": [],
            "how": [],
        },
        "content": "网络流传'赛场水中大肠杆菌严重超标'的说法",
        "purpose": "获取东京湾水质检测原始数据",
        "expected_results": ["东京都环境局监测报告", "世界卫生组织检测记录"],
        "statuses": [],
        "latest_tool_messages": [],
        "total_tokens": 0,
        "max_tokens": 24000,  # 设置最大token数量
        "supporting_evidence": []  # 初始化证据列表
    }

    result = search_agent.invoke(
        example_input, 
        config={"callbacks": [agent_callback]}
    )
    
    # 打印最终结果
    if "result" in result:
        final_result = result["result"]
        print("\n===== 最终核查结果 =====")
        print(f"总结: {final_result['summary']}")
        print(f"结论: {final_result['conclusion']}")
        print(f"信息来源: {final_result['sources']}")
        print(f"置信度: {final_result['confidence']}")
        print(f"总token消耗: {result.get('total_tokens', 'N/A')}")
        
        # 打印收集到的证据
        if "supporting_evidence" in result and result["supporting_evidence"]:
            print(f"\n===== 收集到的重要证据 ({len(result['supporting_evidence'])}条) =====")
            for i, evidence in enumerate(result["supporting_evidence"]):
                print(f"\n证据 {i+1}:")
                print(f"内容: {evidence.content}")
                print(f"来源: {evidence.source}")
                print(f"相关性: {evidence.relevance}")


if __name__ == "__main__":
    test_search_agent()
