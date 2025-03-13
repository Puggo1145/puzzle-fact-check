import uuid
from typing import Dict, Any, List, TypedDict
from langgraph.graph.state import StateGraph, CompiledStateGraph
from langgraph.types import Send

# 定义状态类型
class TaskState(TypedDict):
    task_id: str
    content: str
    result: str

class MainState(TypedDict):
    tasks: List[TaskState]
    merged_results: Dict[str, str]

def starter(state: MainState) -> MainState:
    """初始化状态"""
    return {
        "tasks": [],
        "merged_results": {}
    }

# 简单的处理函数
def create_tasks(state: MainState) -> List[Send]:
    """创建并行任务"""
    tasks: List[Send] = []
    for i in range(3):
        task_id = str(uuid.uuid4())
        tasks.append(Send(
            "process_task",
            {
                "task_id": task_id,
                "content": f"Task {i} content",
                "result": ""
            }
        ))
        
    return tasks

def process_task(state: TaskState):
    """处理单个任务"""
    # 模拟任务处理
    result = f"Processed: {state['content']}"
    return {"result": result}

def merge_results(states: List[TaskState]) -> Dict[str, Any]:
    """合并多个任务的结果"""
    print("\n--- Merge Function Received States ---")
    for state in states:
        print(f"Task ID: {state['task_id']}")
        print(f"Content: {state['content']}")
        print(f"Result: {state['result']}")
        print("---")
    
    # 将结果合并到一个字典中
    merged_results = {}
    for state in states:
        merged_results[state['task_id']] = state['result']
    
    return {"merged_results": merged_results}

def final_step(state: MainState) -> MainState:
    """最终处理步骤"""
    print("\n--- Final State ---")
    print(f"Merged Results: {state['merged_results']}")
    return state

# 构建图
def build_graph() -> CompiledStateGraph:
    # 创建主图
    graph = StateGraph(MainState)
    
    # 添加节点
    graph.add_node("starter", starter)
    graph.add_node("process_task", process_task)
    graph.add_node("final_step", final_step)
    graph.add_node("merge_results", merge_results)
    
    # 设置入口点
    graph.set_entry_point("starter")
    
    # 添加边
    graph.add_conditional_edges(
        "starter",
        create_tasks, # type: ignore
        ["process_task"],
    )
    
    # 从并行任务合并到最终步骤
    graph.add_edge(["process_task"], "merge_results")
    graph.add_edge("merge_results", "final_step")
    
    # 设置结束点
    graph.set_finish_point("final_step")
    
    return graph.compile()

# 运行图
def run_example():
    graph = build_graph()
    
    # 初始状态
    initial_state = {
        "tasks": [],
        "merged_results": {}
    }
    
    # 执行图
    result = graph.invoke(initial_state)
    
    print("\n--- Execution Complete ---")
    print(f"Final Result: {result}")

if __name__ == "__main__":
    run_example()
