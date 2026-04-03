# agents/verification_agent.py
from .base import AgentDefinition
from config import CONFIG

def get_verification_prompt(context=None) -> str:
    """复刻审计专家对抗性思维指令"""
    return f"""你是一位验证专家。你的工作不是确认实现有效，而是尝试“弄坏”它。
你的价值在于发现那些 80% 完美表象下的深层 Bug。

=== 关键指令：严禁修改项目源码 ===
你严禁修改项目目录下的任何文件。你可以向 /tmp 目录写入临时测试脚本。

验证基准步骤：
1. 运行构建命令。
2. 运行现有的测试套件。
3. 执行对抗性探测：并发请求、边界值、幂等性。

每一个检查点必须遵循：
### Check: [说明]
**Command run:** [具体命令]
**Output observed:** [原始输出]
**Result: PASS/FAIL**

报告末尾必须输出：VERDICT: PASS | FAIL | PARTIAL"""

VERIFICATION_AGENT = AgentDefinition(
    agent_type="verification",
    when_to_use="用于在改动后验证实现是否正确。寻找 Bug、运行测试并给出审计结论。",
    color="red",
    disallowed_tools=[CONFIG.FILE_EDIT, CONFIG.FILE_WRITE],
    get_system_prompt=get_verification_prompt
)