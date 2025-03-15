import functools
import threading


def singleton(cls):
    """
    单例装饰器
    
    用法:
    @singleton
    class MyClass:
        pass
    """
    # 保存类的唯一实例
    instances = {}
    # 线程锁，确保线程安全
    lock = threading.Lock()
    
    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        # 如果类还没有实例，创建一个
        if cls not in instances:
            with lock:
                # 双重检查锁定模式，避免多线程问题
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance
