import time
import sys
import functools
from typing import Callable, Any, Optional


def response_timer(description: Optional[str] = None):
    """
    一个模型响应时间计时器
    
    Args:
        description: 可选的描述文本，显示在计时器前面
        
    Returns:
        装饰后的函数
    
    Example:
        @response_timer("模型思考中")
        def get_model_response():
            # 模型调用代码
            return response
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 准备计时器显示文本
            prefix = f"{description}: " if description else "执行时间: "
            
            # 开始计时
            start_time = time.time()
            
            # 创建计时器线程
            stop_timer = False
            
            def update_timer():
                elapsed = 0
                while not stop_timer:
                    elapsed = time.time() - start_time
                    # 在同一行更新时间
                    sys.stdout.write(f"\r{prefix}{elapsed:.2f}秒")
                    sys.stdout.flush()
                    time.sleep(0.1)
                # 最后一次更新，显示最终时间
                sys.stdout.write(f"\r{prefix}{elapsed:.2f}秒 - 完成\n")
                sys.stdout.flush()
            
            # 使用线程运行计时器
            import threading
            timer_thread = threading.Thread(target=update_timer)
            timer_thread.daemon = True
            timer_thread.start()
            
            try:
                # 执行被装饰的函数
                result = func(*args, **kwargs)
                return result
            finally:
                # 停止计时器
                stop_timer = True
                timer_thread.join(timeout=1.0)  # 等待计时器线程结束
        
        return wrapper
    return decorator 