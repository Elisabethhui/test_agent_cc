#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
post_clean 模块
自动生成的空文件，可根据业务逻辑实现功能
"""
from micro_compact import CACHE_STATE

class AppState:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.cache = {}
            cls._instance.permissions = set()
            cls._instance.system_prompt = {}
        return cls._instance

APP_STATE = AppState()

def post_compact_cleanup(is_main_thread: bool = True):
    CACHE_STATE.pending_edits.clear()
    CACHE_STATE.pinned.clear()

    if is_main_thread:
        APP_STATE.cache.clear()
        APP_STATE.permissions.clear()
        APP_STATE.system_prompt.clear()

    print("✅ 压缩后清理完成（单例安全）")