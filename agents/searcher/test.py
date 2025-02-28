from graph import search_agent
from utils import print_streaming_message

def test_search_agent():
    example_input = {
        "content": "",
        "purpose": "",
        "expected_result": "",
        "statuses": [],
        "latest_tool_messages": []
    }
    
    for s in search_agent.stream(example_input, stream_mode="values"):
        print_streaming_message(s)
    

if __name__ == "__main__":
    test_search_agent()
