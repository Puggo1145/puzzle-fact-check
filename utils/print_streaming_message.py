from typing import Any

def print_streaming_message(s: dict[str, Any] | Any):
    message = s["messages"][-1]
    if isinstance(message, tuple):
        print(message)
    else:
        message.pretty_print()