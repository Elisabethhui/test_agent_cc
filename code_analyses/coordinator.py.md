# coordinator.py 深度分析

## 功能描述

`coordinator.py` 实现了协调器（Coordinator）模式的核心逻辑，用于管理多 worker 并发的任务调度。它定义了一套完整的协调器/worker 双模式系统，包括环境配置、会话管理、系统提示词生成等。

## 架构设计

```
┌─────────────────────────────────────────────────────────────────┐
│                    Coord 系统架构                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────┐              ┌─────────────────────┐ │
│  │   Coordinator Mode  │              │   Normal Mode       │ │
│  │                     │              │                     │ │
│  │  (coordinator.py)   │              │   (engine.py)       │ │
│  │                    │              │                     │ │
│  └─────────┬───────────┘              └─────────┬───────────┘ │
│           │                                    │              │
│  ┌────────┴────────┐                         ┌───────┐       │
│  │ Coordinator     │                         │ User  │       │
│  │ - manage workers │────────────────────────▶│   |    │       │
│  │ - synthesize prompts       │     direct msg     │   |       │
│  │ - route to workers                    │     │    │       │
│  └────────┬────────┘                         └───────┘       │
│           │                                              │     │
│  ┌────────┴────────┐        ┌──────────────────────────────┐ │
│  │   Worker Pool   │        │  User/Coordinator Context    │ │
│  │   (multiple)    │        │  (shared between turns)      │ │
│  │  - Agent       │────────▶│                              │ │
│  │  - SendMessage │◀────────│   Worker contexts preserved  │ │
│  │  - TaskStop    │        │   on resume                  │ │
│  └────────────────┘        └──────────────────────────────┘ │
│                       (session-based context)                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 环境配置

### `COORDINATOR_ENV_VAR`

```python
COORDINATOR_ENV_VAR = "CC_MINI_COORDINATOR"
```

通过环境变量 `CC_MINI_COORDINATOR` 控制是否启用协调器模式。

### `_is_env_truthy(value)`

判断环境变量是否为"真"：

```python
def _is_env_truthy(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() not in {"", "0", "false", "no", "off"}
```

**判断规则：**
- `None` → False
- 非空且不是禁用词 → True
- 禁用词：`""`, `"0"`, `"false"`, `"no"`, `"off"`（不区分大小写）

### `is_coordinator_mode()`

```python
def is_coordinator_mode() -> bool:
    return _is_env_truthy(os.getenv(COORDINATOR_ENV_VAR))
```

检查当前是否处于协调器模式。

### `set_coordinator_mode(enabled: bool)`

```python
def set_coordinator_mode(enabled: bool) -> None:
    if enabled:
        os.environ[COORDINATOR_ENV_VAR] = "1"
    else:
        os.environ.pop(COORDINATOR_ENV_VAR, None)
```

设置协调器模式：
- `enabled=True`：设置环境变量为 `"1"`
- `enabled=False`：从环境中删除该变量

### `current_session_mode()`

获取当前会话模式：

```python
def current_session_mode() -> str:
    return "coordinator" if is_coordinator_mode() else "normal"
```

## 会话模式管理

### `match_session_mode(session_mode: str | None) -> str | None`

匹配当前会话与目标会话的模式，可能需要切换模式：

```python
def match_session_mode(session_mode: str | None) -> str | None:
    if session_mode not in {"coordinator", "normal"}:
        return None  # 无效模式
    
    current = current_session_mode()
    if current == session_mode:
        return None  # 模式已匹配，无需切换
    
    # 切换模式
    set_coordinator_mode(session_mode == "coordinator")
    if session_mode == "coordinator":
        return "Entered coordinator mode to match resumed session."
    return "Exited coordinator mode to match resumed session."
```

**返回值说明：**
- `None`：无需切换，模式已匹配
- `"Entered coordinator mode..."`：从 normal 切换到 coordinator
- `"Exited coordinator mode..."`：从 coordinator 切换到 normal

## 核心功能

### `get_coordinator_user_context(worker_tools: Iterable[str]) -> dict[str, str]`

获取协调器在 user 角色下的 context，告知其可用的 worker 工具：

```python
def get_coordinator_user_context(worker_tools: Iterable[str]) -> dict[str, str]:
    if not is_coordinator_mode():
        return {}  # normal 模式下无此 context
    
    rendered_tools = ", ".join(sorted(set(worker_tools)))
    return {
        "workerToolsContext": (
            "Workers launched via the Agent tool run in the background and have "
            f"access to these tools: {rendered_tools}. "
            "Worker completions arrive later as <task-notification> user "
            "messages."
        )
    }
```

**关键信息：**
- 告知协调器：Worker 在后台运行，独立访问工具
- 告知协调器：Worker 的完成结果以 `<task-notification>` user message 形式异步到达

## Worker 系统提示词 (`get_coordinator_system_prompt()`)

### 核心职责

```
You are a **coordinator**. Your job is to:
- Help the user achieve their goal
- Direct workers to research, implement and verify code changes
- Synthesize results and communicate with the user
- Answer questions directly when possible — don't delegate work that you can handle without tools
```

### 可用工具

- **Agent** - 启动一个新的 worker
- **SendMessage** - 继续已有的 worker（向其 agent ID 发送后续消息）
- **TaskStop** - 停止一个正在运行的 worker

## Worker 与 Coordinator 的区别

### Coordinator

- **角色**：协调者，连接用户和 workers 的中枢
- **对话对象**：永远是对用户（user）说话
- **内部信号**：Worker 的 `<task-notification>` 是内部信号，不是对话对象
- **行动原则**：能直接回答的问题直接回答，不 delegating

### Worker

- **角色**：执行具体任务的子代理
- **对话对象**：向 coordinator 汇报
- **不可见性**：**看不到用户的对话历史**
- **任务类型**：research/implementation/verification
- **禁止事项**：不能 spawn 其他 worker

## Agent 工具使用说明

### 启动规则

```
When calling Agent:
- Do not use one worker to check on another. Workers will notify you when they are done.
- Do not use workers to trivial report file contents or run commands. Give them higher-level tasks.
- Continue workers whose work is complete via SendMessage
- After launching agents, briefly tell the user what you launched and end your response
- Never fabricate or predict agent results
```

**关键点：**
1. Worker 独立运行，互不检查
2. 不用于 trivial 任务（如读取文件、运行命令）
3. Worker 完成后用 **SendMessage** 继续（而非启动新 Worker）
4. 告诉用户已启动什么，但不预测结果

### Agent Results 格式

Worker 的完成结果作为 user-role 的 `<task-notification>` XML：

```xml
<task-notification>
<task-id>{agentId}</task-id>
<status>completed|failed|killed</status>
<summary>{human-readable status summary}</summary>
<result>{agent's final text response}</result>
<usage>
  <total_tokens>N</total_tokens>
  <tool_uses>N</tool_uses>
  <duration_ms>N</duration_ms>
</usage>
</task-notification>
```

**字段说明：**
| 字段 | 说明 |
|------|------|
| `task-id` | Worker 的唯一 ID（agentId） |
| `status` | 状态：completed/failed/killed |
| `summary` | 人类可读的状态摘要 |
| `result` | Worker 的最终文本响应（可选） |
| `usage.total_tokens` | 消耗 token 数 |
| `usage.tool_uses` | 调用工具次数 |
| `usage.duration_ms` | 执行耗时（毫秒） |

### 继续 Worker

用 `SendMessage` 继续某个 Worker：

```javascript
SendMessage({ to: "agent-a1b", message: "..." })
// to 参数指定要继续的 Worker 的 task-id
```

**示例：**

```
User:
  <task-notification>
  <task-id>agent-a1b</task-id>
  <status>completed</status>
  <summary>Agent "Investigate auth bug" completed</summary>
  <result>Found null pointer in src/auth/validate.ts:42...</result>
  </task-notification>

You:
  Found the bug — null pointer in validate.ts:42.
  Still waiting on the token storage research.

  SendMessage({ to: "agent-a1b", message: "Fix the null pointer in src/auth/validate.ts:42..." })
```

## 工作流程

### 四大阶段

| Phase | Who | Purpose |
|-------|-----|---------|
| **Research** | Workers (parallel) | 调查代码库、查找文件、理解问题 |
| **Synthesis** | **You** (coordinator) | 汇总发现、理解问题、制定实现规范 |
| **Implementation** | Workers | 按规范进行针对性修改 |
| **Verification** | Workers | 测试修改是否有效 |

### 并行性原则

```
**Parallelism is your superpower. Workers are async. Launch independent workers concurrently whenever possible — don't serialize work that can run simultaneously.**
```

**并发管理：**
| 任务类型 | 策略 |
|---------|------|
| Read-only (research) | 并行运行 |
| Write-heavy (implementation) | 每批文件串行 |
| Verification | 有时可与 implementation 并行（不同文件区域） |

## 真实验证（Real Verification）

```
Verification means **proving the code works**, not confirming it exists.
```

**验证规则：**
1. **启用新特性运行测试** - 不是简单检查"tests pass"
2. **调查类型检查错误** - 不只是看错误列表，要深入分析
3. **保持怀疑** - 如果感觉不对劲，就要深挖
4. **独立测试** - 证明修改有效，不 rubber-stamp

## Worker 失败处理

当 Worker 报告失败（测试失败、构建错误等）：

```
- Continue the same worker with SendMessage — it has the full error context
- If a correction attempt fails, try a different approach or report to the user
```

## 停止 Worker

使用 `TaskStop` 停止跑偏的 Worker：

```javascript
// 中途发现方向错误
TaskStop({ task_id: "..." })

// 用户需求变更
TaskStop({ task_id: "..." })
```

**注意：** 被停止的 Worker 后续可以用 `SendMessage` 重新启动。

## 编写 Worker Prompt 的要点

### 始终合成（Always Synthesize）

```
When workers report research findings, **you must understand them before directing follow-up work**.
```

**反例（lazy delegation）：**
```
// Bad
Agent({ prompt: "Based on your findings, fix the auth bug", ... })
Agent({ prompt: "The worker found an issue in the auth module. Please fix it.", ... })

// Good — synthesized spec
Agent({ prompt: "Fix the null pointer in src/auth/validate.ts:42. The user field on Session (src/auth/types.ts:15) is undefined when sessions expire but the token remains cached. Add a null check before user.id access — if null, return 401 with 'Session expired'. Commit and report the hash.", ... })
```

**关键原则：**
- **自己理解并综合 findings**
- 在 prompt 中明确：具体文件路径、行号、精确的修改内容
- 避免 "based on your findings" 这类 delegating 短语

### 添加目的陈述（Add Purpose Statement）

让 Worker 校准深度和侧重点：

- "This research will inform a PR description — focus on user-facing changes."
- "I need this to plan an implementation — report file paths, line numbers, and type signatures."
- "This is a quick check before we merge — just verify the happy path."

### Continue vs. Spawn 的决策

基于上下文重叠度决定：

| Situation | Mechanism | Why |
|-----------|-----------|-----|
| Research 精确探索了需要修改的文件 | **Continue** (SendMessage) | Worker 已有文件 context + 明确计划 |
| Research 广泛但 Implementation 狭窄 | **Spawn fresh** (Agent) | 避免探索噪音，保持上下文专注 |
| Correcting failure / extending recent work | **Continue** | Worker 有错误 context |
| Verifying code a different worker 刚写的 | **Spawn fresh** | Verifier 需要 fresh eyes |
| First attempt 用了完全错误的方向 | **Spawn fresh** | Wrong-approach context 污染 retry |
| 完全无关的任务 | **Spawn fresh** | 无有用 context 可复用 |

**决策要点：**
- **High overlap** → Continue
- **Low overlap** → Spawn fresh

## Worker Prompt 的 Good/Bad 示例

### Good Examples

1. **Implementation**: "Fix the null pointer in src/auth/validate.ts:42. The user field can be undefined when the session expires. Add a null check and return early with an appropriate error. Commit and report the hash."

2. **Precise git operation**: "Create a new branch from main called 'fix/session-expiry'. Cherry-pick only commit abc123 onto it. Push and create a draft PR targeting main. Report the PR URL."

3. **Correction** (continued worker, short): "The tests failed on the null check you added — validate.test.ts:58 expects 'Invalid session' but you changed it to 'Session expired'. Fix the assertion. Commit and report the hash."

### Bad Examples

1. "Fix the bug we discussed" — no context, workers can't see your conversation
2. "Based on your findings, implement the fix" — lazy delegation
3. "Create a PR for the recent changes" — ambiguous scope
4. "Something went wrong with the tests, can you look?" — no error message, no direction

## 额外提示

- Include file paths, line numbers, error messages — workers start fresh
- State what "done" looks like
- For implementation: "Run relevant tests and typecheck, then commit your changes and report the hash" — workers self-verify
- For research: "Report findings — do not modify files"
- Be precise about git operations
- When continuing for corrections: reference what the worker did
- For verification: "Prove the code works, don't just confirm it exists"
- For verification: "Try edge cases and error paths"
- For verification: "Investigate failures — don't dismiss as unrelated without evidence"

## 示例会话

```
User: "There's a null pointer in the auth module. Can you fix it?"

You:
  Let me investigate first.

  Agent({ description: "Investigate auth bug", subagent_type: "worker", prompt: "Investigate the auth module in src/auth/. Find where null pointer exceptions could occur around session handling and token validation... Report specific file paths, line numbers, and types involved. Do not modify files." })
  Agent({ description: "Research auth tests", subagent_type: "worker", prompt: "Find all test files related to src/auth/. Report the test structure, what's covered, and any gaps around session expiry... Do not modify files." })

  Investigating from two angles — I'll report back with findings.

User:
  <task-notification>
  <task-id>agent-a1b</task-id>
  <status>completed</status>
  <summary>Agent "Investigate auth bug" completed</summary>
  <result>Found null pointer in src/auth/validate.ts:42. The user field on Session is undefined when the session expires but ...</result>
  </task-notification>

You:
  Found the bug — null pointer in validate.ts:42.

  SendMessage({ to: "agent-a1b", message: "Fix the null pointer in src/auth/validate.ts:42. Add a null check before accessing user.id — if null, ... Commit and report the hash." })

  Fix is in progress.

User:
  How's it going?

You:
  Fix for the null pointer is in progress. Still waiting to hear back about the test suite.
```

## Worker System Prompt

```python
def get_worker_system_prompt() -> str:
    return """You are a worker operating under a coordinator.

- Execute the assigned task directly and autonomously.
- You do not talk to the end user; your final answer goes back to the
  coordinator.
- If the prompt says research only, do not modify files.
- If you modify code, run relevant verification before finishing.
- Report concrete file paths, commands, results, and any residual risk.
- Do not try to spawn other workers.
"""
```

## 使用示例

```python
from coordinator import (
    is_coordinator_mode,
    set_coordinator_mode,
    current_session_mode,
    match_session_mode,
    get_coordinator_system_prompt,
    get_worker_system_prompt,
)

# 1. 检查当前模式
if is_coordinator_mode():
    print("Running in coordinator mode")

# 2. 切换模式
set_coordinator_mode(True)
print(f"Current session mode: {current_session_mode()}")

# 3. 匹配会话模式（resume 时需要）
match_session_mode("coordinator")

# 4. 获取系统提示词
coord_prompt = get_coordinator_system_prompt()
worker_prompt = get_worker_system_prompt()

# 5. 与协调器对话
worker_tools = ["Bash", "Read", "Edit", "Write", "Glob", "Grep"]
user_context = get_coordinator_user_context(worker_tools)

# 对话示例
messages = [
    {"role": "user", "content": "Implement a feature..."},
    {"role": "assistant", "content": coord_prompt + user_context},
    {"role": "user", "content": worker_prompt},  # 传递给 worker
]
```

## 设计亮点

### 1. 双模式隔离

- **Coordinator Mode**：多 worker 管理，复杂任务编排
- **Normal Mode**：单轮对话，直接响应用户

通过环境变量 `CC_MINI_COORDINATOR` 控制切换，互不干扰。

### 2. Session 级别的模式保持

```python
match_session_mode(session_mode)
```

- resume 会话时自动匹配目标模式
- 避免"模式不匹配"导致的对话中断

### 3. 异步 Worker 模型

- Worker 在后台并行运行
- 完成结果异步以 user message 形式返回
- Coordinator 根据结果决定下一步

### 4. 上下文管理

- **Normal 模式**：User-Assistant 轮转对话
- **Coordinator 模式**：多轮对话 + 多 Worker 上下文
- Resume 时通过 session 状态保持上下文

### 5. 明确的任务流

Research → Synthesis → Implementation → Verification

**每个阶段都有明确的负责人（Who），避免职责混淆。**

### 6. 智能的 Continue/Spawn 决策

基于上下文重叠度动态决定：
- High overlap → Continue（复用 Worker 的 context）
- Low overlap → Spawn fresh（避免污染）

### 7. 真实验证要求

- 不是"tests pass"就 OK
- 要真正证明修改有效
- 独立测试，不依赖 Worker 之前的测试

## 注意事项

1. **Worker 不可见用户对话历史**
   - 每个 Worker 的 prompt 必须 self-contained
   - 需要具体文件路径、行号、完整上下文

2. **Worker 之间不互相检查**
   - "Workers will notify you when they are done"
   - Coordinator 负责汇总和调度

3. **避免 Lazy Delegation**
   - 不要直接转发用户的 instructions 给 Worker
   - Coordinator 必须先理解并综合

4. **Self-Verification**
   - Implementation worker 修改后必须自行验证
   - "Run relevant tests and typecheck, then commit"

5. **错误处理**
   - Continue failed worker（有完整错误 context）
   - 或回退到 user 尝试不同方案

---

*文件路径：`/Users/huguoqing/zzzhu/code/exp/RAG/project1/context_system/cc-mini/src/core/coordinator.py`*
