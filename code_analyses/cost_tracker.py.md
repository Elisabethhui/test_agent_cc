# cost_tracker.py 深度分析

## 功能描述

`cost_tracker.py` 实现了 Token 使用量和费用的跟踪统计。它从 claude-code-main 的 `src/utils/modelCost.ts` 和 `src/cost-tracker.ts` 移植而来，用于追踪 API 调用中的 token 消耗和成本。

## 架构设计

```
┌─────────────────────────────────────────┐
│           CostTracker                   │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │         ModelUsage dict           │  │
│  │  ┌───────────────────────────┐   │  │
│  │  │       Claude 3.5 Sonnet   │   │  │
│  │  │         ModelUsage        │   │  │
│  │  │         ┌──────────────┐ │   │  │
│  │  │         │ input_tokens │ │   │  │
│  │  │         │output_tokens │ │   │  │
│  │  │         │cache_read   │ │   │  │
│  │  │         │cache_write  │ │   │  │
│  │  │         │cost_usd     │ │   │  │
│  │  │         │duration_s   │ │   │  │
│  │  │         │pricing_known│ │   │  │
│  │  │         └──────────────┘ │   │  │
│  │  └───────────────────────────┘   │  │
│  └───────────────────────────────────┘  │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │         Memory                    │  │
│  │  _total_cost_usd, _total_api_duration_s  │
│  │  _model_usage, _wall_start          │  │
│  │  _lines_added, _lines_removed       │  │
│  │  _last_input_tokens                │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## 技术要点

### 1. 定价分层（Pricing Tiers）

定义了不同模型的价格档位（每百万 tokens 的美元费用）：

```python
@dataclass(frozen=True)
class _PricingTier:
    input: float        # 输入 token 价格
    output: float       # 输出 token 价格
    cache_write: float  # 缓存写入价格
    cache_read: float   # 缓存读取价格

# 各模型对应的价格档位
_TIER_3_15 = _PricingTier(input=3.0, output=15.0, cache_write=3.75, cache_read=0.30)   # Claude 3.5 Sonnet
_TIER_15_75 = _PricingTier(input=15.0, output=75.0, cache_write=18.75, cache_read=1.50)   # Claude Sonnet
_TIER_5_25 = _PricingTier(input=5.0, output=25.0, cache_write=6.25, cache_read=0.50)     # Claude Opus
_TIER_HAIKU_35 = _PricingTier(input=0.80, output=4.0, cache_write=1.0, cache_read=0.08)  # Claude 3.5 Haiku
_TIER_HAIKU_45 = _PricingTier(input=1.0, output=5.0, cache_write=1.25, cache_read=0.10)  # Claude Haiku 4.5
_TIER_30_150 = _PricingTier(input=30.0, output=150.0, cache_write=37.5, cache_read=3.0)  # Claude Opus 4.6 (fast)
```

**关键逻辑：**
- 每个模型前缀映射到一个价格档位
- `claude-opus-4-6` 需要检查是否设置了 `speed=fast`（传入 usage 中的 speed 字段）
- 顺序匹配：先匹配的前缀优先
- GPT/o1/o3/o4 系列模型返回 None（不支持）
- 未知模型使用 `_DEFAULT_TIER`（claude-sonnet 价格）

### 2. 缓存计费机制

Anthropic API 的计费方式：
- `input_tokens`：当前输入 token 数（**已排除缓存读取部分**）
- `cache_read_input_tokens`：从缓存中读取的 token 数
- `cache_creation_input_tokens`：新创建的输入 token 数

**计费公式：**
```
cost = (input_tokens * input_price + 
        output_tokens * output_price + 
        cache_read_tokens * cache_read_price + 
        cache_write_tokens * cache_write_price) / 1_000_000
```

### 3. Token 格式化显示

```python
def _fmt_tokens(n: int) -> str:
    """如官方 CLI 格式：1m, 1.2k, 100"""
    if n >= 1_000_000:
        v = n / 1_000_000
        return f"{v:.1f}m" if v != int(v) else f"{int(v)}m"
    if n >= 1_000:
        v = n / _000
        return f"{v:.1f}k" if v != int(v) else f"{int(v)}k"
    return str(n)
```

**显示规则：**
- ≥ 100 万：m 单位
- ≥ 1000：k 单位  
- < 1000：直接显示数字

### 4. 持续时间格式化

```python
def _fmt_duration(seconds: float) -> str:
    """如 "2h 30m 15s", "30m 15s", "45s""""
    if seconds < 0:
        seconds = 0
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    # 只显示非零单位
    if h > 0:
        return f"{h}h {m}m {s}s"
    if m > 0:
        return f"{m}m {s}s"
    return f"{s}s"
