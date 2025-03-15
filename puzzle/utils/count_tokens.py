import json
from typing import List
import tiktoken
from langchain_core.messages import BaseMessage

# 初始化tokenizer
tokenizer = tiktoken.get_encoding("cl100k_base")

def count_tokens(messages: List[BaseMessage]) -> int:
    """计算消息列表的token数量"""
    # 将消息转换为字符串
    message_texts = []
    for message in messages:
        if hasattr(message, "content") and isinstance(message.content, str):
            message_texts.append(message.content)
        else:
            # 如果消息内容不是字符串，尝试转换为JSON字符串
            try:
                message_texts.append(json.dumps(message.content))
            except:
                message_texts.append(str(message.content))
    
    # 合并所有文本
    combined_text = " ".join(message_texts)
    
    # 计算token数量
    tokens = tokenizer.encode(combined_text)
    return len(tokens)