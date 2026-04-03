# config.py
import os

# 模型配置
MODEL_NAME = "qwen2.5-7b-instruct" # 或其他本地模型
API_BASE = "http://localhost:8000/v1"
API_KEY = "w2hqq0809"

# 压缩阈值 (根据源码 apiMicrocompact.ts 映射)
MAX_CONTEXT_TOKENS = 120000  # 触发全量压缩的阈值
MICRO_COMPACT_THRESHOLD = 2000  # 单个工具结果超过此字符则物理脱水
GAP_MINUTES_THRESHOLD = 30 # 超过30分钟未互动触发自动清理

# 记忆存储路径 (Scoped Memory)
USER_CONFIG_PATH = os.path.expanduser("~/.claude/config.json")
PROJECT_CONFIG_PATH = "./.claude/memory.json"
LOCAL_STATE_PATH = "./.claude/local_state.json"

# 工具黑名单 (微压缩时优先清理这些工具的输出)
TOOLS_TO_DEHYDRATE = ["file_read", "bash", "ls", "grep"]