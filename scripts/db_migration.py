#!/usr/bin/env python
"""
数据库迁移脚本 - 应用 Neo4j label 和 constrains

此脚本从 neomodel 配置中获取数据库 URL，并执行 neomodel_install_labels 命令
来安装数据库模式中定义的 label 和 constrains。
"""

from dotenv import load_dotenv
load_dotenv()

import os
import sys
import subprocess
from db import config

def run_migration():
    """执行数据库迁移"""
    # 获取当前数据库 URL
    db_url = config.DATABASE_URL
    
    if not db_url:
        print("错误: 未找到数据库 URL。请确保 neomodel 配置正确。")
        sys.exit(1)
    
    # 构建命令
    schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              "db", "schema.py")
    
    if not os.path.exists(schema_path):
        print(f"错误: 未找到模式文件: {schema_path}")
        sys.exit(1)
    
    # 构建并执行命令
    cmd = ["neomodel_install_labels", schema_path, "--db", db_url]
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("迁移成功完成!")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"迁移失败: {e}")
        print(e.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_migration() 