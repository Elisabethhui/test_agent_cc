# tools/file_tool.py
import os

def file_read(path: str) -> str:
    """读取指定路径文件的内容"""
    if not os.path.exists(path):
        return "错误：找不到该文件。"
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"读取异常：{str(e)}"

def file_write(path: str, content: str) -> str:
    """将内容写入指定文件（注意：Agent 只在具有权限时调用）"""
    try:
        # 自动创建不存在的父目录
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"成功写入：{path}"
    except Exception as e:
        return f"写入异常：{str(e)}"