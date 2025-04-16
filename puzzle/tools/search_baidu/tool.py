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


class BaiduToolInput(BaseModel):
    """输入参数 Schema"""

    query: str = Field(description="搜索关键词")
    limit: Optional[int] = Field(
        default=10, 
        description="返回结果的最大数量，如果不指定则返回所有结果",
        ge=10,
        le=100,
    )
    safe: Optional[bool] = Field(
        default=True,
        description="是否启用安全搜索",
    )


class SearchBaiduTool(BaseTool):
    """百度搜索工具，提供百度搜索引擎的访问功能"""

    name: str = "search_baidu"
    description: str = "通过百度搜索检索互联网，其在中文内容检索上表现出色"
    args_schema: Optional[ArgsSchema] = BaiduToolInput

    session: Any = None
    base_url: str = "https://www.baidu.com/s"

    def __init__(self, **data):
        """初始化百度搜索工具"""
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
            "Referer": "https://www.baidu.com/",
            "Connection": "keep-alive",
        })
        
        return session

    def _make_request(self, url: str, params: Dict) -> str:
        """发送请求到百度搜索，增强处理中文搜索"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # 对于中文查询，尝试使用不同的请求方式
                has_chinese = any('\u4e00' <= char <= '\u9fff' for char in params.get('wd', ''))
                
                if has_chinese:
                    # 对于中文查询，直接构建URL而不是使用params
                    encoded_query = urllib.parse.quote(params['wd'])
                    full_url = f"{url}?wd={encoded_query}"
                    if 'safe' in params and params['safe'] == "1":
                        full_url += "&safe=1"
                    
                    response = self.session.get(full_url, timeout=10)
                else:
                    # 对于英文查询，使用标准params方式
                    response = self.session.get(url, params=params, timeout=10)
                    
                response.raise_for_status()
                
                # 检查是否被重定向到验证页面
                if "wappass.baidu.com" in response.url:
                    if attempt < max_retries - 1:
                        print(f"检测到重定向到验证页面，尝试其他方法...")
                        continue
                    else:
                        raise ToolException("百度要求验证，无法完成搜索")
                        
                return response.text
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = 2**attempt  # 指数退避
                    print(f"请求失败: {e}. 等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    raise ToolException(f"百度搜索请求失败: {e}")

        raise ToolException("请求失败")

    def search(
        self, 
        query: str, 
        limit: Optional[int] = None, 
        safe: bool = True
    ) -> List[Dict]:
        """搜索百度

        Args:
            query: 搜索查询
            limit: 返回结果的最大数量，如果为None则返回所有结果
            safe: 是否启用安全搜索

        Returns:
            搜索结果列表
        """
        # 基础查询参数
        params = {
            "wd": query,  # 百度使用wd作为查询参数
        }
        
        # 根据设置添加安全搜索参数
        if safe:
            params["safe"] = "1"
        
        html_content = self._make_request(self.base_url, params)
        
        # 解析HTML内容
        return self._parse_search_results(html_content, limit)

    def _parse_search_results(self, html_content: str, limit: Optional[int] = None) -> List[Dict]:
        """解析百度搜索结果HTML

        Args:
            html_content: 百度搜索结果页面的HTML内容
            limit: 返回结果的最大数量，如果为None则返回所有结果

        Returns:
            结构化的搜索结果列表
        """
        results = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 首先找到内容容器 #content_left
        content_left = soup.select_one('#content_left')
        
        if content_left:
            # 在容器中查找搜索结果 - 匹配 "result" 或 "c-container" 类名的部分
            search_results = content_left.select('div[class*="result"][class*="c-container"]')
            
            # 如果没有找到结果，试着用更宽松的选择器
            if not search_results:
                search_results = content_left.select('div[class*="result"], div[class*="c-container"]')
            
            for i, result in enumerate(search_results):
                if limit is not None and i >= limit:
                    break
                    
                # 提取标题 - 通常在 h3.c-title 内的 a 标签中
                title_element = result.select_one('h3[class*="c-title"] a') or result.select_one('h3 a')
                title = title_element.get_text().strip() if title_element else None
                
                # URL - 百度使用了重定向链接，提取 href
                url = None
                if title_element and title_element.has_attr('href'):
                    url = title_element['href']
                
                # 提取摘要 - 使用包含 "content-right" 的类名
                snippet_element = result.select_one('span[class*="content-right"]')
                snippet = snippet_element.get_text().strip() if snippet_element else None
                
                # 提取网站来源名称
                site_element = result.select_one('[class*="source"]')
                site = site_element.get_text().strip() if site_element else None
                
                # 提取日期（如果有）
                date_element = result.select_one('div[class*="content-limit"] .c-color-gray2')
                date = date_element.get_text().strip() if date_element else None
                
                # 只有在找到标题时才添加结果
                if title:
                    results.append({
                        "title": title,
                        "link": url,
                        "snippet": snippet,
                        "site": site,
                        "date": date,
                    })
        
        # 如果在 #content_left 中找不到结果，尝试直接在整个页面中搜索
        if not results:
            # 查找所有可能包含搜索结果的容器
            containers = soup.select('div[class*="result"], div[class*="c-container"]')
            
            for i, container in enumerate(containers):
                if limit is not None and i >= limit:
                    break
                
                # 标题检查
                title_element = (
                    container.select_one('h3[class*="c-title"] a') or 
                    container.select_one('h3 a') or
                    container.select_one('a[class*="title"]')
                )
                title = title_element.get_text().strip() if title_element else None
                
                # URL检查
                url = None
                if title_element and title_element.has_attr('href'):
                    url = title_element['href']
                
                # 摘要检查 - 尝试多种可能的选择器
                snippet_element = (
                    container.select_one('span[class*="content-right"]') or
                    container.select_one('div[class*="pure-test-wrap"] span') or
                    container.select_one('div[class*="content"]') or
                    container.select_one('div[class*="abstract"]')
                )
                snippet = snippet_element.get_text().strip() if snippet_element else None
                
                # 只有在找到标题时才添加结果
                if title:
                    results.append({
                        "title": title,
                        "link": url,
                        "snippet": snippet,
                        "site": None,
                        "date": None,
                    })
        
        return results

    def _run(
        self, query: str, limit: Optional[int] = None, safe: bool = True
    ) -> str:
        """运行工具

        Args:
            query: 搜索关键词
            limit: 返回结果的最大数量，如果为None则返回所有结果
            safe: 是否启用安全搜索

        Returns:
            搜索结果的JSON字符串
        """
        try:
            result = self.search(query, limit, safe)
            # Ensure proper encoding for all Unicode characters by disabling ASCII escaping
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"操作执行失败: {str(e)}"}, ensure_ascii=False) 