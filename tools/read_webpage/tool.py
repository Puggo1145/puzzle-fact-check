from typing import Dict, Optional, cast
from langchain_core.tools.base import ArgsSchema
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
import json
import asyncio
import html2text
from playwright.async_api import async_playwright
import re
import nest_asyncio
import os
import urllib.parse
from datetime import datetime

# 允许嵌套事件循环，解决并发调用问题
nest_asyncio.apply()

WAIT_UNTIL = "domcontentloaded"
TIMEOUT = 10000
DEFAULT_LOGS_DIR = os.path.join("logs", "read_webpage")


class ReadWebpageToolInput(BaseModel):
    """输入参数 Schema"""
    url: str = Field(description="要读取的网页URL")


class ReadWebpageTool(BaseTool):
    """网页读取工具，使用 Playwright 渲染页面并将内容转换为 LLM 友好的 Markdown 格式"""

    name: str = "read_webpage"
    description: str = "当你需要查看网页内容时使用"
    args_schema: Optional[ArgsSchema] = ReadWebpageToolInput

    _browser_args = {
        "headless": True,
        "ignore_default_args": ["--enable-automation"],
    }
    _context_args = {
        "java_script_enabled": True,
        "bypass_csp": True,
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    }

    html_converter: Optional[html2text.HTML2Text] = None
    _loop = None  # 存储事件循环
    
    # 结果保存相关
    save_results: bool = False
    logs_dir: str = DEFAULT_LOGS_DIR

    def __init__(self, save_results: bool = False, logs_dir: str = DEFAULT_LOGS_DIR, **kwargs):
        """初始化网页读取工具
        
        Args:
            save_results: 是否保存结果到日志文件
            logs_dir: 日志保存目录
            **kwargs: 其他参数
        """
        super().__init__(**kwargs)
        # 初始化HTML转换器
        converter = html2text.HTML2Text()
        converter.ignore_links = False  # 确保保留链接
        converter.ignore_images = True
        converter.ignore_tables = False
        converter.body_width = 0  # 不限制宽度
        self.html_converter = converter
        
        # 设置结果保存选项
        self.save_results = save_results
        self.logs_dir = logs_dir
        
        # 如果启用了结果保存，确保日志目录存在
        if self.save_results:
            os.makedirs(self.logs_dir, exist_ok=True)

    def _save_result(self, url: str, result: Dict) -> str:
        """保存结果到日志文件
        
        Args:
            url: 网页URL
            result: 结果字典
            
        Returns:
            保存的文件路径
        """
        if not self.save_results:
            return ""
            
        # 创建安全的文件名
        # 从URL中提取域名部分
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc.replace(".", "_")
        
        # 创建时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 创建文件名
        filename = f"{domain}_{timestamp}.json"
        filepath = os.path.join(self.logs_dir, filename)
        
        # 保存结果
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"Result saved to {filepath}")
            return filepath
        except Exception as e:
            print(f"Failed to save result: {str(e)}")
            return ""

    async def _clean_html(self, page) -> str:
        """清理HTML，移除空节点和无用内容

        Args:
            page: Playwright页面对象

        Returns:
            清理后的HTML内容
        """
        # 移除脚本、样式、注释等无用内容
        await page.evaluate(
            """() => {
            // 移除脚本和样式标签
            const elementsToRemove = document.querySelectorAll('script, style, noscript, iframe, svg');
            elementsToRemove.forEach(el => el.remove());
            
            // 移除注释节点
            const removeComments = (node) => {
                if (!node) return;
                const childNodes = [...node.childNodes];
                childNodes.forEach(child => {
                    if (child.nodeType === 8) { // 注释节点
                        child.remove();
                    } else {
                        removeComments(child);
                    }
                });
            };
            removeComments(document.body);
            
            // 移除空白节点和只包含空格的文本节点
            const removeEmptyNodes = (node) => {
                if (!node) return;
                const childNodes = [...node.childNodes];
                childNodes.forEach(child => {
                    if (child.nodeType === 3 && child.textContent.trim() === '') { // 空文本节点
                        child.remove();
                    } else if (child.nodeType === 1) { // 元素节点
                        removeEmptyNodes(child);
                        // 如果元素没有子节点且不是自闭合标签，则移除
                        const selfClosingTags = ['img', 'br', 'hr', 'input', 'meta', 'link'];
                        if (child.childNodes.length === 0 && !selfClosingTags.includes(child.tagName.toLowerCase())) {
                            // 检查是否有有意义的属性
                            const hasImportantAttrs = child.hasAttribute('id') || 
                                                     child.hasAttribute('class') || 
                                                     child.hasAttribute('role');
                            if (!hasImportantAttrs) {
                                child.remove();
                            }
                        }
                    }
                });
            };
            removeEmptyNodes(document.body);
        }"""
        )

        # 获取清理后的HTML
        return await page.content()

    async def _extract_main_content(self, page) -> str:
        """尝试提取页面的主要内容区域

        Args:
            page: Playwright页面对象

        Returns:
            主要内容区域的HTML，如果无法确定则返回完整HTML
        """
        # 尝试识别主要内容区域
        try:
            main_content = await page.evaluate(
                """() => {
                // 常见的主要内容容器选择器
                const mainSelectors = [
                    'main',
                    'article',
                    '#content',
                    '.content',
                    '.main-content',
                    '.article-content',
                    '.post-content',
                    '.entry-content',
                    '[role="main"]'
                ];
                
                // 尝试找到主要内容容器
                for (const selector of mainSelectors) {
                    const element = document.querySelector(selector);
                    if (element && element.textContent.trim().length > 200) {
                        return element.outerHTML;
                    }
                }
                
                // 如果找不到明确的主要内容区域，检查body是否存在
                if (document.body) {
                    return document.body.outerHTML;
                }
                
                // 如果连body都不存在，返回整个HTML
                return document.documentElement ? document.documentElement.outerHTML : '';
            }"""
            )
            return main_content if main_content else ""
        except Exception as e:
            # 如果提取失败，记录错误并返回空字符串
            print(f"Error extracting main content: {str(e)}")
            try:
                # 尝试获取整个页面内容作为备选
                return await page.content()
            except:
                return ""

    async def _fetch_page_content(self, url: str) -> Dict:
        """使用Playwright异步获取页面内容

        Args:
            url: 网页URL

        Returns:
            包含页面内容和元数据的字典
        """
        result = {
            "url": url,
            "title": "",
            "content": "",
            "error": None,
            "timestamp": datetime.now().isoformat(),
        }

        try:
            # 使用单独的playwright实例，避免并发问题
            async with async_playwright() as p:
                # 启动浏览器
                browser = await p.chromium.launch(**self._browser_args)

                # 创建上下文和页面
                context = await browser.new_context(**self._context_args)
                page = await context.new_page()

                # 设置超时
                page.set_default_timeout(TIMEOUT)

                # 导航到页面
                try:
                    await page.goto(url, wait_until=WAIT_UNTIL)
                except Exception as e:
                    # 如果导航超时，但页面已经有内容，我们仍然继续处理
                    result["error"] = f"Navigation incomplete: {str(e)}"

                try:
                    # 获取页面标题
                    result["title"] = await page.title()
                except Exception as e:
                    result["error"] = f"{result.get('error', '')} Title extraction failed: {str(e)}"

                try:
                    # 清理HTML
                    clean_html = await self._clean_html(page)
                    
                    # 尝试提取主要内容
                    main_content = await self._extract_main_content(page)
                    
                    # 使用主要内容，如果它足够长；否则使用清理后的完整HTML
                    html_content = main_content if main_content and len(main_content) > 500 else clean_html

                    # 转换HTML到Markdown
                    if html_content:
                        html_converter = cast(html2text.HTML2Text, self.html_converter)
                        markdown_content = html_converter.handle(html_content)
                        
                        # 后处理Markdown，移除多余的空行和空格
                        markdown_content = self._clean_markdown(markdown_content)
                        
                        result["content"] = markdown_content
                except Exception as e:
                    result["error"] = f"{result.get('error', '')} Content extraction failed: {str(e)}"

                # 关闭浏览器
                await browser.close()

        except Exception as e:
            result["error"] = f"Operation failed: {str(e)}"

        return result

    def _clean_markdown(self, markdown: str) -> str:
        """清理Markdown内容，移除多余的空行和格式问题

        Args:
            markdown: 原始Markdown内容

        Returns:
            清理后的Markdown内容
        """
        # 移除连续的空行，将3个以上的换行符替换为2个
        markdown = re.sub(r"\n{3,}", "\n\n", markdown)

        # 移除行首行尾的空白字符
        lines = [line.strip() for line in markdown.split("\n")]

        # 移除空行
        lines = [line for line in lines if line]

        # 重新组合内容
        cleaned_markdown = "\n\n".join(lines)

        return cleaned_markdown

    def _get_or_create_event_loop(self):
        """获取现有事件循环或创建新的事件循环"""
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            # 如果没有事件循环，创建一个新的
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop

    def read_webpage(
        self,
        url: str,
    ) -> Dict:
        """读取网页内容

        Args:
            url: 网页URL

        Returns:
            包含页面内容和元数据的字典
        """
        # 使用现有事件循环或创建新的
        loop = self._get_or_create_event_loop()
        
        # 在当前事件循环中运行异步任务
        result = loop.run_until_complete(self._fetch_page_content(url=url))
        
        # 如果启用了结果保存，保存结果
        if self.save_results:
            self._save_result(url, result)
            
        return result

    def _run(
        self,
        url: str,
    ) -> str:
        """运行工具

        Args:
            url: 网页URL

        Returns:
            页面内容的JSON字符串
        """
        try:
            result = self.read_webpage(url=url)
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            error_result = {
                "url": url,
                "error": f"操作执行失败: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }
            
            # 如果启用了结果保存，保存错误结果
            if self.save_results:
                self._save_result(url, error_result)
                
            return json.dumps(error_result, ensure_ascii=False)
