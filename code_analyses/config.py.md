# config.py Analysis

## 文件概述
`config.py` 负责应用配置的加载与解析，支持从 TOML 文件、环境变量、命令行参数多个来源读取配置，并遵循「命令行 > 环境变量 > 文件配置」的优先级顺序。

## 核心类

### AppConfig
```python
@dataclass(frozen=True)
class AppConfig:
    provider: str                 # LLM 提供商（anthropic/openai）
    api_key: str | None
    base_url: str | None
    model: str                    # 模型名称
    max_tokens: int
    effort: str | None            # effort level (low/medium/high)
    buddy_model: str | None       # Companion 模型
    memory_dir: Path              # 记忆存储目录
    dream_interval_hours: float   # Dream 整合间隔（小时）
    dream_min_sessions: int       # Dream 触发最少年限数
    auto_dream: bool              # 是否自动触发 dream
    config_paths: tuple[Path, ...]
```

## 关键配置项

### 模型别名映射
```python
_MODEL_ALIASES = {
    "sonnet": "claude-sonnet-4-6",
    "opus": "claude-opus-4-6",
    "haiku": "claude-haiku-4-5-20251001",
    # ... 更多别名
}
```

### 模型最大 token 限制
```python
_MODEL_MAX_TOKENS = (
    ("claude-opus-4-6", 64000),
    ("claude-sonnet-4-6", 32000),
    ("claude-3-5-sonnet", 8192),
    # ... 更多模型限制
)
```

### 环境变量名
```python
_ENV_MODEL = "CC_MINI_MODEL"
_ENV_MAX_TOKENS = "CC_MINI_MAX_TOKENS"
_ENV_MEMORY_DIR = "CC_MINI_MEMORY_DIR"
_ENV_PROVIDER = "CC_MINI_PROVIDER"
_ENV_EFFORT = "CC_MINI_EFFORT"
_ENV_BUDDY_MODEL = "CC_MINI_BUDDY_MODEL"
```

## 主要函数

### resolve_model
```python
def resolve_model(model: str | None, provider: str = DEFAULT_PROVIDER) -> str:
    """解析模型名称，支持别名转换（Anthropic 提供商）。"""
```

### default_max_tokens_for_model
```python
def default_max_tokens_for_model(
    model: str | None,
    provider: str = DEFAULT_PROVIDER,
) -> int:
    """根据模型名称返回默认最大 token 限制。"""
```

### load_app_config
```python
def load_app_config(args: Namespace) -> AppConfig:
    """从文件、环境变量、命令行参数加载应用配置。
    
    优先级：命令行 > 环境变量 > 文件配置
    """
```

## 配置加载流程

### load_app_config 执行步骤

1. **加载文件配置** (`_load_file_values`)
   - 首先读取显式指定的配置文件路径
   - 若无指定，按顺序尝试默认配置路径：
     - `~/.config/cc-mini/config.toml`
     - `./.cc-mini.toml`
   - 支持合并多个配置文件（后者覆盖前者）

2. **加载环境变量** (`_load_env_values`)
   - 读取所有相关的 CC_MINI_* 环境变量
   - 对于 OpenAI 提供读取 `OPENAI_API_KEY`、`OPENAI_BASE_URL`
   - 对于 Anthropic 读取 `ANTHROPIC_API_KEY`、`ANTHROPIC_BASE_URL`

3. **合并配置值**
   - 定义优先级：命令行参数 > 环境变量 > 文件配置
   - 计算 provider：按 key 存在性判断（openai 优先，若无则 anthropic）

4. **构建 AppConfig 对象**
   - 按优先级顺序应用各来源的配置值

## 辅助函数

### _load_file_values
```python
def _load_file_values(explicit_path: str | None) -> tuple[dict, tuple[Path, ...]]:
    """加载配置文件值，支持多文件合并。"""
```

### _read_config_file
```python
def _read_config_file(path: Path) -> dict:
    """读取单个 TOML 配置文件。"""
```

### _merge_file_values
```python
def _merge_file_values(target: dict, incoming: dict) -> None:
    """合并配置值（浅合并，providers 下 deep merge）。"""
```

### _infer_provider
```python
def _infer_provider(provider_values: dict) -> str:
    """若两种 provider 都配置，则优先使用 openai。"""
```

### _parse_max_tokens / _parse_effort
```python
def _parse_max_tokens(raw_value: Any, default: int) -> int:
    """解析 max_tokens，支持整数或保留默认值。"""

def _parse_effort(raw_value: Any) -> str | None:
    """解析 effort level（low/medium/high）。"""
```

## TOML 配置文件结构

```toml
[anthropic]          # Anthropic 提供商配置
    api_key = "..."
    base_url = "..."
    model = "sonnet"
    max_tokens = 32000
    effort = "medium"

[openai]             # OpenAI 提供商配置
    api_key = "..."
    base_url = "..."
    model = "gpt-4"
    max_tokens = 16384

# 顶层配置（可选）
provider = "anthropic"
memory_dir = "~/.mini-claude/memories"
dream_interval_hours = 24
```

## 使用场景

1. **项目启动**：通过 `--config` 参数指定配置路径
2. **用户自定义**：编辑 `~/.config/cc-mini/config.toml`
3. **命令行覆盖**：启动时通过参数临时覆盖配置
4. **环境变量覆盖**：环境变量优先级最高

## 依赖模块
- `argparse` - Namespace 用于解析命令行参数
- `dataclasses` - AppConfig 定义
- `dotenv` - 加载环境变量
- `tomllib` / `tomli` - TOML 解析（Python 3.11+ 用 tomllib）
- `llm` - 模型名称解析和默认 token 限制

## 注意事项
1. **配置优先级**：命令行 > 环境变量 > 文件配置
2. **Provider 推断**：若两种都配置，优先使用 openai
3. **配置路径**：支持配置路径继承（先读上层，后读下层）
4. **错误处理**：文件不存在或 TOML 格式错误会抛出 ValueError
