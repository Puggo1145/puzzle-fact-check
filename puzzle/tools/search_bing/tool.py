import requests
import time
import json
import urllib.parse
from typing import Dict, List, Optional, Any, Literal
from langchain_core.tools.base import ArgsSchema
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from langchain_core.tools import ToolException
from bs4 import BeautifulSoup


class BingToolInput(BaseModel):
    """输入参数 Schema"""

    query: str = Field(description="搜索关键词")
    limit: Optional[int] = Field(
        default=10, 
        description="返回结果的最大数量，如果不指定则返回所有结果",
        ge=10,
        le=100,
    )
    ensearch: Optional[bool] = Field(
        default=False,
        description="是否使用国际版搜索（默认为中国版）",
        examples=[
            True,  # 使用国际版
            False,  # 使用中国版
        ],
    )


class SearchBingTool(BaseTool):
    """Bing搜索工具，提供Bing搜索引擎的访问功能"""

    name: str = "search_bing"
    description: str = "当你想要通过 Bing 搜索引擎检索互联网时使用。Bing 搜索引擎在中文和外文搜索结果上表现较为平衡"
    args_schema: Optional[ArgsSchema] = BingToolInput

    session: Any = None
    base_url: str = "https://www.bing.com/search"

    def __init__(self, **data):
        """初始化Bing搜索工具"""
        super().__init__(**data)
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """创建带有更真实浏览器特征的会话"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # 使用更完整的浏览器标识和Cookie支持
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "Referer": "https://www.bing.com/",
            "Connection": "keep-alive",
        })
        
        return session

    def _make_request(self, url: str, params: Dict) -> str:
        """发送请求到Bing搜索，增强处理中文搜索"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # 对于中文查询，尝试使用不同的请求方式
                has_chinese = any('\u4e00' <= char <= '\u9fff' for char in params.get('q', ''))
                
                if has_chinese:
                    # 对于中文查询，直接构建URL而不是使用params
                    encoded_query = urllib.parse.quote(params['q'])
                    full_url = f"{url}?q={encoded_query}"
                    if 'ensearch' in params and params['ensearch'] == "1":
                        full_url += "&ensearch=1"
                    
                    response = self.session.get(full_url, timeout=10)
                else:
                    # 对于英文查询，使用标准params方式
                    response = self.session.get(url, params=params, timeout=10)
                    
                response.raise_for_status()
                
                # 检查是否被重定向到验证页面
                if "www.bing.com/ck/a" in response.url or "login.live.com" in response.url:
                    if attempt < max_retries - 1:
                        print(f"检测到重定向到验证页面，尝试其他方法...")
                        continue
                    else:
                        raise ToolException("Bing要求验证，无法完成搜索")
                        
                return response.text
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = 2**attempt  # 指数退避
                    print(f"请求失败: {e}. 等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    raise ToolException(f"Bing搜索请求失败: {e}")

        raise ToolException("请求失败")

    def search(
        self, 
        query: str, 
        limit: Optional[int] = None, 
        ensearch: bool = False
    ) -> List[Dict]:
        """搜索Bing

        Args:
            query: 搜索查询
            limit: 返回结果的最大数量，如果为None则返回所有结果
            ensearch: 是否使用国际版搜索

        Returns:
            搜索结果列表
        """
        # 基础查询参数
        params = {
            "q": query,  # 将在_make_request中进行URL编码
        }
        
        # 根据设置添加国际版参数
        if ensearch:
            params["ensearch"] = "1"
        
        html_content = self._make_request(self.base_url, params)
        
        # 解析HTML内容
        return self._parse_search_results(html_content, limit)

    def _parse_search_results(self, html_content: str, limit: Optional[int] = None) -> List[Dict]:
        """解析Bing搜索结果HTML

        Args:
            html_content: Bing搜索结果页面的HTML内容
            limit: 返回结果的最大数量，如果为None则返回所有结果

        Returns:
            结构化的搜索结果列表
        """
        results = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 查找主要搜索结果
        search_results = soup.select('#b_results > li.b_algo')
        
        for i, result in enumerate(search_results):
            if limit is not None and i >= limit:
                break
                
            # 标题
            title_element = result.select_one('h2 a')
            title = title_element.get_text() if title_element else None
            
            # 页面 title
            from_title_element = result.select_one('.tptt')
            from_title = from_title_element.get_text() if from_title_element else None
            
            # URL
            url = title_element.get('href') if title_element else None
            
            # 提取摘要
            snippet_element = result.select_one('.b_caption p')
            snippet = snippet_element.get_text() if snippet_element else None
            
            # 提取日期（如果有）
            date_element = result.select_one('.news_dt')
            date = date_element.get_text() if date_element else None
            
            results.append({
                "title": title,
                "from": from_title,
                "url": url,
                "snippet": snippet,
                "date": date,
            })
            
        return results

    def _run(
        self, query: str, limit: Optional[int] = None, ensearch: bool = False
    ) -> str:
        """运行工具

        Args:
            query: 搜索关键词
            limit: 返回结果的最大数量，如果为None则返回所有结果
            ensearch: 是否使用国际版搜索

        Returns:
            搜索结果的JSON字符串
        """
        try:
            result = self.search(query, limit, ensearch)
            # Ensure proper encoding for all Unicode characters by disabling ASCII escaping
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"操作执行失败: {str(e)}"}, ensure_ascii=False) 