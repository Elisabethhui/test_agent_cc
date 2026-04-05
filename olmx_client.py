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
        
请你作为 AI Agent，使用你自带的工具链自动完成以下任务：
  1. 使用 Glob 工具扫描/Users/huguoqing/zzzhu/code/exp/RAG/project1/context_system/cc-mini/src/下所有 .py 文件
  2. 对每个文件使用 Read 工具读取内容
  3. 对代码进行深度分析：功能、架构、技术要点、核心逻辑、关键函数、意图
  4. 使用 Write 工具为每个文件生成同名的分析文档 .md
  5. 所有文档保存到 code_analyses/ 目录
  6. 不要问我确认，直接自动执行所有工具
  7. 全程使用你自己的工具链完成，不要生成独立Python脚本
  8. 请停止并行处理，改为串行执行：一个文件读取完成 → 分析完成 → 写入 .md 之后，再处理下一个文件。不要同时处理多个文件。
  9. 忽略code_analyses/文件夹下已经存在的.md对应的文件