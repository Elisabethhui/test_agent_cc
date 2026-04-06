# Bash 工具

## 文件路径

`cc-mini/src/core/tools/bash.py`

## 依赖

- `tools.base` (`Tool`, `ToolResult`)
- `..sandbox.manager` (`SandboxManager`)
- `subprocess` 标准库

## 工具概览

`Bash` 工具用于执行 Bash 命令并返回输出。它集成了沙箱机制，可以安全地运行命令。

---

## 属性

```python
name = "Bash"

description = (
    "Executes a given bash command and returns its output.\n\n"
    "The working directory persists between commands, but shell state does not. "
    "The shell environment is initialized from the user's profile (bash or zsh).\n\n"
    "IMPORTANT: Avoid using this tool to run `find`, `grep`, `cat`, `head`, `tail`, "
    "`sed`, `awk`, or `echo` commands, unless explicitly instructed or after you have "
    "verified that a dedicated tool cannot accomplish your task.\n"
    # ... (详细使用指南)
)
```

**主要特性提醒**：

- 工作目录在命令间持久化，但 shell 状态不持久
- 推荐使用专用工具（Glob、Read、Edit、Write、AskUserQuestion）
- 使用绝对路径，避免 `cd`
- 默认超时 120 秒
- 支持并行和串行执行

## input_schema

```json
{
  "type": "object",
  "properties": {
    "command": {
      "type": "string",
      "description": "The bash command to execute"
    },
    "timeout": {
      "type": "integer",
      "description": "Timeout in seconds",
      "default": 120
    },
    "dangerously_disable_sandbox": {
      "type": "boolean",
      "description": "If true and allowed by config, run outside sandbox"
    }
  },
  "required": ["command"]
}
```

---

## 类结构

### BashTool

继承自 `Tool`，负责执行命令并返回结果。

#### get_activity_description(**kwargs) → str | None

返回命令预览用于 spinner 显示：

```python
def get_activity_description(self, **kwargs) -> str | None:
    command = kwargs.get("command", "")
    # Show a truncated version of the command
    preview = command[:60] + "…" if len(command) > 60 else command
    return f"Running {preview}" if command else None
```

#### __init__(sandbox_manager: SandboxManager | None = None)

初始化时可选绑定沙箱管理器：

```python
def __init__(self, sandbox_manager: SandboxManager | None = None):
    self._sandbox = sandbox_manager
```

#### execute(command, timeout=120, dangerously_disable_sandbox=False) → ToolResult

执行命令的核心方法：

```python
def execute(
    self,
    command: str,
    timeout: int = _DEFAULT_TIMEOUT,
    dangerously_disable_sandbox: bool = False,
) -> ToolResult:
    # Sandbox 决策
    use_sandbox = (
        self._sandbox is not None
        and self._sandbox.should_sandbox(command, dangerously_disable_sandbox)
    )
    
    # 如果有沙箱，包装命令
    actual_command = self._sandbox.wrap(command) if use_sandbox else command
    
    try:
        result = subprocess.run(
            actual_command, shell=True, capture_output=True,
            text=True, encoding="utf-8", errors="replace", timeout=timeout,
        )
        
        # 格式化输出
        parts = []
        if result.stdout:
            parts.append(result.stdout.rstrip())
        if result.stderr:
            parts.append(f"[stderr]\n{result.stderr.rstrip()}")
        if result.returncode != 0:
            parts.append(f"[exit code: {result.returncode}]")
            
        return ToolResult(content="\n".join(parts) if parts else "(no output)")
        
    except subprocess.TimeoutExpired:
        return ToolResult(content=f"Error: Command timed out after {timeout}s", is_error=True)
    except Exception as e:
        return ToolResult(content=f"Error: {e}", is_error=True)
```

---

## 执行流程

```
用户请求
    ↓
BashTool.execute(command, timeout, disable_sandbox)
    ↓
检查是否需要沙箱
    ↓
SandboxManager.should_sandbox()
    ↓
判断条件：
  - 命令在允许列表中
  - 不在排除列表中
  - 路径在允许目录中
    ↓
需要沙箱 → SandboxManager.wrap() 包装
不需要沙箱 → 直接使用原命令
    ↓
subprocess.run() 执行命令
    ↓
捕获输出 (stdout/stderr/exit code)
    ↓
格式化输出
    ↓
返回 ToolResult
```

---

## 输出格式

```
命令输出内容
[stderr]
错误信息（如果有）
[exit code: 返回码]（如果非 0）
```

**示例**：

```
# 成功
File created: /path/to/file.md

# 失败
Error: Something went wrong
[exit code: 123]
```

