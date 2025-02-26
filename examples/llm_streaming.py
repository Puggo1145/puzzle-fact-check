from langchain_deepseek import ChatDeepSeek
from utils import ReasonerStreamingCallback
from dotenv import load_dotenv

load_dotenv()

messages = [
    ("human", "Hello deepseek."),
]



# To enable callbacks, set streaming=True
model = ChatDeepSeek(
    model="deepseek-reasoner",
    streaming=True,
    callbacks=[ReasonerStreamingCallback()],
)

model.invoke(messages)

# R1 Chunk Content:
# content='' 
# additional_kwargs={'reasoning_content': ' they'} 
# response_metadata={} 
