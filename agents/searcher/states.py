from typing import List, Annotated, Sequence
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage, ToolMessage, AIMessage
from langgraph.graph.message import add_messages


class Status(BaseModel):
    evaluation: str = Field(description="对已执行操作是否满足预期结果的评估")
    memory: str = Field(description="对已执行操作的总结")
    next_step: str = Field(description="基于已有信息规划的下一步目标")
    action: AIMessage | str = Field(
        description="调用工具或回答",
        json_schema_extra={
            "options": [
                "如果你希望调用工具，请在此处输出工具调用信息",
                "如果你认为现有信息已经满足预期目标，请在此处输出：'answer'",
            ]
        },
    )


class SearchAgentState(BaseModel):
    content: str = Field(description="从新闻中提取的事实陈述")
    purpose: str = Field(description="你的检索目标")
    expected_result: List[str] = Field(
        description="期望找到的信息来源类型，如官方网站、新闻报道、学术论文等"
    )
    statuses: Annotated[Sequence[BaseMessage[Status]], add_messages] = Field(
        description="所有已执行的操作"
    )
    latest_tool_messages: List[ToolMessage]
