import json
from langchain_core.tools import BaseTool
from tools import (
    SearchBingTool,
    SearchGoogleTool,
    SearchWikipediaTool,
    ReadWebpageTool,
    get_current_time,
)
from langchain_core.utils.function_calling import convert_to_openai_tool

tools: list[BaseTool] = [
    SearchBingTool(),
    SearchGoogleTool(),
    SearchWikipediaTool(),
    ReadWebpageTool(),
    get_current_time,
]

tool_calling_schema = [
    convert_to_openai_tool(tool)
    for tool in tools
]

print(json.dumps(tool_calling_schema, indent=4, ensure_ascii=False))
