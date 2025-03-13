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
        config={
            "cli_mode": True,
            "max_search_tokens": 5000,
        },
    )
    
    example_input = {
        "news_text": """
2025 年 1 月 31 日，美国第七巡回法庭的约瑟夫·巴伦法官判决拜登赦免那些没有被起诉的人违宪，
宪法中并没有适用于可以预早赦免未被起诉的人的条款。拜登先发布制人的赦免令很可能无效。
"""
    }

    thread_config = {"thread_id": "some_id"}
    agent.invoke(
        initial_state=example_input,
        config={"configurable": thread_config}
    )
    
if __name__ == "__main__":
    main()
