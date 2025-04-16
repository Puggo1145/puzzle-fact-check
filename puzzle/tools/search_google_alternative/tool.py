from typing import Dict, List, Optional
from langchain_core.tools.base import ArgsSchema
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from langchain_core.tools import ToolException
import json
from googlesearch import search as google_search


class GoogleToolInput(BaseModel):
    """输入参数 Schema"""

    query: str = Field(description="搜索关键词")
    limit: Optional[int] = Field(
        default=None, description="返回结果的最大数量，如果不指定则返回所有结果"
    )
    lang: Optional[str] = Field(
        default="zh-CN",
        description="搜索结果的语言",
        examples=[
            "zh-CN",  # 中文
            "en",  # 英文
            "fr",  # 法语
            "de",  # 德语
            "ja",  # 日语
        ],
    )
    region: Optional[str] = Field(
        default=None,
        description="搜索结果的地区/国家代码",
        examples=[
            "us",  # 美国
            "uk",  # 英国
            "cn",  # 中国
            "jp",  # 日本
            "de",  # 德国
        ],
    )
    unique: Optional[bool] = Field(
        default=True,
        description="是否只返回唯一的链接结果",
    )


class SearchGoogleAlternative(BaseTool):
    """使用爬虫实现的 Google 搜索替代版，没钱的时候用这个"""

    name: str = "search_google_alternative"
    description: str = "官方 Google 搜索 api 的下位替代，当官方 api 无法使用的时候使用。该工具的访问速度可能稍慢，在访问次数过多时会被限流"
    args_schema: Optional[ArgsSchema] = GoogleToolInput

    # 内部控制参数
    _sleep_interval: float = 1.0
    _timeout: int = 10

    def search(
        self, 
        query: str, 
        limit: Optional[int] = None, 
        lang: str = "zh-CN",
        region: Optional[str] = None,
        unique: bool = True,
    ) -> List[Dict] | None:
        """搜索Google

        Args:
            query: 搜索查询
            limit: 返回结果的最大数量，如果为None则返回所有结果
            lang: 搜索结果的语言
            region: 搜索结果的地区/国家代码
            unique: 是否只返回唯一的链接结果

        Returns:
            搜索结果列表
        """
        # 如果没有指定limit，默认获取10个结果（一个页面的所有结果）
        num_results = limit if limit is not None else 10
        # 语言参数
        lang_param = lang.split("-")[0] if "-" in lang else lang

        try:
            search_results = google_search(
                query,
                num_results=num_results,
                lang=lang_param,
                region=region,
                unique=unique,
                sleep_interval=int(self._sleep_interval),  # 使用内部控制参数，转换为int
                advanced=True,  # 启用高级搜索
                timeout=self._timeout,  # 使用内部控制参数
            )

            # 结构化搜索结果
            results = []
            for result in search_results:
                try:
                    # 使用字典访问方式，避免属性访问的类型检查问题
                    result_dict = {
                        "title": getattr(result, "title", ""),
                        "link": getattr(result, "link", ""),
                        "snippet": getattr(result, "description", "")
                    }
                    if result_dict["title"] and result_dict["snippet"]:
                        results.append(result_dict)
                except Exception:
                    # 忽略无法处理的结果
                    continue

            return results

        except Exception as e:
            error_message = f"Google搜索出错: {str(e)}"
            print(error_message)
            # 返回一个包含错误信息的字典列表，而不是字符串列表
            return [{
                "title": "搜索错误",
                "link": "",
                "snippet": error_message
            }]
        
    def _run(
        self, 
        query: str, 
        limit: Optional[int] = None, 
        lang: str = "zh-CN",
        region: Optional[str] = None,
        unique: bool = True,
    ) -> str:
        """运行工具

        Args:
            query: 搜索关键词
            limit: 返回结果的最大数量，如果为None则返回所有结果
            lang: 搜索结果的语言
            region: 搜索结果的地区/国家代码
            unique: 是否只返回唯一的链接结果

        Returns:
            搜索结果的JSON字符串
        """
        try:
            result = self.search(
                query=query, 
                limit=limit, 
                lang=lang,
                region=region,
                unique=unique,
            )
            # 确保即使搜索返回None也能返回一个空列表
            if result is None:
                return json.dumps([], ensure_ascii=False)
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            # 返回一个包含错误信息的结果，确保LLM能够理解搜索失败
            error_result = [{
                "title": "搜索错误",
                "link": "",
                "snippet": f"Google搜索执行失败: {str(e)}"
            }]
            return json.dumps(error_result, ensure_ascii=False)
