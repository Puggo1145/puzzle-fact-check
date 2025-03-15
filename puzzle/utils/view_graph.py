import sys
from langgraph.graph.state import CompiledGraph

def view_graph(
    agent_graph: CompiledGraph,
    output_path: str = "graph.png"
):
    # 添加命令行查看图的选项
    if "--view-graph" in sys.argv:
        import os

        agent_graph.get_graph().draw_mermaid_png(output_file_path=output_path)
        print(f"Graph saved to {os.path.abspath(output_path)}")
        
        sys.exit()