from .graph import MainAgent
from models import ChatQwen, ChatGemini
from langchain_openai import ChatOpenAI
from utils.llm_callbacks import ReasonerStreamingCallback


def test_plan_agent():
    example_initial_state = {
        "news_text": """
最近有网络流传说法称，2025 年初，美国共和党议员Riley Moore通过了一项新法案，将禁止中国公民以学生身份来美国。这项法案会导致每年大约30万中国学生将无法获得F、J、M类签证，从而无法到美国学习或参与学术交流。
"""
    }
    
    # model = ChatQwen(
    #     model="qwq-plus-latest",
    #     streaming=True,
    #     callbacks=[ReasonerStreamingCallback()]
    # )
    # model = ChatGemini(
    #     model="gemini-2.5-pro-exp-03-25",
    #     temperature=0,
    #     callbacks=[ReasonerStreamingCallback()]
    # )
    model = ChatOpenAI(
        model="chatgpt-4o-latest",
        temperature=0,
        streaming=True,
        callbacks=[ReasonerStreamingCallback()]
    )
    metadata_extract_model = ChatOpenAI(
        model="gpt-4o-mini", 
        temperature=0
    )
    # search_model = ChatQwen(
    #     model="qwq-plus-latest",
    #     streaming=True,
    #     callbacks=[ReasonerStreamingCallback()]
    # )
    # search_model = ChatGemini(
    #     model="gemini-2.5-pro-exp-03-25",
    #     temperature=0,
    #     callbacks=[ReasonerStreamingCallback()]
    # )
    search_model = ChatOpenAI(
        model="chatgpt-4o-latest",
        temperature=0,
        streaming=True,
        callbacks=[ReasonerStreamingCallback()]
    )

    main_agent = MainAgent(
        model=model,
        metadata_extract_model=metadata_extract_model,
        search_model=search_model,
        max_search_tokens=10000,
        selected_tools=[]
    )

    thread_config = {"thread_id": "test_id"}
    main_agent.graph.invoke(
        example_initial_state,
        {"configurable": thread_config},
    )


if __name__ == "__main__":
    test_plan_agent()
