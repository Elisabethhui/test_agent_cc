# main.py
import asyncio
from olmx_client import OLMxClient
from core.executor import AgentExecutor
from agents.coordinator_agent import CoordinatorAgent
from core.session_memory import session_mem

async def main():
    # 初始化客户端
    client = OLMxClient()
    
    # 模拟项目记忆加载
    session_mem.save_to_scope("project", "coding_style", "Use PascalCase for classes")
    session_mem.save_to_scope("user", "preference", "Verbose logs")
    
    # 启动协调器模式
    coord = CoordinatorAgent()
    executor = AgentExecutor({
        "system_prompt": coord.system_prompt,
        "cwd": "/home/project/test_agent_cc"
    }, client)
    
    print("--- Claude Code Minimal Implementation (Python) ---")
    
    # 测试多轮对话触发压缩与治理
    query = "请分析当前项目的架构，并制定一个升级到分布式系统的计划。"
    print(f"User: {query}")
    
    response = await executor.run_turn(query)
    print(f"\nAssistant: {response}")

if __name__ == "__main__":
    asyncio.run(main())