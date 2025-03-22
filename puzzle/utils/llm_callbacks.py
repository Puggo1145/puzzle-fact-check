from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import GenerationChunk, ChatGenerationChunk, LLMResult

from typing import Optional, Union, Any, Literal


class ReasonerStreamingCallback(BaseCallbackHandler):
    def __init__(self):
        self.current_output_type: Literal["thinking", "content"] = "content"
        # ANSI escape code for gray color
        self.gray_color = "\033[90m"
        self.reset_color = "\033[0m"

    def on_llm_new_token(
        self,
        token: str,
        *,
        chunk: Optional[Union[GenerationChunk, ChatGenerationChunk]] = None,
        **kwargs: Any,
    ):
        if "reasoning_content" in chunk.message.additional_kwargs:  # type: ignore
            # Reasoning Content Flag
            if not self.current_output_type == "thinking":
                print("\n💭 思考: ")
                self.current_output_type = "thinking"

            print(f"{self.gray_color}{chunk.message.additional_kwargs['reasoning_content']}{self.reset_color}", end="", flush=True)  # type: ignore
        elif chunk.message.content:  # type: ignore
            # Content Flag
            if not self.current_output_type == "content":
                print("\n 输出: ")
                self.current_output_type = "content"

            print(chunk.message.content, end="", flush=True)  # type: ignore
            
    def on_llm_end(
        self,
        response: LLMResult,
        **kwargs: Any,
    ) -> None:
        self.current_output_type = "thinking"


class NormalStreamingCallback(BaseCallbackHandler):
    def __init__(self):
        self.has_content_started = False

    def on_llm_new_token(
        self,
        token: str,
        **kwargs: Any,
    ):
        """Run on new LLM token. Only available when streaming is enabled."""

        if not self.has_content_started:
            print("\n CONTENT: ", "\n")
            self.has_content_started = True

        print(token, end="", flush=True)
