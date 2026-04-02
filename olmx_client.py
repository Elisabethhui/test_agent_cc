import json
import httpx
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# ======================
# 🔥 你的本地 MLX Qwen3.5
# ======================
llm = ChatOpenAI(
    model="Qwen3.5-9B-MLX-4bit",
    api_key="w2hqq0809",
    base_url="http://localhost:8000/v1",
    temperature=0.1
)

# ======================
# ✅ 模型调用（新版 LangChain 格式）
# ======================
async def model_call(messages):
    langchain_msgs = []
    for m in messages:
        content = m["content"]
        if m["role"] == "system":
            langchain_msgs.append(SystemMessage(content=content))
        elif m["role"] == "assistant":
            langchain_msgs.append(AIMessage(content=content))
        else:
            langchain_msgs.append(HumanMessage(content=content))
    
    # 新版异步调用
    return await llm.ainvoke(langchain_msgs)

