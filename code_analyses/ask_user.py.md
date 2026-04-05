# ask_user.py 深度分析

## 功能描述

`ask_user.py` 实现了交互式用户提问工具 `AskUserQuestionTool`，用于向用户显示 **多选项菜单**（单选或多选）并收集回答。

这是 **直接人机交互** 的核心组件，允许 AI Agent 主动向用户提问以澄清需求、获取偏好或做决策。

## 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                  AskUserQuestionTool                     │
│                                                         │
│  ┌─────────────────────────────────────────┐            │
│  │       Interactive Menu (prompt_toolkit) │            │
│  │                                         │            │
│  │  Q1: What do you want to do?            │            │
│  │  (1) Option A                          │            │
│  │  (2) Option B                          │            │
│  │  (5) Other: [your answer]             │            │
│  │  ↑↓ navigate · 1-4 select             │            │            │
│  │                                         │            │
│  │  Q2: Which frameworks?                │            │
│  │  (1) Django            (4) FastAPI     │            │
│  │  (2) Flask             (5) Other       │            │
│  │  (1) (2)  or  (3)        or  Other:   │            │
│  │        ✗ ✗               [grails]     │            │
│  │  ↑↓ navigate · space toggle · ↵ confirm           │            │
│  │                                         │            │
│  └─────────────────────────────────────────┘            │
│                                   ┌─────────┐         │
│                                   │   Tool  │         │
│                                   │  Execute│         │
│                                   └─────────┘         │
└─────────────────────────────────────────────────────────┘
```

## 技术要点

### 1. prompt_toolkit 驱动

使用 `prompt_toolkit` 构建交互式终端菜单：

```python
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl
```

### 2. 单选与多选分离

```python
# 单选菜单
def _select_one(question, labels, descriptions) -> str | None

# 多选菜单
def _select_multi(question, labels, descriptions) -> list[str] | None
```

### 3. "Other" 选项

每个问题都自动添加 **第 5 个选项 "Other"**：
- 单选时：Inline 文本输入（直接跟在选项旁）
- 多选时：独立的文本缓冲区

### 4. 智能按键处理

**箭头键**: 总是导航（即使在 Other 输入时也有效）

**数字键**: 
- 在非 Other 选项：直接选择该选项
- 在 Other 选项：聚焦 Other

**Enter**: 
- 在非 Other 选项：直接选择
- 在 Other 选项：提交输入

**Space**:
- 单选时：无作用
- 多选时：切换复选框

**Escape/Ctrl-C**: 取消整个提问

**Backspace**: 
- 在非 Other：删除文字
- 在 Other: 删除最后一个字符

## 核心逻辑

### 数据结构

```python
# 输入格式（从 AskUserQuestionTool.execute() 传入）
questions: list[dict] = [
    {
        "question": "What do you want to do?",
        "options": [
            {"label": "Option A", "description": "Description 1"},
            {"label": "Option B", "description": "Description 2"},
        ],
        "multiSelect": False
    },
    {
        "question": "Which frameworks?",
        "options": [
            {"label": "Django", "description": "Description 1"},
            {"label": "Flask", "description": "Description 2"},
            {"label": "FastAPI", "description": "Description 3"},
        ],
        "multiSelect": True
    }
]
```

处理流程：
```
questions → [
    Q1 (single) → labels = [A, B, "Other"],
    Q2 (multi) → labels = [D, F, FA, "Other"]
] → render menus → collect answers
```

### 1. 单选菜单 `_select_one()`

```python
def _select_one(question: str, labels: list[str], descriptions: list[str]) -> str | None:
    """箭头键导航的单选菜单"""
```

**状态管理：**
```python
other_idx = len(labels) - 1  # "Other" 的索引
cursor = [0]  # 当前选中的选项（0-based）
text_buf: list[str] = [""]  # Other 的文本缓冲区
result: list[str] = []  # 收集的结果（用于捕获已选择的选项）
```

**事件处理：**

#### 上下箭头 - 导航

```python
@kb.add("up")
def _up(event):
    # 循环导航
    cursor[0] = (cursor[0] - 1) % len(labels)

@kb.add("down")
def _down(event):
    cursor[0] = (cursor[0] + 1) % len(labels)
