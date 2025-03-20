from typing import Annotated
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from langchain.tools import tool

@tool
def get_current_time(
    timezone: Annotated[str, "时区名称"] = "UTC"
) -> str:
    """
    当你需要知道当前的准确日期和时间时使用此工具。
    
    Args:
        timezone: 时区名称，默认为"UTC"。常用时区包括：
            - "UTC": 协调世界时
            - "Asia/Shanghai": 中国标准时间 (UTC+8)
            - "America/New_York": 美国东部时间
            - "Europe/London": 英国时间
            - "Asia/Tokyo": 日本标准时间
    
    Returns:
        包含当前日期和时间的字符串，格式为"YYYY-MM-DD HH:MM:SS 星期几 时区"
    
    Example:
        >>> get_current_time("Asia/Shanghai")
        '2023-11-02 15:30:45 星期四 CST+0800'
    """
    
    try:
        # 获取指定时区的当前时间
        tz = ZoneInfo(timezone)
        current_time = datetime.now(tz)
        
        # 获取星期几（中文）
        weekday_map = {
            0: "星期一",
            1: "星期二",
            2: "星期三",
            3: "星期四",
            4: "星期五",
            5: "星期六",
            6: "星期日"
        }
        weekday = weekday_map[current_time.weekday()]
        
        # 格式化时间字符串
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        timezone_name = current_time.strftime("%Z%z")
        
        return f"{formatted_time} {weekday} {timezone_name}"
    
    except ZoneInfoNotFoundError:
        return f"错误：未知时区 '{timezone}'。请使用有效的时区名称，如 'UTC', 'Asia/Shanghai', 'America/New_York' 等。"
    except Exception as e:
        return f"获取时间时出错：{str(e)}" 