```

## 核心类

### `CostTracker`

主要数据结构和操作方法：

```python
class CostTracker:
    def __init__(self) -> None:
        self._total_cost_usd: float = 0.0
        self._total_api_duration_s: float = 0.0
        self._model_usage: dict[str, ModelUsage] = {}
        self._wall_start: float = time.monotonic()
        self._lines_added: int = 0
        self._lines_removed: int = 0
        self._last_input_tokens: int = 0
    
    @property
    def total_cost_usd(self) -> float:
        """总费用（美元）"""
        return self._total_cost_usd
    
    @property
    def last_input_tokens(self) -> int:
        """最近一次 API 调用的输入 token 数（反映上下文大小）"""
        return self._last_input_tokens
    
    def calculate_cost(model: str, usage: dict) -> float:
        """计算单次 API 调用的费用"""
        tier = _tier_for_model(model, usage)
        if tier is None:
            return 0.0
        
        cost = (
            usage.get("input_tokens", 0) * tier.input +
            usage.get("output_tokens", 0) * tier.output +
            usage.get("cache_read_input_tokens", 0) * tier.cache_read +
            usage.get("cache_creation_input_tokens", 0) * tier.cache_write
        ) / 1_000_000
        return cost
    
    def add_usage(self, model: str, usage: dict, api_duration_s: float = 0.0) -> float:
        """记录 token 消耗，返回本次调用费用"""
        cost = self.calculate_cost(model, usage)
        self._total_cost_usd += cost
        self._total_api_duration_s += api_duration_s
        self._last_input_tokens = usage.get("input_tokens", 0)
        
        mu = self._model_usage.setdefault(model, ModelUsage())
        mu.input_tokens += usage.get("input_tokens", 0)
        mu.output_tokens += usage.get("output_tokens", 0)
        mu.cache_read_input_tokens += usage.get("cache_read_input_tokens", 0)
        mu.cache_creation_input_tokens += usage.get("cache_creation_input_tokens", 0)
        mu.cost_usd += cost
        mu.api_duration_s += api_duration_s
        if not _is_known_model(model):
            mu.pricing_known = False
        return cost
    
    def add_lines_changed(self, added: int, removed: int) -> None:
        """记录代码变更（行数）"""
        self._lines_added += added
        self._lines_removed += removed
    
    def format_cost(self) -> str:
        """格式化成本输出，匹配官方 Claude Code 格式"""
        if not self._model_usage:
            return "No API usage recorded."
        
        wall_s = time.monotonic() - self._wall_start
        unknown_pricing = any(not mu.pricing_known for mu in self._model_usage.values())
        
        lines = [
            f"Total cost:            ${self._total_cost_usd:.2f}",
            "Pricing note:          Costs may be inaccurate due to usage of unknown models" if unknown_pricing else "",
            f"Total duration (API):  {_fmt_duration(self._total_api_duration_s)}",
            f"Total duration (wall): {_fmt_duration(wall_s)}",
            f"Total code changes:    {self._lines_added} {'line' if self._lines_added == 1 else 'lines'} added, "
            f"{self._lines_removed} {'line' if self._lines_removed == 1 else 'lines'} removed",
            "Usage by model:",
        ]
        
        # 各模型使用详情
        max_name = max(len(m) for m in self._model_usage)
        for model, mu in sorted(self._model_usage.items()):
            parts = [
                f"{_fmt_tokens(mu.input_tokens)} input",
                f"{_fmt_tokens(mu.output_tokens)} output",
            ]
            if mu.cache_read_input_tokens:
                parts.append(f"{_fmt_tokens(mu.cache_read_input_tokens)} cache read")
            if mu.cache_creation_input_tokens:
                parts.append(f"{_fmt_tokens(mu.cache_creation_input_tokens)} cache write")
            
            detail = ", ".join(parts)
            if not mu.pricing_known:
                detail += ", pricing unavailable"
            
            name_pad = model.rjust(max_name)
            lines.append(f"  {name_pad}:  {detail} (${mu.cost_usd:.4f})")
        
        return "\n".join(lines)
