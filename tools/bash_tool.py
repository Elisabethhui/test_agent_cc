# tools/bash_tool.py
import subprocess

def run_bash(command: str) -> str:
    """执行本地 Bash 命令并捕获输出内容"""
    try:
        # 设置超时时间防止挂死
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return result.stdout
        return f"错误 (代码 {result.returncode}):\n{result.stderr}"
    except Exception as e:
        return f"系统级执行失败: {str(e)}"