```

无论当前是否在 Other 输入状态，箭头键始终有效。

#### Enter - 确认选择

```python
@kb.add("enter")
def _enter(event):
    if _on_other():  # 当前在 Other 选项
        if text_buf[0]:
            result.append(text_buf[0])  # 提交输入的文本
        else:
            result.append(_OTHER)  # 空 Other = 取消
    else:  # 在非 Other 选项
        result.append(labels[cursor[0]])  # 提交已选选项
    event.app.exit()
```

#### Esc - 取消

```python
@kb.add("escape")
def _esc(event):
    if _on_other() and text_buf[0]:
        # 在 Other 且有输入：清空输入并回到上一个选项
        text_buf[0] = ""
        cursor[0] = max(other_idx - 1, 0)
    else:
        # 取消整个菜单
        event.app.exit()
```

**巧妙设计**: 如果只在 Other 有输入就按 Esc，保留输入并回到上一个选项，给用户修改机会。

#### Backspace - 删除字符

```python
@kb.add("backspace")
def _bs(event):
    if _on_other():
        text_buf[0] = text_buf[0][:-1]  # 删除最后一个字符
```

只在 Other 模式下响应 backspace。

#### 任意字符 - 智能处理

```python
@kb.add("<any>")
def _char(event):
    ch = event.data
    if not ch or not ch.isprintable():
        return  # 控制键交给其他处理器
    
    if _on_other():
        text_buf[0] += ch  # 在 Other 中：输入文本
    else:
        # 在非 Other 中：数字键选择，其他字符跳转到 Other
        if ch.isdigit():
            idx = int(ch) - 1  # 1->0, 2->1, ...
            if 0 <= idx < len(labels):
                if idx == other_idx:
                    cursor[0] = other_idx  # 聚焦 Other
                else:
                    result.append(labels[idx])  # 选择该选项
        else:
            cursor[0] = other_idx  # 跳转到 Other
            text_buf[0] += ch  # 输入文本
```

这是**最关键的设计**，实现了无缝切换。

### 2. 多选菜单 `_select_multi()`

```python
def _select_multi(question: str, labels: list[str], descriptions: list[str]) -> list[str] | None:
    """多选菜单，支持复选框"""
```

**状态管理：**
```python
other_idx = len(labels) - 1
cursor = [0]           # 当前光标位置
checked: set[int] = set()  # 已选择的选项索引
text_buf: list[str] = [""]   # Other 的文本缓冲区
confirmed = [False]        # 是否已确认提交
```

**事件处理：**

#### 上下箭头 - 导航

```python
@kb.add("up")
def _up(event):
    cursor[0] = (cursor[0] - 1) % len(labels)

@kb.add("down")
def _down(event):
    cursor[0] = (cursor[0] + 1) % len(labels)
```

#### Space - 切换复选框

```python
@kb.add("space")
def _toggle(event):
    if _on_other():
        # 在 Other：输入空格到文本缓冲区
        text_buf[0] += " "
        checked.add(other_idx)
        return
    idx = cursor[0]
    if idx in checked:
        checked.discard(idx)
    else:
        checked.add(idx)
```

#### Enter - 确认并提交

```python
@kb.add("enter")
def _confirm(event):
    confirmed[0] = True  # 标记为已确认
    event.app.exit()
```

#### Esc - 取消

```python
@kb.add("escape")
def _esc(event):
    if _on_other() and text_buf[0]:
        text_buf[0] = ""  # 清空 Other 输入
        checked.discard(other_idx)  # 取消 Other
        cursor[0] = max(other_idx - 1, 0)  # 回到上一个选项
    else:
        event.app.exit()
```

#### 任意字符

```python
@kb.add("<any>")
def _char(event):
    ch = event.data
    if not ch or not ch.isprintable():
        return
    
    if _on_other():
        text_buf[0] += ch  # 输入文本
        checked.add(other_idx)  # 自动选中 Other
    else:
        if ch.isdigit():
            # 数字键聚焦到该选项
            idx = int(ch) - 1
            cursor[0] = idx
        else:
            # 非数字键跳转到 Other
            cursor[0] = other_idx
            text_buf[0] += ch
```

#### Backspace - 智能删除

```python
@kb.add("backspace")
def _bs(event):
    if _on_other():
        text_buf[0] = text_buf[0][:-1]
        if not text_buf[0]:
            checked.discard(other_idx)  # 清空后取消 Other
