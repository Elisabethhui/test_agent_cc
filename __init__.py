#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Context System 核心上下文管理包
包含：会话压缩、安全切割、记忆管理、结构化总结等核心模块
"""

__version__ = "1.0.0"
__author__ = "Auto Generated"

# 导出核心模块（方便外部导入使用）
from .compact_system import CompactSystem
from .grouping import safe_grouping
from .session_memory import SessionMemory
