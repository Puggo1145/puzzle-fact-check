from typing import Dict, List, Optional, Union
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


class SearchGoogleTool(BaseTool):
    """Google搜索工具，提供Google搜索引擎的访问功能"""

    name: str = "search_google"
    description: str = (
        "当你想要通过 Google 搜索引擎检索互联网时使用。Google 搜索引擎在全球信息和学术内容搜索上表现较好"
    )
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
                sleep_interval=self._sleep_interval,  # 使用内部控制参数
                advanced=True,  # 启用高级搜索
                timeout=self._timeout,  # 使用内部控制参数
            )

            # 结构化搜索结果
            results = [
                {
                    "title": result.title,
                    "url": result.url,
                    "description": result.description,
                }
                for result in search_results if result.title and result.description
            ]

            return results

        except Exception as e:
            print(f"Google搜索出错: {str(e)}")
            return None
        
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
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"操作执行失败: {str(e)}"}, ensure_ascii=False)
