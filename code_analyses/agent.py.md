# agent.py 深度分析

## 功能描述

`agent.py` 实现了 **Agent**（子代理）工具以及与工作器（Worker）相关的工具类：
- **AgentTool**: 用于启动背景工作器进行调研、实现或验证
- **SendMessageTool**: 续写已返回工作器的任务
- **TaskStopTool**: 停止运行的工作器

这是 **多线程/多代理协作系统** 的核心，允许主代理异步执行任务。

## 架构设计

```
┌──────────────────────────────────────────────────┐
│                    Agent System                  │
│                                                  │
│  ┌─────────────┐         ┌──────────────┐       │
│  │ AgentTool   │─────►   │ WorkerManager │       │
│  │             │  spawn() │              │       │
│  │             │         │              │       │
│  │             │◄─────   │ Worker        │       │
│  │             │  get    │  (Threaded)   │       │
│  │ (main)       │ activity│  (background)│       │
│  └─────────────┘  desc()  └──────────────┘       │
│                                                  │
│  ┌─────────────┐         ┌──────────────┐       │
│  │ SendMessage │─────►   │ WorkerManager │       │
│  │ Tool        │  continue│              │       │
│  │             │         │              │       │
│  │             │◄─────   │ Worker        │       │
│  └─────────────┘  task()  (responds)         │       │
│                                                  │
│  ┌─────────────┐         ┌──────────────┐       │
│  │ TaskStop    │─────►   │ WorkerManager │       │
│  │ Tool        │  stop()  │              │       │
│  │             │         │              │       │
│  │             │◄─────   │ Worker        │       │
│  └─────────────┘  task()  (terminates)     │       │
└──────────────────────────────────────────────────┘
```

## 技术要点

### 1. 工具基础类继承

所有工具都继承自 `Tool` 基类：

```python
from .base import Tool, ToolResult

class AgentTool(Tool):
    name = "Agent"
    description = "Spawn a background worker..."
```

### 2. WorkerManager 集成

所有 Agent 工具都依赖 `WorkerManager` 进行实际的任务管理：

```python
def __init__(self, manager: WorkerManager):
    self._manager = manager
```

### 3. 异步任务模式

- **立即返回**: 启动任务时只返回 `task_id` 和初始 payload
- **后台执行**: Worker 在独立线程中运行
- **结果异步**: 完成结果通过 `task_notification` 消息返回

## 核心逻辑

### 1. AgentTool - 启动子代理

```python
class AgentTool(Tool):
    name = "Agent"
    description = (
        "Spawn a background worker for research, implementation, or "
        "verification. Returns immediately with a task_id. Final results "
        "arrive later as a <task-notification> user message."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "description": {"type": "string", "description": "Short label for the worker task"},
            "prompt": {"type": "string", "description": "Self-contained instructions for the worker"},
            "subagent_type": {
                "type": "string",
                "enum": ["worker"],
                "default": "worker",
                "description": "Only 'worker' is currently supported",
            },
        },
        "required": ["description", "prompt"],
    }

    def get_activity_description(self, **kwargs) -> str | None:
        desc = kwargs.get("description", "")
        return f"Running agent: {desc}" if desc else "Running agent…"
```

**关键方法：`execute()`**

```python
def execute(
    self,
    description: str,
    prompt: str,
    subagent_type: str = "worker",
) -> ToolResult:
    try:
        # 向 WorkerManager 请求创建任务，获取 task_id 和初始 payload
        payload = self._manager.spawn(
            description=description,
            prompt=prompt,
            subagent_type=subagent_type,
        )
    except ValueError as exc:
        return ToolResult(content=f"Error: {exc}", is_error=True)
    
    # 返回 JSON 格式的结果（task_id 在 JSON 中）
    return ToolResult(content=json.dumps(payload, ensure_ascii=False))
```

**执行流程：**
1. 接收 `description` 和 `prompt` 两个必需参数
2. 调用 `WorkerManager.spawn()` 启动 Worker
3. 捕获可能的参数错误（`ValueError`）
4. 返回包含 `task_id` 的 JSON 响应

### 2. SendMessageTool - 续写任务

```python
class SendMessageTool(Tool):
    name = "SendMessage"
    description = (
        "Continue an existing idle worker by task_id. Use this after a worker "
        "has already reported back and you want it to take another step."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "to": {"type": "string", "description": "Worker task id to continue"},
            "message": {"type": "string", "description": "Next self-contained instruction"},
        },
        "required": ["to", "message"],
    }

    def __init__(self, manager: WorkerManager):
        self._manager = manager

    def execute(self, to: str, message: str) -> ToolResult:
        try:
            payload = self._manager.continue_task(task_id=to, message=message)
        except ValueError as exc:
            return ToolResult(content=f"Error: {exc}", is_error=True)
        return ToolResult(content=json.dumps(payload, ensure_ascii=False))
```

**使用场景：** Worker 已经完成当前步骤返回，主代理决定让它继续执行下一步。

**执行流程：**
1. 通过 `task_id` 查找对应的 Worker
2. 调用 `WorkerManager.continue_task()` 注入新指令
3. Worker 收到消息后会继续执行

### 3. TaskStopTool - 停止任务

