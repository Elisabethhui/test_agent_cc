# AskUserQuestion 工具

## 功能概述

`AskUserQuestion` 是一个交互式问答工具，用于让模型向用户提问并收集选择式答案。该工具基于 `prompt_toolkit` 实现终端 UI，支持：

- 单选题（single-select）
- 多选题（multi-select）
- "Other"（其他）选项：内联文本输入

## 文件路径

`cc-mini/src/core/tools/ask_user.py`

## 核心类

### AskUserQuestionTool

继承自 `Tool` 基类，提供交互式提问功能。

#### 属性

- **name**: `"AskUserQuestion"`
- **description**: 描述工具的用途，说明用于收集用户偏好、澄清模糊指令等，每个问题有 2-4 个选项加上自动的 "Other" 选项
- **input_schema**: 输入参数 Schema

#### input_schema 结构

```json
{
  "type": "object",
  "properties": {
    "questions": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["question", "options"],
        "properties": {
          "question": {"type": "string"},
          "options": {
            "type": "array",
            "minItems": 2,
            "maxItems": 4,
            "items": {
              "type": "object",
              "required": ["label", "description"],
              "properties": {
                "label": {"type": "string"},
                "description": {"type": "string"}
              }
            }
          },
          "multiSelect": {"type": "boolean", "default": false}
        }
      }
    }
  },
  "required": ["questions"]
}
```

#### 方法

- **is_read_only()**: 返回 `True`（不修改文件）
- **execute(**kwargs)**: 执行问答，返回 `ToolResult`

## 内部函数

### _select_one(question, labels, descriptions)

单选择题的交互式菜单实现。

- 使用 `prompt_toolkit` 创建终端应用
- 最后一个选项永远是 "Other"（内联文本输入）
- 支持上下箭头键导航
- 支持在 "Other" 选项时直接输入文本

### _select_multi(question, labels, descriptions)

选择题的交互式菜单实现。

- 与 `_select_one` 类似，但支持空格勾选/取消
- 支持快捷键操作

## 交互逻辑

### 单选题 (_select_one)

| 操作 | 行为 |
|------|------|
| ↑↓ | 导航选项（即使在 Other 输入时） |
| 数字键 | 选中的是普通选项→直接选择；选中的是 Other→聚焦 Other |
| Enter | 选中普通选项；Other 带文本→提交文本；Other 无文本→取消 |
| Esc | 有文本→清除文本并上移；无文本→取消 |
| Backspace | 在 Other 中删除字符 |

### 多选题 (_select_multi)

| 操作 | 行为 |
|------|------|
| ↑↓ | 导航选项（即使在 Other 输入时） |
| Space | 勾选/取消当前选项；在 Other 中→输入空格 |
| Enter | 确认选择 |
| Esc | 有文本→清除文本并上移；无文本→取消 |
| Backspace | 在 Other 中删除字符，为空时取消 Other |
| 数字键 | 聚焦对应选项 |
| 其他字符 | 聚焦 Other 并输入 |

## execute() 执行流程

1. 获取问题列表 `questions`
2. 如果为空，返回错误：`"No questions provided."`
3. 对每个问题：
   - 获取问题文本、选项列表、是否为多选
   - 构建 labels 列表（原选项 + "Other"）
   - 构建 descs 列表（原选项描述 + 空字符串）
   - 如果是多选，调用 `_select_multi()`，否则调用 `_select_one()`
   - 如果用户取消，返回错误：`"User cancelled the question."`
   - 格式化答案
4. 合并所有答案，返回结果

## 结果格式

```
User answered:
问题 1 => 答案 1
问题 2 => 答案 2
...
```

- 单选：`"选项名"` 或 `"用户输入文本"`
- 多选：`"选项 1, 选项 2, ... (用户输入文本)"`

## 依赖

- `prompt_toolkit`（用于终端 UI）
- 来自 `tools/base.py` 的 `Tool` 和 `ToolResult`

## 特性

1. **兼容官方行为**：
   - Other 是内联文本输入，不是独立问题
   - 箭头键始终可用
   - 数字键智能处理

2. **交互式 UI**：
   - 高亮当前选项（ansibrightcyan）
   - Other 选项显示文本输入区域（ansibrightgreen）
   - 灰色提示区域（ansigray）

3. **用户体验**：
   - 支持快速选择（数字键）
   - 支持导航 + 输入混合操作
   - 清晰的取消机制（Esc 或 Ctrl-C）
