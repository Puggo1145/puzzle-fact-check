from langgraph.graph.state import StateGraph
from pydantic import BaseModel
from agents.base import BaseAgentCallback

from typing import Any, Optional
from uuid import UUID


class TestCallback(BaseAgentCallback):
    async def on_chain_end(
        self,
        outputs: dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> None:
        print(f"当前节点：{self.current_node}")
        print(f"run_id：{run_id}")
        
        if self.current_node == "retrieve_knowledge":
            print(outputs)


class TestState(BaseModel):
    random: int

graph_builder = StateGraph(TestState)


def node_1(state: TestState):
    print("node 1")
    return state

    
def node_2(state: TestState):
    print("node 2")
    return state
    
    
graph_builder.add_node("node_1", node_1)
graph_builder.add_node("node_2", node_2)
graph_builder.set_entry_point("node_1")
graph_builder.add_edge("node_1", "node_2")

graph = graph_builder.compile()
graph.invoke(input={"random": 0}, config={"callbacks": [TestCallback()]})
