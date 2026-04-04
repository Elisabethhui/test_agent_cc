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