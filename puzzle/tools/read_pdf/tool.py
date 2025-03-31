from typing import Dict, List, Optional, Any, Literal
from langchain_core.tools.base import ArgsSchema
import requests
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from langchain_core.tools import ToolException
import io
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import PyPDF2
import json


MAX_SUCCESSIVE_PAGES = 5

class PDFReaderToolInput(BaseModel):
    """输入参数 Schema"""

    url: str = Field(description="PDF文件的URL链接")
    start_page: int = Field(
        default=1, 
        description="开始读取的页码（默认从1开始）"
    )
    end_page: Optional[int] = Field(
        default=None, 
        description="结束读取的页码（不提供则默认读取到文档末尾）。注意，一次读取最大只能连续读取5页（end_page - start_page <= 5）",
    )


class ReadPDFTool(BaseTool):
    """在线PDF阅读工具，可以读取在线PDF文件的内容而无需下载"""

    name: str = "read_pdf"
    description: str = "当你需要阅读在线PDF文档时使用，可以指定页码范围进行读取"
    args_schema: Optional[ArgsSchema] = PDFReaderToolInput

    session: Any = None

    def __init__(self, **data):
        """初始化PDF阅读工具"""
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
                "User-Agent": "PDFReaderTool/1.0",
            }
        )
        return session

    def _get_pdf_from_url(self, url: str) -> io.BytesIO:
        """从URL获取PDF文件内容

        Args:
            url: PDF文件的URL

        Returns:
            BytesIO对象，包含PDF文件内容
        """
        try:
            response = self.session.get(url, stream=True, timeout=30)
            
            # 检查响应头确认是PDF文件
            content_type = response.headers.get('Content-Type', '').lower()
            if 'application/pdf' not in content_type and not url.lower().endswith('.pdf'):
                raise ToolException(f"提供的URL不是PDF文件: {content_type}")
                
            response.raise_for_status()
            return io.BytesIO(response.content)
        except requests.exceptions.RequestException as e:
            raise ToolException(f"获取PDF文件失败: {str(e)}")

    def _extract_text_from_pdf(
        self, pdf_file: io.BytesIO, start_page: int = 1, end_page: Optional[int] = None
    ) -> Dict:
        """从PDF文件提取文本内容

        Args:
            pdf_file: 包含PDF内容的BytesIO对象
            start_page: 开始页码（从1开始）
            end_page: 结束页码，如不指定则读取到文档末尾

        Returns:
            包含PDF内容的字典
        """
        try:
            reader = PyPDF2.PdfReader(pdf_file)
            total_pages = len(reader.pages)
            
            # 验证页码范围
            if start_page < 1:
                start_page = 1
            if end_page is None:
                # 如果未指定结束页码，默认只读取起始页后的5页
                end_page = min(start_page + 4, total_pages)
            else:
                # 确保一次最多只读取5页
                max_allowed_pages = 5
                if end_page - start_page + 1 > max_allowed_pages:
                    end_page = start_page + max_allowed_pages - 1
                
                # 确保不超过文档总页数
                end_page = min(end_page, total_pages)
                
            # 确保start_page不大于end_page和总页数
            start_page = min(start_page, total_pages)
            
            # 提取内容
            content = []
            
            for page_num in range(start_page - 1, end_page):
                page = reader.pages[page_num]
                
                # 提取页面文本
                page_text = page.extract_text() or "【此页面无文本内容】"
                
                content.append({
                    "page_number": page_num + 1,
                    "text": page_text
                })
            
            return {
                "total_pages": total_pages,
                "read_pages": {
                    "start": start_page,
                    "end": end_page
                },
                "content": content
            }
            
        except Exception as e:
            raise ToolException(f"解析PDF文件失败: {str(e)}")

    def _run(self, url: str, start_page: int = 1, end_page: Optional[int] = None) -> str:
        """运行工具

        Args:
            url: PDF文件的URL
            start_page: 开始页码（从1开始）
            end_page: 结束页码，如不指定则读取到文档末尾

        Returns:
            PDF内容的JSON字符串
        """
        try:
            # 检查是否请求了过多页数
            if end_page is not None and start_page is not None:
                if end_page - start_page > MAX_SUCCESSIVE_PAGES:
                    return json.dumps({
                        "error": f"单次请求最多允许读取{MAX_SUCCESSIVE_PAGES}页。请调整参数，从第{start_page}页读取最大后{MAX_SUCCESSIVE_PAGES}页的内容"
                    }, ensure_ascii=False)
            
            pdf_file = self._get_pdf_from_url(url)
            result = self._extract_text_from_pdf(pdf_file, start_page, end_page)
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"读取PDF失败: {str(e)}"}, ensure_ascii=False)
