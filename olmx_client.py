# olmx_client.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# 配置本地模型客户端 (连接至本地 MLX Qwen 服务或 Ollama)
# 端口默认为 8000 (MLX) 或 11434 (Ollama)
llm = ChatOpenAI(
    model="Qwen3.5-9B-MLX-4bit",
    api_key="w2hqq0809",
    base_url="http://localhost:8000/v1",
    temperature=0.1
)

async def model_call(messages: list) -> str:
    """
    统一模型调用接口：将字典格式消息转换为 LangChain 消息对象并执行
    """
    langchain_msgs = []
    for m in messages:
        role = m["role"]
        content = str(m["content"])
        if role == "system":
            langchain_msgs.append(SystemMessage(content=content))
        elif role == "assistant":
            langchain_msgs.append(AIMessage(content=content))
        else:
            langchain_msgs.append(HumanMessage(content=content))
    
    # 执行异步调用
    res = await llm.ainvoke(langchain_msgs)
    return res.content