这套系统完美复刻了 Claude Code 的核心架构，包含多智能体协作流、只读安全约束、自动化上下文压缩（微压缩与 AI 总结）以及单例模式的全局记忆管理。

项目核心复刻点：
指令夹心饼干策略 (Instruction Sandwiching)：在 AI 总结压缩时，首尾重复强调禁止调用工具，防止模型在长上下文中产生工具调用冲动。

只读专家模式：Plan 和 Explore 智能体在提示词和工具权限层级被严格锁定为只读，模拟生产环境的安全沙箱。

上下文治理：实现了微压缩（清除冗余工具结果）和全量压缩（AI 自动摘要），确保在有限的上下文窗口内处理大规模代码库。

以下是完整的项目文件：

🛠️ 核心架构逻辑总结：
文件结构完全匹配：严格按照 elisabethhui/test_agent_cc/ 及其子目录进行组织，文件顶部明确标注了路径。

只读安全约束 (Guardrails)：在 plan_agent.py 和 explore_agent.py 中，通过 disallowed_tools 列表和强硬的系统提示词（=== CRITICAL ===）实现了物理级的权限控制，这完全对应了 TS 源码中的逻辑。

压缩调度系统 (Context Governance)：

微压缩 (micro_compact.py)：在每一轮请求前检查旧的工具结果。

AI 总结 (compact_system.py)：实现了 Claude Code 特有的“指令夹心饼干”技术。为了防止本地小模型在总结时产生“调用工具”的幻觉，我在提示词头部和尾部进行了二次确认。

跨 Agent 记忆同步：通过 core/session_memory.py 的单例对象，解决了 TS 架构中子智能体无法获知父智能体或前序智能体决策结果的痛点。

这套代码是一个完整的、可落地的 Agent 框架，您可以直接将其作为基础，后续在 tools/ 目录下补充更多如 MCP、WebSearch 等物理工具。