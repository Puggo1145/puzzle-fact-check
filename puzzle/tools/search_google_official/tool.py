from typing import Dict, Optional, Any
from langchain_core.tools.base import ArgsSchema
import requests
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from langchain_core.tools import ToolException
import time
import json
import os


class GoogleSearchOfficialInput(BaseModel):
    """Google Official Search API 输入参数 Schema"""

    query: str = Field(description="搜索关键词")
    num: Optional[int] = Field(default=10, description="返回结果的数量，取值范围1-10")
    
    # 可选参数
    c2coff: Optional[str] = Field(
        default=None, 
        description="启用或禁用简体和繁体中文搜索。0: 启用（默认），1: 禁用"
    )
    cr: Optional[str] = Field(
        default=None, 
        description="将搜索结果限制为源自特定国家的文档"
    )
    dateRestrict: Optional[str] = Field(
        default=None, 
        description="根据日期限制结果。支持的值包括：d[数字]：过去天数，w[数字]：过去周数，m[数字]：过去月数，y[数字]：过去年数"
    )
    exactTerms: Optional[str] = Field(
        default=None, 
        description="搜索结果中必须包含的短语"
    )
    excludeTerms: Optional[str] = Field(
        default=None, 
        description="搜索结果中不应出现的单词或短语"
    )
    fileType: Optional[str] = Field(
        default=None, 
        description="将结果限制为指定扩展名的文件"
    )
    filter: Optional[str] = Field(
        default=None, 
        description="控制打开或关闭重复内容过滤器。0: 关闭过滤，1: 打开过滤"
    )
    gl: Optional[str] = Field(
        default=None, 
        description="终端用户的地理位置，使用两字母国家代码"
    )
    highRange: Optional[str] = Field(
        default=None, 
        description="指定搜索范围的结束值"
    )
    hq: Optional[str] = Field(
        default=None, 
        description="将指定的查询词附加到查询中，如同它们与逻辑AND运算符组合一样"
    )
    linkSite: Optional[str] = Field(
        default=None, 
        description="指定所有搜索结果应包含指向特定URL的链接"
    )
    lowRange: Optional[str] = Field(
        default=None, 
        description="指定搜索范围的起始值"
    )
    lr: Optional[str] = Field(
        default=None, 
        description="将搜索限制为用特定语言编写的文档"
    )
    orTerms: Optional[str] = Field(
        default=None, 
        description="提供要在文档中检查的附加搜索词，搜索结果中的每个文档必须至少包含一个附加搜索词"
    )
    rights: Optional[str] = Field(
        default=None, 
        description="基于许可进行过滤"
    )
    siteSearch: Optional[str] = Field(
        default=None, 
        description="指定应始终包含在结果中或排除在结果之外的给定站点"
    )
    siteSearchFilter: Optional[str] = Field(
        default=None, 
        description="控制是否包含或排除siteSearch参数中命名的站点的结果。e: 排除, i: 包含"
    )
    sort: Optional[str] = Field(
        default=None, 
        description="应用于结果的排序表达式"
    )
    start: Optional[int] = Field(
        default=None, 
        description="返回的第一个结果的索引"
    )


class SearchGoogleOfficial(BaseTool):
    """Google官方搜索API工具，提供Google Programmable Search Engine接口访问功能"""

    name: str = "search_google_official"
    description: str = "Google Search 官方 API，调用 Google 搜索引擎时的首选工具，其在全球内容检索上表现出色"
    args_schema: Optional[ArgsSchema] = GoogleSearchOfficialInput

    session: Any = None
    base_url: str = "https://www.googleapis.com/customsearch/v1"
    api_key: Optional[str] = None
    search_engine_id: Optional[str] = None

    def __init__(self, api_key: Optional[str] = None, search_engine_id: Optional[str] = None, **data):
        """初始化Google官方搜索工具

        Args:
            api_key: Google API Key
            search_engine_id: Google Custom Search Engine ID
        """
        super().__init__(**data)
        
        # 优先使用传入的参数，其次使用环境变量
        self.api_key = api_key or os.environ.get("GOOGLE_SEARCH_API_KEY")
        self.search_engine_id = search_engine_id or os.environ.get("GOOGLE_CX_ID")
        
        if not self.api_key or not self.search_engine_id:
            raise ValueError("必须提供Google API Key和Custom Search Engine ID")
            
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """创建带有重试机制的会话"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update(
            {
                "User-Agent": "GoogleSearchOfficialTool/1.0",
            }
        )
        return session

    def _make_request(self, params: Dict) -> Dict:
        """发送请求到Google Custom Search API

        Args:
            params: API参数字典

        Returns:
            API响应的JSON数据
        """
        # 添加API密钥和搜索引擎ID
        params["key"] = self.api_key
        params["cx"] = self.search_engine_id
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = self.session.get(self.base_url, params=params, timeout=10)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = 2**attempt  # 指数退避
                    time.sleep(wait_time)
                else:
                    raise ToolException(f"Google搜索API请求失败: {e}")

        raise ToolException("请求失败")

    def _run(self, **kwargs) -> str:
        """运行Google官方搜索工具

        Args:
            query: 搜索关键词
            num: 返回结果的数量
            以及其他可选参数

        Returns:
            搜索结果的JSON字符串，只包含items部分
        """
        try:
            # 提取所有非None的参数
            params = {k: v for k, v in kwargs.items() if v is not None}
            
            # 确保必须参数存在
            if "query" not in params:
                return json.dumps({"error": "必须提供搜索关键词"}, ensure_ascii=False)
                
            # 将query参数重命名为q，符合Google API要求
            params["q"] = params.pop("query")
            
            # 确保num在有效范围内
            if "num" in params and (params["num"] < 1 or params["num"] > 10):
                params["num"] = max(1, min(10, params["num"]))

            result = self._make_request(params)
            
            # 只返回items部分的结果
            if "items" in result:
                formatted_results = []
                for item in result["items"]:
                    formatted_results.append({
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "displayLink": item.get("displayLink", ""),
                        "formattedUrl": item.get("formattedUrl", ""),
                    })
                return json.dumps(formatted_results, ensure_ascii=False)
            else:
                return json.dumps([], ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({"error": f"搜索执行失败: {str(e)}"}, ensure_ascii=False)