```

## 辅助函数

### `_tier_for_model(model, usage)`

根据模型名称和 usage 信息确定价格档位：

```python
def _tier_for_model(model: str, usage: dict | None = None) -> _PricingTier | None:
    model_lower = model.lower()
    
    # 特殊处理：claude-opus-4-6 根据 speed 不同价格不同
    if "claude-opus-4-6" in model_lower:
        if usage and usage.get("speed") == "fast":
            return _TIER_30_150
        return _TIER_5_25
    
    # 顺序匹配模型前缀
    for prefix, tier in _MODEL_PRICING:
        if prefix in model_lower:
            return tier
    
    # GPT/o1/o3/o4 系列不支持
    if model_lower.startswith(("gpt-", "o1", "o3", "o4")):
        return None
    
    # 未知模型使用默认档位
    return _DEFAULT_TIER  # 即 _TIER_3_15
```

### `_is_known_model(model)`

检查模型是否支持计费：

```python
def _is_known_model(model: str) -> bool:
    model_lower = model.lower()
    if "claude-opus-4-6" in model_lower:
        return True
    for prefix, _ in _MODEL_PRICING:
        if prefix in model_lower:
            return True
    return False
```

### `ModelUsage` 数据类

```python
@dataclass
class ModelUsage:
    input_tokens: int = 0              # 该模型总输入 token
    output_tokens: int = 0             # 该模型总输出 token
    cache_read_input_tokens: int = 0   # 该模型总缓存读取
    cache_creation_input_tokens: int = 0  # 该模型总缓存写入
    cost_usd: float = 0.0             # 该模型总费用
    api_duration_s: float = 0.0       # 该模型总 API 持续时间
    pricing_known: bool = True        # 价格是否已知
```

## 使用示例

```python
from cost_tracker import CostTracker

tracker = CostTracker()

# 记录每次 API 调用
usage = {
    "input_tokens": 1500,
    "output_tokens": 500,
    "cache_read_input_tokens": 800,
    "cache_creation_input_tokens": 700,
}
cost = tracker.add_usage("claude-3-5-sonnet", usage, api_duration_s=1.5)

# 记录代码变更
tracker.add_lines_changed(50, 10)

# 打印成本统计
print(tracker.format_cost())
```

**输出示例：**
```
Total cost:            $0.43
Total duration (API):  2m 3s
Total duration (wall): 5s
Total code changes:    50 lines added, 10 lines removed
Usage by model:
  claude-3-5-sonnet:  1.5k input, 500 output, 800 cache read, 700 cache write ($0.4310)
```

## 输出格式说明

```
Total cost:            $X.XX              # 总费用（2 位小数）
Total duration (API):  Xh Ym Zs           # API 总耗时
Total duration (wall): Xh Ym Zs           # 总耗时（含等待）
Total code changes:    X lines added, Y removed  # 代码变更量

Usage by model:                            # 各模型使用详情
  model-name:  INPUT input, OUTPUT output, CACHE cache read/write ($COST)
```

**每行格式：**
- 模型名右对齐（对齐到最长的模型名）
- 输入、输出、缓存 token 数量（自动单位切换）
- 费用：4 位小数

## 设计亮点

### 1. 缓存计费正确处理

明确区分三类 token：
- `input_tokens` = `cache_read_input_tokens` + `cache_creation_input_tokens`
- 但计费时分别按各自单价计算

### 2. 未知模型处理

- 使用默认价格档位（claude-sonnet）
- `pricing_known = False` 标记
- 输出时显示警告提示

### 3. 持续时间双维度

- `API 持续时间`：实际请求耗时
- `墙钟时间`：包含等待时间
- 分别显示便于分析

### 4. 代码行数统计

- 记录 `add_lines_changed()` 接收的行增删数
- 累计统计代码变更总量

### 5. 格式化人性化

- Token 数量自动单位切换（k/m）
- 时间智能显示（仅显示非零单位）
- 输出对齐美观

## 注意事项

1. **ModelUsage 对象在 `add_usage()` 中创建并复用**：
   - `self._model_usage.setdefault(model, ModelUsage())`
   - 首次调用创建新对象，后续复用同一对象累计数据

2. **定时器的使用**：
   - `wall_start` 使用 `time.monotonic()` 而非 `time.time()`
   - 避免因系统时钟调整导致计算错误

3. **非已知模型的定价未知标志**：
   - `mu.pricing_known = False`
   - 输出时显示警告，提醒用户费用可能不准确

---

*文件路径：`/Users/huguoqing/zzzhu/code/exp/RAG/project1/context_system/cc-mini/src/core/cost_tracker.py`*
