from enum import Enum

class AgentType(Enum):
    MAIN = "main"
    PLANNER = "planner"
    CODE = "code"
    REVIEW = "review"

class AgentCoordinator:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def run_sequential(self, session_id, agent_types, task, model_call):
        results = []
        for typ in agent_types:
            res = await self._run_agent(typ, task, model_call)
            results.append((typ.value, res))
        return results

    async def _run_agent(self, typ, task, model_call):
        prompt = self._get_prompt(typ)
        msgs = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": task}
        ]
        return await model_call(msgs)

    def _get_prompt(self, typ):
        if typ == AgentType.PLANNER:
            return "你是规划智能体，输出步骤"
        if typ == AgentType.CODE:
            return "你是代码智能体"
        if typ == AgentType.REVIEW:
            return "你是审查智能体"
        return "你是主智能体"

AGENT_COORD = AgentCoordinator()