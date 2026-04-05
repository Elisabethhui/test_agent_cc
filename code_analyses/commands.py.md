# commands.py Analysis

## 文件概述
`commands.py` 实现了斜杠命令（slash command）的解析与分发系统，参照 `claude-code` 的 `src/commands.ts` 实现。

## 核心结构

### 1. CommandContext（命令上下文）
```python
@dataclass
class CommandContext:
    engine: Engine              # 引擎实例
    session_store: SessionStore | None  # 会话存储
    compact_service: CompactService  # 压缩服务
    console: Console           # 输出控制台
    app_config: AppConfig      # 应用配置
    memory_dir: Path | None = None  # 记忆目录
    permissions: PermissionChecker | None = None
    run_dream: object = None   # Dream 功能
    cost_tracker: CostTracker | None = None
    new_session_store: object = None
    reconfigure_mode: object = None
    plan_manager: object = None
    pending_query: str | None = None  # 后续模型查询
```

### 2. 命令解析函数
```python
def parse_command(text: str) -> tuple[str, str] | None:
    """如果 *text* 以 ``/`` 开头，返回 ``(command_name, args)``，否则返回 None。"""
```

### 3. 命令处理函数
实现了 13 个内置命令：

| 命令 | 功能 |
|------|------|
| `/help` | 显示可用命令列表 |
| `/compact` | 压缩对话上下文 |
| `/resume` | 恢复历史会话 |
| `/history` | 列出当前目录的历史会话 |
| `/clear` | 清空对话，开始新会话 |
| `/memory` | 显示当前记忆索引 |
| `/remember` | 保存笔记到每日日志 |
| `/dream` | 将每日日志整合为主题文件 |
| `/skills` | 列出所有可用技能 |
| `/cost` | 显示 token 使用量和费用摘要 |
| `/model` | 显示或切换模型（支持交互式选择器） |
| `/plan` | 进入计划模式或显示当前计划 |

### 4. 命令分发与技能执行

#### handle_command
```python
def handle_command(name: str, args: str, ctx: CommandContext) -> bool:
    """分发斜杠命令。如果名称不匹配内置命令，则检查技能注册表。"""
```

#### _execute_skill
```python
def _execute_skill(skill, args: str, ctx: CommandContext) -> bool:
    """执行技能 —— inline（内联）或 forked（分叉）。

    - Inline: 将技能提示注入当前对话
    - Forked: 在隔离的轮次中运行技能，结果不持久化
    """
```

## 实现细节

### /compact 命令
- 检查消息数量（至少 4 条）
- 调用 `CompactService.compact()` 压缩消息
- 持久化压缩后的会话状态

### /resume 命令
- 支持按索引编号（0 起始）或 session-id 前缀恢复会话
- 检查会话模式兼容性并显示警告

### /clear 命令
- 清空消息并创建新会话

### /memory 命令
- 从记忆目录加载记忆索引

### /remember 命令
- 将文本追加到每日日志

### /dream 命令
- 调用 `run_dream` 整合每日日志

### /skills 命令
- 列出所有可用技能及其提示和来源

### /cost 命令
- 显示费用追踪器统计

### /model 命令
- 交互式模型选择器（支持方向键、数字键、鼠标选择）
- 支持 effort level 选择
- 兼容 Anthropic 和不同 provider 的模型名称映射

## 设计特点

1. **命令注册表模式**：通过 `_COMMAND_TABLE` 统一管理所有命令
2. **内联与分叉执行**：技能可根据 `context` 参数决定执行方式
3. **上下文对象化**：所有命令共享 `CommandContext` 对象
4. **交互式选择器**：基于 `prompt_toolkit` 实现

## 依赖模块
- `coordinator` - 会话模式管理
- `compact` - 消息压缩服务
- `session` - 会话存储
- `memory` - 记忆系统
- `skills` - 技能注册表
- `cost_tracker` - 费用追踪
- `config` - 配置管理
- `plan` - 计划模式管理
- `main` - 查询执行
