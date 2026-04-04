# main.py
import asyncio
from olmx_client import OLMxClient
from agents import get_agent_by_type
from core.executor import AgentExecutor
from core.session_memory import session_mem

async def main():
    # 初始化客户端
    client = OLMxClient()
    
    # 模拟项目启动：加载记忆
    session_mem.set_memory("project", "style", "PEP8")
    session_mem.set_memory("user", "preference", "No verbose logs")
    
    # 获取 Plan 智能体 (架构师)
    plan_agent = get_agent_by_type("Plan")
    
    # 注入 Fork 指令 (模拟源码中的 forkSubagent 逻辑)
    plan_agent.fork_directive = "你是一个临时分身。请在 300 字内给出结果。禁止进行代码写入。"
    
    # 实例化执行器
    executor = AgentExecutor(plan_agent, client)
    
    print("--- Claude Code Minimal Implementation Booted ---")
    
    # 模拟任务
    task = "请分析当前项目的 core 目录结构，并给出一个重构计划。"
    print(f"\nUser: {task}")
    
    response = await executor.run_turn(task)
    print(f"\nAssistant: {response}")
    
    # 模拟多轮对话触发压缩逻辑
    print("\n--- 正在模拟多轮对话以展示自动压缩能力 ---")
    for _ in range(5):
        executor.messages.append({"role": "tool", "name": "bash", "content": "A" * 3000}) # 构造超长工具输出
    
    await executor.run_turn("继续之前的重构建议。")
    print("\n[系统状态] 已自动执行微压缩 (Micro-Compaction)，旧的工具结果已被物理剔除。")

if __name__ == "__main__":
    asyncio.run(main())