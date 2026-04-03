# main.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__)))
import asyncio
from core.executor import AgentExecutor
from core.session_memory import SESSION_MEMORY

async def main():
    """
    Claude Code 最小复现版 - 演示多 Agent 协作工作流
    模拟：Plan Agent (规划) -> 更新记忆 -> Verification Agent (审计)
    """
    print("🚀 [Claude Code] 初始化智能体系统...\n" + "="*40)

    # 任务：重构项目的记忆管理模块
    
    # 步骤 1：召唤 Plan Agent 制定蓝图
    planner = AgentExecutor("Plan")
    print(">> 召唤架构师规划中...")
    plan = await planner.execute("请帮我制定一个将 SessionMemory 改为支持本地文件持久化存储的方案。")
    print(f"\n[规划摘要]:\n{plan[:200]}...")

    # 更新单例记忆中心，将规划结果告知系统
    SESSION_MEMORY.memory = f"当前架构师确定的重构方案：{plan[:100]}..."

    # 步骤 2：召唤审计专家进行安全审查
    # verifier 启动时会通过单例模式自动感知 planner 留下的记忆
    verifier = AgentExecutor("verification")
    print("\n>> 召唤审计员进行安全性验证中...")
    audit_report = await verifier.execute("分析上面的持久化方案，指出可能的路径穿越或权限泄露风险。")
    
    print("\n" + "="*40)
    print("🏆 [任务完成] 审计专家结论如下：")
    print(audit_report)

if __name__ == "__main__":
    # 请确保本地 8000 端口已启动兼容 OpenAI 协议的模型推理服务
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n❌ 执行失败：{e}\n提示：请检查本地模型服务端(localhost:8000)是否在线。")