```

### 3. 渲染逻辑 `_get_tokens()`

使用 `prompt_toolkit` 的 `FormattedTextControl` 动态生成终端 UI。

**渲染格式：**

```
? {question}\n
  ❯ (0) {label} — {description}    # 当前选项，高亮
    (1) {label} — {description}
    (2) {label} — {description}
    (5) [✗] {number}) {label}      # Other 选项，显示当前输入
        Type something.
  ↑↓ navigate · space toggle · ↵ confirm
```

**样式处理：**
- `ansibrightcyan`: 高亮显示当前选项
- `ansibrightgreen bold`: 高亮的 Other 输入
- `ansigray`: 辅助文本

### 4. `AskUserQuestionTool` - 整合类

```python
class AskUserQuestionTool(Tool):
    @property
    def name(self) -> str:
        return "AskUserQuestion"

    @property
    def description(self) -> str:
        return (
            "Ask the user a question with predefined options. Use this to gather "
            "preferences, clarify ambiguous instructions, or get decisions on "
            "implementation choices. Each question has 2-4 options plus an automatic "
            "'Other' option for free-form input."
        )

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "questions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string"},
                            "options": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "label": {"type": "string"},
                                        "description": {"type": "string"},
                                    },
                                    "required": ["label", "description"],
                                },
                                "minItems": 2,
                                "maxItems": 4,
                            },
                            "multiSelect": {"type": "boolean", "default": False},
                        },
                        "required": ["question", "options"],
                    },
                    "minItems": 1,
                    "maxItems": 4,
                }
            },
            "required": ["questions"],
        }

    def is_read_only(self) -> bool:
        return True  # 必须等待用户交互

    def execute(self, **kwargs) -> ToolResult:
        questions = kwargs.get("questions", [])
        if not questions:
            return ToolResult(content="No questions provided.", is_error=True)

        answers: list[str] = []

        for q in questions:
            question_text = q.get("question", "")
            options = q.get("options", [])
            multi = q.get("multiSelect", False)

            labels = [o["label"] for o in options] + ["Other"]
            descs = [o.get("description", "") for o in options] + [""]

            if multi:
                selected = _select_multi(question_text, labels, descs)
                if selected is None:
                    return ToolResult(content="User cancelled the question.", is_error=True)
                answer = ", ".join(selected) if selected else "(no selection)"
            else:
                chosen = _select_one(question_text, labels, descs)
                if chosen is None:
                    return ToolResult(content="User cancelled the question.", is_error=True)
                answer = chosen

            answers.append(f"{question_text} => {answer}")

        result_text = "User answered:\n" + "\n".join(answers)
        return ToolResult(content=result_text)
```

**执行流程：**

```
1. 验证 questions 不为空
2. 遍历每个问题：
   - 构建 labels/descriptions（+ "Other"）
   - 如果是多选，调用_select_multi()
   - 如果是单选，调用_select_one()
   - 如果有用户取消，立即返回错误
   - 收集答案
3. 返回所有答案的汇总
```

## 关键函数

| 函数 | 作用 | 返回 |
|------|------|------|
| `_select_one()` | 渲染并处理单选菜单 | `str \| None` - 选中的标签或 None（取消） |
| `_select_multi()` | 渲染并处理多选菜单 | `list[str] \| None` - 选中的标签列表或 None |
| `AskUserQuestionTool.execute()` | 执行用户提问（多个问题） | `ToolResult` - 包含所有答案 |

## 使用示例

### 单选择题

```python
from ask_user import AskUserQuestionTool

question = {
    "question": "Which programming language to use?",
    "options": [
        {"label": "Python", "description": "Great for AI"},
        {"label": "JavaScript", "description": "Good for web"},
    ],
    "multiSelect": False
}

tool = AskUserQuestionTool()
result = tool.execute(questions=[question])

print(result.content)
# 输出：
# User answered:
# Which programming language to use? => Python
```

### 多选择题

```python
question = {
    "question": "Select frameworks",
    "options": [
        {"label": "Django", "description": "Full-featured"},
        {"label": "Flask", "description": "Lightweight"},
        {"label": "FastAPI", "description": "Async-first"},
    ],
    "multiSelect": True
}

result = tool.execute(questions=[question])

