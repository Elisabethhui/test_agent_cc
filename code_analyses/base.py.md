# Tool 基类与结果

## 文件路径

`cc-mini/src/core/tools/base.py`

## 内容

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ToolResult:
    """工具执行结果"""
    content: str          # 返回内容
    is_error: bool = False # 是否错误


class Tool(ABC):
    """工具基类（抽象）"""
    
    @property
    @abstractmethod
    def name(self) -> str: ...
    
    @property
    @abstractmethod
    def description(self) -> str: ...
    
    @property
    @abstractmethod
    def input_schema(self) -> dict: ...
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult: ...
    
    def get_activity_description(self, **kwargs) -> str | None:
        """返回工具执行时的活动描述（显示在 spinner 中）"""
        return None
    
    def is_read_only(self) -> bool:
        """是否只读工具（不修改文件）"""
        return False
    
    def to_api_schema(self) -> dict:
        """转换为 API Schema 格式（用于前端显示）"""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }
```

## 核心概念

### ToolResult

```python
@dataclass
class ToolResult:
    content: str          # 返回内容
    is_error: bool = False # 是否错误
```

- **content**: 工具返回的字符串内容
- **is_error**: 标记是否为错误状态

**使用示例**：

```python
# 正常返回
ToolResult(content="操作成功", is_error=False)

# 错误返回
ToolResult(content="Error: something went wrong", is_error=True)
```

### Tool（抽象基类）

所有工具类必须继承 `Tool` 并实现以下属性：

#### 1. name

```python
@property
def name(self) -> str:
    """工具名称，用于 API 调用"""
    return "ToolName"
```

#### 2. description

```python
@property
def description(self) -> str:
    """工具描述，向用户展示功能"""
    return "Do something useful."
```

#### 3. input_schema

```python
@property
def input_schema(self) -> dict:
    """输入参数 Schema（OpenAPI 格式）"""
    return {
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "参数说明"},
            "param2": {
                "type": "integer",
                "default": 10,
                "description": "参数说明"
            }
        },
        "required": ["param1"]  # 必填参数
    }
```

#### 4. execute

```python
def execute(self, **kwargs) -> ToolResult:
    """核心执行方法"""
    # 解析参数
    param1 = kwargs.get("param1", "default")
    param2 = kwargs.get("param2", 10)
    
    # 执行逻辑
    
    # 返回结果
    return ToolResult(content="结果内容", is_error=False)
```

## 完整工具示例

```python
class FileReadTool(Tool):
    name = "FileRead"
    description = "Read the contents of a file."
    input_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "File path to read"}
        },
        "required": ["path"]
    }
    
    def is_read_only(self) -> bool:
        return True  # 只读操作
    
    def execute(self, path: str) -> ToolResult:
        from tools.file_read import read_file
        content = read_file(path)
        return ToolResult(content=content)
```

## 方法详解

### get_activity_description(**kwargs) → str | None

返回执行时的活动描述，显示在终端 spinner 中。

```python
def get_activity_description(self, **kwargs) -> str | None:
    return f"Reading file: {path}"
```

### is_read_only() → bool

判断工具是否为只读操作：

```python
def is_read_only(self) -> bool:
    return True  # 不修改任何文件，可以安全运行
```

### to_api_schema() → dict

转换为前端 API Schema 格式：

```python
def to_api_schema(self) -> dict:
    return {
        "name": self.name,
        "description": self.description,
        "input_schema": self.input_schema,
    }
```

## 使用流程

```
模型生成工具调用
    ↓
验证参数
    ↓
执行工具.execute(**args)
    ↓
返回 ToolResult
    ↓
序列化为 JSON 添加到消息队列
    ↓
下次对话时反序列化继续
```

## 注意事项

1. **name 要唯一**：避免工具名冲突
2. **description 要清晰**：方便模型理解
3. **input_schema 要准确**：参数类型、描述、必填项
4. **execute 要健壮**：处理参数缺失、文件不存在等错误
5. **content 要完整**：包含所有必要信息
6. **错误要设置 is_error=True**：方便下游判断