---

## 沙箱机制

### should_sandbox(command, disable_sandbox) → bool

判断命令是否需要在沙箱中运行：

1. 如果 `disable_sandbox=True` 且配置允许，则不沙箱
2. 否则调用允许/排除规则判断

### wrap(command) → str

沙箱化命令，添加 `bwrap` 参数：

```python
def wrap(self, command: str) -> str:
    """包装命令，添加 bwrap 参数"""
    # 使用 bubblewrap 创建隔离环境
    # 添加 --dev --bind /path 等参数
    # 返回类似：bwrap --dev --bind /host/path /sandbox/path -- command
```

---

## 使用沙箱的条件

### 必须沙箱（自动）

```python
# 涉及文件操作
git checkout, git commit, git push
touch, rm, mv, cat

# 网络请求
curl, wget, httpie

# 进程操作
pkill, kill, killall

# 目录创建
mkdir, rm -rf
```

### 不需要沙箱（手动）

```python
# 只读文件操作
grep, head, tail, cat
find, ls

# 文本处理
sed, awk, tr

# 纯终端操作
echo, printf, clear, top, htop

# 但是需要先通过专用工具验证
# 例如先 Glob 查找文件，确认存在再用 cat 读取
```

---

## 注意事项

1. **始终优先使用专用工具**：
   - Glob → Glob
   - Read → Read
   - Write → Write
   - Edit → Edit
   - Grep → Grep

2. **路径必须存在且正确**：
   ```python
   # ✅ 使用绝对路径
   bash -c "cat /Users/huguoqing/zzzhu/code/..."
   
   # ❌ 使用相对路径（可能出错）
   bash -c "cat config.py"
   ```

3. **空格必须加引号**：
   ```bash
   # ✅ 正确
   bash -c "cp 'file name with spaces.md' ."
   
   # ❌ 错误（会分解成多个参数）
   bash -c "cp file name with spaces.md ."
   ```

4. **超时控制**：
   - 默认 120 秒
   - 长时间运行任务可适当延长
   - 避免无限循环

5. **错误处理**：
   - 返回码非 0 会输出 `[exit code: N]`
   - `TimeoutExpired` 返回超时错误
   - 其他异常返回 `Error: {msg}`

---

## 并行执行

可以同时调用多个 `Bash` 工具：

```json
{
  "actions": [
    {
      "tool": "Bash",
      "args": {"command": "command1", "timeout": 30}
    },
    {
      "tool": "Bash",
      "args": {"command": "command2", "timeout": 30}
    }
  ]
}
```

两个命令会并行执行，互不等待。

---

## 与专用工具的关系

| 操作 | 推荐工具 | Bash 用途 |
|------|----------|----------|
| 文件搜索 | Glob | 仅作验证 |
| 内容搜索 | Grep | 仅作验证 |
| 读取文件 | Read | 仅作验证 |
| 写入文件 | Write | 仅作验证 |
| 编辑文件 | Edit | 仅作验证 |
| 用户输入 | AskUserQuestion | 仅作验证 |
| **系统操作** | Bash | **实际执行** |

---

## 输出状态码

| 返回码 | 含义 |
|-------|------|
| 0 | 成功 |
| 1 | 一般错误 |
| 128 | 进程未找到 |
| 127 | 命令未找到 |
| 126 | 命令被拒绝执行 |
| 123 | 权限不足 |
| 255 | 未知错误 |

---

## 常见用法

### 目录导航（用绝对路径）

```bash
ls /Users/huguoqing/zzzhu/code/exp/RAG/project1/context_system/cc-mini/src/core/
```

### 查看文件（用专用工具）

❌ 不要：
```bash
cat config.py
```

✅ 应该：
```python
# 先用工具查看
Read: file_path="config.py"
```

### 文件编辑（用专用工具）

❌ 不要：
```bash
sed -i 's/old/new/' config.py
```

✅ 应该：
```python
# 先用工具编辑
Edit: file_path="config.py", old_string="old", new_string="new"
```

### 获取命令帮助

```bash
bash -c "command --help"
```

### 创建临时文件

```bash
bash -c "mktemp && cat /tmp/tmp.XXXXXX"
```

---

## 安全建议

1. **不要运行可疑命令**：总是检查来源
2. **不要删除重要文件**：先用 `ls` 确认
3. **小心递归操作**：`rm -rf`, `rm -R *`
4. **小心网络命令**：`curl`/`wget` 可能下载恶意内容
5. **注意环境变量**：`env`, `export` 可能修改环境
