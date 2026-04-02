#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
summary_prompt 模块
自动生成的空文件，可根据业务逻辑实现功能
"""
SUMMARY_PROMPT = """
你是高精度智能体对话压缩器，输出结构化总结：
1. 用户核心需求
2. 关键技术
3. 文件与代码
4. 错误与修复
5. 解决过程
6. 用户关键输入
7. 待办任务
8. 当前进度
9. 下一步

禁止调用工具。
"""

def get_summary_prompt():
    return SUMMARY_PROMPT