print(result.content)
# 输出：
# User answered:
# Select frameworks => Django, FastAPI
```

### 混合问题

```python
questions = [
    {
        "question": "Approach?",
        "options": [
            {"label": "Full implementation"},
            {"label": "MVP first"},
        ],
        "multiSelect": False
    },
    {
        "question": "Additional features?",
        "options": [
            {"label": "Authentication"},
            {"label": "Database"},
            {"label": "Testing"},
        ],
        "multiSelect": True
    }
]

result = tool.execute(questions=questions)
# 输出所有问题的答案汇总
```

## 动画/渲染效果

```
🤔 Which programming language?

  ❯ (1) Python
     — Great for AI
    (2) JavaScript
     — Good for web
    (5) Other: Py
       Write code here...
  ↑↓ navigate · ↵ select
```

当用户移动到 Other 并开始输入时：

```
    (1) Python
    (2) JavaScript
    (5) [Py] Other: Py
                      █
  ↑↓ navigate · ↵ select
```

## 设计亮点

### 1. "Other" 选项的设计

**解决的核心问题**: 用户经常有预定义选项以外的想法。

**实现方案**:
- 作为第 N+1 个选项始终存在
- 不是独立的 prompt，而是 **inline text input**
- 导航和输入无缝切换

### 2. 按键优化

| 按键 | 在非 Other | 在 Other |
|------|-----------|---------|
| 上下箭头 | 导航 | **仍然导航**（神奇！） |
| 数字 | 直接选择 | 聚焦 Other |
| 其他字母 | 跳转到 Other | 输入文本 |
| Space | 无作用 | 输入空格/切换 |
| Enter | 确认选择 | 提交 Other |
| Esc | 取消 | 清空并返回上一个 |

**用户体验：**
- 箭头键始终可用（可随时调整选择）
- 数字快速选择
- 输入 Other 时仍然能按箭头导航
- 随时可以 Esc 退出

### 3. Backspace 智能处理

- 在普通选项：删除文字（如果有在输入）
- 在 Other：删除文字，如果清空则取消 Other

### 4. 多种输入方式

```
(1) Python          ← 数字键选择
   Python           ← Enter 选择
   Type "Python"    ← 输入文字后 Enter
(1) (2)             ← 多选：同时选多个
[1] (2)            ← 多选：输入并确认
   Other: Pytho     ← 输入 Other
```

## 使用场景

1. **需求澄清**
```python
questions = [{
    "question": "How to handle errors?",
    "options": [
        {"label": "Silent ignore"},
        {"label": "Log and continue"},
        {"label": "Throw exception"},
    ],
    "multiSelect": False
}]
```

2. **技术选型**
```python
questions = [{
    "question": "Choose stack:",
    "options": [
        {"label": "Python", "description": "Great for AI"},
        {"label": "Rust", "description": "Fast and safe"},
        {"label": "Go", "description": "Simple and fast"},
    ],
    "multiSelect": True
}]
```

3. **参数确认**
```python
questions = [{
    "question": "Model temperature?",
    "options": [
        {"label": "0.1", "description": "More deterministic"},
        {"label": "0.7", "description": "More creative"},
    ],
    "multiSelect": False
}]
```

## 技术要点总结

| 技术点 | 说明 |
|--------|------|
| **prompt_toolkit** | 构建交互式终端 UI |
| **KeyBindings** | 自定义键盘事件处理 |
| **Layout** | 动态布局（标题、选项、提示） |
| **FormattedTextControl** | 渲染文本内容 |
| **State machine** | 管理光标和输入状态 |
| **Inline Other** | 第 N+1 个选项是文本输入 |

## 与纯数字交互的对比

**传统方案**（仅数字选项）：
```
请选择：1. 功能 A  2. 功能 B
```

**问题**：
- 用户想选"功能 C"怎么办？需要说"3"，系统不知道
- 用户体验差，没有灵活性

**本方案**：
```
请选择：
  ❯ (1) 功能 A
    (2) 功能 B
    (5) Other: [待输入]
  ↑↓导航 · 1-2 选择 · Enter 确认
```

**优势**：
- ✅ 预定义选项快速选择（数字键）
- ✅ 自定义选项自由输入
- ✅ 导航始终流畅（箭头键）
- ✅ 随时可修改（箭头 + Backspace）

---

*文件路径：`/Users/huguoqing/zzzhu/code/exp/RAG/project1/context_system/cc-mini/src/core/tools/ask_user.py`*