```python
class TaskStopTool(Tool):
    name = "TaskStop"
    description = "Stop a running worker by task_id."
    input_schema = {
        "type": "object",
        "properties": {
            "task_id": {"type": "string", "description": "Worker task id"},
        },
        "required": ["task_id"],
    }

    def __init__(self, manager: WorkerManager):
        self._manager = manager

    def execute(self, task_id: str) -> ToolResult:
        try:
            payload = self._manager.stop_task(task_id=task_id)
        except ValueError as exc:
            return ToolResult(content=f"Error: {exc}", is_error=True)
        return ToolResult(content=json.dumps(payload, ensure_ascii=False))
```

**使用场景：**
- 任务已执行很久，不再需要继续
- 检测到错误，需要终止并获取中间结果
- 内存/资源限制

## 关键函数

| 类 | 方法 | 作用 |
|----|------|------|
| AgentTool | `execute(description, prompt, subagent_type)` | 启动新的 Worker 任务 |
| AgentTool | `get_activity_description()` | 返回 Agent 活动的描述（用于状态显示） |
| SendMessageTool | `execute(to, message)` | 给指定 task_id 的 Worker 发送新消息 |
| TaskStopTool | `execute(task_id)` | 停止指定的 Worker |

## WorkerManager 接口

虽然 WorkerManager 在这个文件中被使用，但它实际定义在 `worker_manager.py`。从使用方式可以看出它的核心接口：

```python
# 创建任务
payload = manager.spawn(description="...", prompt="...", subagent_type="worker")

# 续写任务
payload = manager.continue_task(task_id="...", message="...")

# 停止任务
payload = manager.stop_task(task_id="...")
```

返回的 `payload` 是一个字典（JSON），包含：
- `task_id`: 任务的唯一标识
- 其他元数据和状态信息

## 使用示例

### 启动一个调研任务

```python
from tools.agent import AgentTool
from worker_manager import WorkerManager

manager = WorkerManager()
agent_tool = AgentTool(manager)

# 启动任务
result = agent_tool.execute(
    description="Research pandas DataFrame",
    prompt="""Write a comprehensive guide on pandas DataFrame operations.
Include:
1. Creating DataFrames
2. Data manipulation
3. Export to CSV
4. Common pitfalls"""
)

task_id = json.loads(result.content)["task_id"]
```

### 等待结果（在其他地方处理）

```python
# 主线程继续处理其他事情
for event in engine.submit(user_input):
    if listener.check_esc():
        break
    ...

# 监听 task_notification 消息
if message.content.startswith("<task-notification>"):
    import json
    task_data = json.loads(message.content)
    if task_data["task_id"] == task_id:
        print(f"Task complete: {task_data['result']}")
```

### 中途给 Worker 发指令

```python
# 任务已经返回，让 Worker 继续
result = send_message_tool.execute(
    to=task_id,
    message="Now show an example with sample data"
)
```

### 停止一个卡住的 Worker

```python
result = task_stop_tool.execute(task_id=task_id)
```

## 设计亮点

### 1. 异步协作架构

```
主代理 (Main Agent)      Worker (线程)
     │                     │
     │  spawn() ─────►      │
     │  (immediate)        │
     │                     │
     ◄─────────────────────┘
     │  task_notification  │ (异步返回结果)
     └─────────────────────┘
```

主代理 **立即返回**，Worker **异步执行**，结果 **异步返回**。

### 2. 工具组合模式

三个工具形成一个完整的生命周期管理：

```
Agent     → 启动 Worker
Send      → 续写 Worker
Stop      → 终止 Worker
```

### 3. 错误处理

```python
try:
    payload = self._manager.spawn(...)
except ValueError as exc:
    return ToolResult(content=f"Error: {exc}", is_error=True)
```

清晰区分任务执行错误和 API 调用错误。

### 4. 自包含指令

```python
prompt: {"description": "...", "prompt": "..."}
# prompt 必须是"self-contained instructions"
# Worker 不需要知道上下文，独立可执行
```

## 技术要点总结

| 技术点 | 说明 |
|--------|------|
| **多代理协作** | 主代理负责决策，Worker 负责执行 |
| **异步执行** | 任务在后台线程运行 |
| **任务追踪** | 通过 task_id 追踪和管理任务 |
| **JSON 通信** | 工具与 Worker 之间通过 JSON 交换数据 |
| **即时反馈** | 启动任务后立即返回 task_id |
| **异步结果** | 结果通过 task_notification 消息异步返回 |

## 使用场景

1. **长耗时任务**: 不需要立即等待结果时可以启动
2. **多任务并行**: 可以同时进行多个独立任务
3. **代码生成**: Worker 专注生成代码片段
4. **代码验证**: Worker 专注验证代码正确性
5. **调研收集**: Worker 专注信息搜集和整理

## 与前端交互

前端通过接收 `task_notification` 消息向用户展示结果：

```python
# 伪代码示例
if message.is_user and message.content.startswith("<task-notification>"):
    task_data = json.loads(message.content)
    task_id = task_data["task_id"]
    
    # 更新 UI 显示
    show_task_result(task_id, task_data["result"])
```

---

*文件路径：`/Users/huguoqing/zzzhu/code/exp/RAG/project1/context_system/cc-mini/src/core/tools/agent.py`*
