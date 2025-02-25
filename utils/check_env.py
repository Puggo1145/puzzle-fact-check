from typing import Optional
from pydantic import SecretStr
import os
import getpass


def check_env(
    env_name: str, 
    prompt_message: Optional[str] = None, 
) -> SecretStr:
    """
    检查环境变量是否存在，如果不存在则提示用户输入
    
    Args:
        env_name: 环境变量名称
        prompt_message: 提示用户输入的消息，如果为None则使用默认消息
        
    Returns:
        环境变量的值或用户输入的值
    """
    # 检查环境变量是否存在
    env_value = os.environ.get(env_name)
    
    # 如果环境变量不存在，提示用户输入
    if not env_value:
        if prompt_message is None:
            prompt_message = f"缺少环境变量 {env_name} 的值，请手动输入"
        
        env_value = getpass.getpass(prompt_message)
        
        # 将用户输入的值设置为环境变量，以便后续使用
        os.environ[env_name] = env_value
    
    return SecretStr(env_value)