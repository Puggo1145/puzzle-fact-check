from dotenv import load_dotenv
from agents import MainAgent
from models import ChatQwen
from langchain_openai import ChatOpenAI

load_dotenv()

def main():
    model = ChatQwen(model="qwq-32b", streaming=True)
    search_model = ChatQwen(model="qwq-plus-latest", streaming=True)
    metadata_extract_model = ChatOpenAI(model="gpt-4o-mini")
    
    agent = MainAgent(
        model=model,
        search_model=search_model,
        metadata_extract_model=metadata_extract_model,
    )
    
    example_input = {
        "news_text": """
2021 年 7 月 26 日，东京奥运会男子铁人三项比赛结束后，
金牌得主挪威选手 Kristian Blummenfelt 和一些其他选手跪地
呕吐，中文网络流传说法称："铁人三项选手集体呕吐"因
为"赛场水中大肠杆菌严重超标"、"铁人三项选手在粪水
中游泳"等"""
    }
    thread_config = {"thread_id": "some_id"}
    
    agent.invoke(
        initial_state=example_input,
        config={"configurable": thread_config}
    )
    
if __name__ == "__main__":
    main()
