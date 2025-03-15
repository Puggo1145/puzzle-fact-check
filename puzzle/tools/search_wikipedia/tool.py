from typing import Dict, List, Optional, Any, Literal
from langchain_core.tools.base import ArgsSchema
import requests
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from langchain_core.tools import ToolException
import time
import json
import re
from bs4 import BeautifulSoup


WikipediaSearchAction = Literal[
    "search_by_titles",
    "search_by_content",
    "get_page",
    # "get_page_source",
]

class WikipediaToolInput(BaseModel):
    """输入参数 Schema"""

    action: WikipediaSearchAction = Field(
        description="要执行的 wikipedia 检索方式",
        examples=[
            {"search_by_titles": "使用词条名称搜索词条，返回匹配的词条列表。通常在给定关键词可能是一个明确的名词、术语、知识元素等时使用"},
            {"search_by_content": "使用内容关键词搜索词条，返回匹配的词条列表。通常在关键词较为模糊时使用"},
            # 这两个参数要解析的数据量非常大
            {"get_page": "返回目标词条的词条页面定义"},
            # {"get_page_source": "返回目标词条的参考资料"},
        ],
    )
    query: str = Field(description="搜索关键词或词条名称")
    limit: Optional[int] = Field(default=5, description="返回结果的最大数量")
    language: str = Field(
        description="目标词条的语言",
        examples=[
            "zh",
            "en",
            "fr",
            "de",
            "es",
            "it",
            "ja",
            "ko",
            "pt",
            "ru",
            "sv",
            "tr",
            "vi",
        ],
    )


class SearchWikipediaTool(BaseTool):
    """维基百科检索工具，提供多种维基百科API访问功能"""

    name: str = "search_wikipedia"
    description: str = "当你想要检索维基百科的时候使用"
    args_schema: Optional[ArgsSchema] = WikipediaToolInput

    session: Any = None
    base_url: str = "https://api.wikimedia.org/core/v1/wikipedia"

    def __init__(self, **data):
        """初始化维基百科工具"""
        super().__init__(**data)
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
                "User-Agent": "WikipediaSearchTool/1.0",
            }
        )
        return session

    def _make_request(self, url: str) -> Dict:
        """发送请求到维基百科 API

        Args:
            url: 完整的API URL

        Returns:
            API响应的JSON数据
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = 2**attempt  # 指数退避
                    print(f"请求失败: {e}. 等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    raise ToolException(f"维基百科API请求失败: {e}")

        raise ToolException("请求失败")

    def search_content(
        self, query: str, limit: int = 5, language: str = "zh"
    ) -> List[Dict]:
        """使用内容关键词搜索维基百科词条

        Args:
            query: 搜索查询
            limit: 返回结果的最大数量
            language: 维基百科语言代码

        Returns:
            搜索结果列表
        """
        url = f"{self.base_url}/{language}/search/page?q={query}&limit={limit}"
        result = self._make_request(url)

        if "pages" in result:
            return [
                {
                    "pageid": page.get("id", ""),
                    "key": page.get("key", ""),
                    "title": page.get("title", ""),
                    "description": page.get("description", ""),
                    "snippet": page.get("excerpt", "")
                    .replace('<span class="searchmatch">', "")
                    .replace("</span>", ""),
                }
                for page in result["pages"]
            ]
        return []

    def search_title(
        self, query: str, limit: int = 5, language: str = "zh"
    ) -> List[Dict]:
        """搜索维基百科标题

        Args:
            query: 搜索查询
            limit: 返回结果的最大数量
            language: 维基百科语言代码

        Returns:
            标题搜索结果列表
        """
        url = f"{self.base_url}/{language}/search/title?q={query}&limit={limit}"

        result = self._make_request(url)

        if "pages" in result:
            return [
                {
                    "pageid": page.get("id", ""),
                    "key": page.get("key", ""),
                    "title": page.get("title", ""),
                    "description": page.get("description", ""),
                }
                for page in result["pages"]
            ]
        return []

    def _parse_wiki_html(self, html_content: str, max_paragraphs: int = 3) -> str:
        """解析维基百科HTML内容，提取词条开头的关键定义

        Args:
            html_content: 维基百科页面的HTML内容
            max_paragraphs: 要提取的最大段落数量

        Returns:
            提取的定义文本
        """
        if not html_content:
            return ""
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 移除参考文献、表格等不需要的元素
        for element in soup.find_all(['table', 'sup', 'span.reference']):
            element.decompose()
            
        # 获取正文内容
        paragraphs = soup.find_all('p')
        
        # 过滤掉空段落
        valid_paragraphs = []
        for p in paragraphs:
            text = p.get_text().strip()
            if text and len(text) > 50:  # 忽略太短的段落
                valid_paragraphs.append(text)
            if len(valid_paragraphs) >= max_paragraphs:
                break
                
        # 清理文本
        definition_text = "\n\n".join(valid_paragraphs)
        
        # 移除多余空格和换行符
        definition_text = re.sub(r'\s+', ' ', definition_text)
        # 移除引用标记 [1], [2] 等
        definition_text = re.sub(r'\[\d+\]', '', definition_text)
        
        return definition_text.strip()

    def get_page(self, title: str, language: str = "zh") -> Dict:
        """获取特定页面的内容

        Args:
            title: 页面标题
            language: 维基百科语言代码

        Returns:
            页面内容
        """
        url = f"{self.base_url}/{language}/page/{title.replace(' ', '_')}/with_html"

        try:
            result = self._make_request(url)
            html_content = result.get("html", "")
            
            # 解析HTML提取定义
            definition = self._parse_wiki_html(html_content)

            return {
                "pageid": result.get("id", ""),
                "key": result.get("key", ""),
                "title": result.get("title", ""),
                "definition": definition,
                # "html": html_content,  # 保留原始HTML以备需要
            }
        except Exception as e:
            raise ToolException(f"无法获取页面内容: {str(e)}")

    def get_page_source(self, title: str, language: str = "zh") -> Dict:
        """返回目标词条的参考资料

        Args:
            title: 页面标题
            language: 维基百科语言代码

        Returns:
            词条使用的参考资料
        """

        url = f"{self.base_url}/{language}/page/{title.replace(' ', '_')}"

        try:
            result = self._make_request(url)

            return {
                "pageid": result.get("id", ""),
                "key": result.get("key", ""),
                "title": result.get("title", ""),
                "source": result.get("source", ""),
            }
        except Exception as e:
            raise ToolException(f"无法获取页面参考资料: {str(e)}")

    def _run(
        self, action: str, query: str, limit: int = 5, language: str = "zh"
    ) -> str:
        """运行工具

        Args:
            action: 要执行的操作
            query: 搜索关键词或词条名称
            limit: 返回结果的最大数量
            language: 维基百科语言代码

        Returns:
            搜索结果的JSON字符串
        """

        try:
            if action == "search_by_content":
                result = self.search_content(query, limit, language)
            elif action == "search_by_titles":
                result = self.search_title(query, limit, language)
            elif action == "get_page":
                result = self.get_page(query, language)
            elif action == "get_page_source":
                result = self.get_page_source(query, language)
            else:
                result = {"error": f"未知操作: {action}"}

            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"操作执行失败: {str(e)}"}, ensure_ascii=False)
