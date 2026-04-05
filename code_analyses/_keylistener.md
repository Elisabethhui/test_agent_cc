# _keylistener.py 深度分析

## 功能描述

`_keylistener.py` 实现了一个后台线程监听器，用于在原始终端模式下监听 **ESC 键** 的按下事件。当检测到 ESC 时，会触发取消回调，立即中止当前的 HTTP 流。

## 架构设计

```
┌─────────────────────────────────────────┐
│           EscListener (Context Manager) │
│                                         │
│  ┌─────────────┐  ┌──────────────────┐ │
│  │   pressed   │  │    _stop Event   │ │
│  └─────────────┘  └──────────────────┘ │
│  ┌─────────────┐  ┌──────────────────┐ │
│  │   _paused   │  │    _thread       │ │
│  └─────────────┘  └──────────────────┘ │
│  │    _fd      │                         │
│  └─────────────┘                        │
│                                         │
│              ┌─────────────────┐        │
│              │      _listen()  │◄───────┘
│              │ (Daemon Thread) │        │
│              └─────────────────┘        │
│                                         │
│             ┌─────────────────┐        │
│             │   check_esc()   │◄───────┐
│             └─────────────────┘        │
│                                        │
│              ┌─────────────────┐       │
│              │  on_cancel()    │───────┼── 触发取消
│              └─────────────────┘       │
└─────────────────────────────────────────┘
```

## 技术要点

### 1. 跨平台实现

- **Unix/Linux/macOS**: 使用 `termios` 和 `tty` 模块进入 cbreak 模式
- **Windows**: 使用 `msvcrt` 模块替代

```python
try:
    import termios
    import tty
    _HAS_TERMIOS = True
except ImportError:
    _HAS_TERMIOS = False
```

### 2. 原始文件描述符读取

使用 `os.read()` 直接读取原始 fd，避免 Python 标准输入的缓冲区问题（与 `select()` 配合时避免 IO 缓冲区不匹配）。

```python
self._fd = sys.stdin.fileno()
```

### 3. 非阻塞 ESC 检测

使用 `select.select()` 实现非阻塞读取，配合短超时避免死锁：

```python
if self._paused.is_set():
    continue
b = os.read(self._fd, 1)
if b == b'\x1b':
    # 区分裸 ESC 和 escape 序列
```

## 核心逻辑

### 1. `__enter__()` - 进入监听状态

```python
def __enter__(self):
    self.pressed = False
    self._stop.clear()
    self._paused.clear()
    
    # 保存并修改终端设置
    self._old_settings = termios.tcgetattr(self._fd)
    tty.setcbreak(self._fd)  # 进入 cbreak 模式
    
    # 启动后台监听线程
    self._thread = threading.Thread(target=self._listen, daemon=True)
    self._thread.start()
```

**关键技术：**
- `tty.setcbreak()`: 让终端进入 cbreak 模式，按键立即生效（无需回车）
- 保存原始设置，退出时恢复

### 2. `__exit__()` - 退出监听状态

```python
def __exit__(self, *_exc):
    self._stop.set()
    if self._thread is not None:
        self._thread.join(timeout=0.5)  # 等待线程退出
    # 恢复终端设置
    if self._old_settings is not None:
        termios.tcsetattr(self._fd, termios.TCSADRAIN, self._old_settings)
```

### 3. `check_esc_nonblocking()` - 主线程检查

```python
def check_esc_nonblocking(self) -> bool:
    if self.pressed:
        return True
    
    # 非阻塞读取
    while self._has_data(0):
        b = os.read(self._fd, 1)
        if b == b'\x1b':
            # 检查是否立即有后续字节
            if self._has_data(0.05):
                self._drain()  # drain escape 序列
                continue
            self.pressed = True  # 裸 ESC
            if self._on_cancel:
                self._on_cancel()
            return True
```

**设计巧妙之处：**
- 区分布尔 ESC 键 (`\x1b`) 和 escape 序列（如 `\x1b[A` 方向键）
- escape 序列以 `\x1b` 开头但紧跟其他字节，需要 drain

### 4. `_listen()` - 后台监听线程

```python
def _listen(self):
    while not self._stop.is_set():
        if self._paused.is_set():
            self._stop.wait(0.05)  # 暂停时短暂休眠
            continue
        
        if not self._has_data(0.05):
            continue  # 没有数据
        
        b = self._read_byte()  # 读取单个字节
        
        if b == b'\x1b':
            # 区分裸 ESC 和 escape 序列
            if self._has_data(0.05):
                self._drain()
                continue  # 是 escape 序列，忽略
            self.pressed = True
            if self._on_cancel:
                self._on_cancel()
            return  # 触发取消
```

### 5. `_drain()` - 消耗 escape 序列

```python
def _drain(self):
    """将 escape 序列后的剩余字节一次性读取完"""
    while self._has_data(0.01):
        os.read(self._fd, 64)  # 每次读 64 字节
```

## 关键函数

| 函数 | 作用 |
|------|------|
| `__enter__()` | 初始化监听器，进入 cbreak 模式，启动线程 |
| `__exit__()` | 停止监听，恢复终端设置 |
| `pause()` | 暂停线程，让主线程的 stdin 可用 |
| `resume()` | 恢复线程监听 |
| `check_esc_nonblocking()` | 主线程非阻塞检查 ESC，返回是否按下 |
| `_listen()` | 后台线程循环读取，检测裸 ESC |
| `_read_byte()` | 从 fd 读取单个字节 |
| `_has_data(timeout)` | 检查 fd 是否有数据可用 |
| `_drain()` | 读取 escape 序列的剩余字节 |

## Windows 实现差异

```python
# Windows 版使用 msvcrt 模块
def check_esc_nonblocking(self) -> bool:
    if self.pressed:
        return True
    while msvcrt.kbhit():  # 阻塞式检查
        if msvcrt.getch() == b'\x1b':
            self.pressed = True
            if self._on_cancel:
                self._on_cancel()
            return True
```

**区别：**
- Unix: 非阻塞 (`select`)
- Windows: 阻塞 (`msvcrt`)

## 使用示例

```python
def cancel():
    engine.cancel_turn()

listener = EscListener(on_cancel=cancel)
with listener:
    for event in engine.submit(user_input):
        if listener.check_esc_nonblocking():
            break  # ESC 被按下，退出循环
        ...
```

## 使用场景

1. **取消流式响应**：用户按下 ESC 立即停止生成
2. **安全交互**：避免用户在等待时按键被"偷取"（通过 pause/resume）
3. **用户体验**：随时可中断，无卡顿

## 技术亮点

1. **避免竞态条件**：正确使用原始 fd 避免与 select 的缓冲区问题
2. **智能过滤**：区分裸 ESC 和 escape 序列
3. **跨平台**：自动适配 Unix 和 Windows
4. **线程安全**：回调是单线程安全的设计
5. **资源管理**：使用 context manager 自动清理

---

*文件路径：`/Users/huguoqing/zzzhu/code/exp/RAG/project1/context_system/cc-mini/src/core/_keylistener.py`*
