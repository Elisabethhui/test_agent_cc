# olmx_client.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import logging

logger = logging.getLogger("OLMxClient")

class OLMxClient:
    """
    本地模型调用客户端。
    支持 LangChain 封装，兼容 MLX, Ollama 或 OpenAI 格式。
    """
    def __init__(self, model_name="Qwen3.5-9B-MLX-4bit", base_url="http://localhost:8000/v1"):
        self.llm = ChatOpenAI(
            model=model_name,
            api_key="w2hqq0809", # 默认占位符
            base_url=base_url,
            temperature=0.1
        )

    async def generate(self, messages: list) -> str:
        """
        核心生成接口：将字典格式消息转换为 LangChain 对象并调用。
        """
        langchain_msgs = []
        for m in messages:
            role = m["role"]
            content = str(m.get("content", ""))
            
            if role == "system":
                langchain_msgs.append(SystemMessage(content=content))
            elif role == "assistant":
                langchain_msgs.append(AIMessage(content=content))
            else:
                langchain_msgs.append(HumanMessage(content=content))
        
        try:
            res = await self.llm.ainvoke(langchain_msgs)
            return res.content
        except Exception as e:
            logger.error(f"LLM Call Error: {e}")
            return f"[ERROR]: 模型连接失败 - {str(e)}"
        


# 请严格按照以下规则执行任务，不准出错：
# 1. 只扫描路径：/Users/huguoqing/zzzhu/code/exp/RAG/project1/context_system/cc-mini/src/core/
# 2. 只读取这个目录下真实存在的 .py 文件，不要自己编造不存在的文件路径
# 3. 串行执行：处理一个文件 → 分析 → 写入 .md → 完全清除上下文历史 → 再处理下一个
# 4. 每处理完一个文件必须清空上下文，绝对不携带历史记录
# 5. 已经在 code_analyses/ 里存在的 .md 文件，对应的原文件跳过不处理
# 6. 只使用 cc-mini 内置工具：Glob、Read、Write
# 7. 不准并行，不准读错路径，不准生成不存在的文件名
# 8. 自动执行，不需要任何确认
# 请从 cc-mini/src/core/目录下第一个存在的 Python 文件开始，一个一个稳定处理，不爆上下文，不读错文件。


# export CC_MINI_MODEL="Qwen3.5-9B-MLX-4bit"                    
# export CC_MINI_PROVIDER=openai
# export OPENAI_BASE_URL=http://localhost:8000/v1
# export OPENAI_API_KEY=w2hqq0809
# export CC_MINI_MAX_TOKENS=32000
# export CC_MINI_AUTO_APPROVE=1
# export CC_MINI_AUTO_COMPACT=1