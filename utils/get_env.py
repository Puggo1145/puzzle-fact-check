from typing import Optional, Union, overload, Literal
from pydantic import SecretStr
import os
import getpass


@overload
def get_env(
    env_name: str, 
    prompt_message: Optional[str] = None, 
    as_secret_str: Literal[False] = False
) -> str: ...

@overload
def get_env(
    env_name: str, 
    prompt_message: Optional[str] = None, 
    as_secret_str: Literal[True] = True
) -> SecretStr: ...

def get_env(
    env_name: str, 
    prompt_message: Optional[str] = None, 
    as_secret_str: bool = False
) -> Union[SecretStr, str]:
    """
    检查环境变量是否存在，如果不存在则提示用户输入
    
    Args:
        env_name: 环境变量名称
        prompt_message: 提示用户输入的消息，如果为None则使用默认消息
        as_secret_str: 是否使用 SecretStr 作为返回值
        
    Returns:
        环境变量的值或用户输入的值，根据 as_secret_str 参数返回 SecretStr 或 str 类型
    """
    # 检查环境变量是否存在
    env_value = os.environ.get(env_name)
    
    # 如果环境变量不存在，提示用户输入
    if not env_value:
        if prompt_message is None:
            prompt_message = f"缺少环境变量 {env_name} 的值，请手动输入"
        
        env_value = getpass.getpass(prompt_message)
        
        os.environ[env_name] = env_value
    
    if as_secret_str:
        return SecretStr(env_value)
    
    return env_value