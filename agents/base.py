from typing import Dict, Any
from langgraph.graph.state import CompiledStateGraph

class BaseAgent:
    def _build_graph(self) -> CompiledStateGraph | Any:
        """ 在该方法内构建 agent graph """
        
    def invoke(
        self, 
        initial_state: Any,
    ) -> Dict[str, Any] | Any:
        """agent 调用方法"""