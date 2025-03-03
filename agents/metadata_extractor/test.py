import json
from langchain_openai import ChatOpenAI
from .graph import MetadataExtractorAgent

def test_metadata_extractor():
    model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
    )
    
    example_initial_state = {
        "news_text": """
2021 年 7 月 26 日，男子铁人三项比赛结束后，
金牌得主挪威选手 Kristian Blummenfelt 和一些其他选手跪地
呕吐，铁人三项标准受到质疑
"""
    }
    
    metadata_extractor_agent = MetadataExtractorAgent(model)
    result = metadata_extractor_agent.invoke(example_initial_state)
    
    print(json.dumps(result, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    test_metadata_extractor()
