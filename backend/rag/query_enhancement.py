"""
查询增强模块

提供查询增强功能，包括：
- Query Rewriting：使用 LLM 重写查询
- Multi-Query：生成多个查询变体
- HyDE：生成假设文档用于检索

参考：
- https://docs.langchain.com/oss/python/langchain/retrieval
"""

from typing import List, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from config import settings, get_logger
from core.models import get_chat_model

logger = get_logger(__name__)


# Query Rewriting 提示词模板
QUERY_REWRITE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一个查询重写专家。你的任务是将用户的查询重写为更专业、更准确、更适合检索的查询。

重写原则：
1. 保持原查询的核心意图
2. 使用更专业、更准确的术语
3. 如果查询模糊，添加必要的上下文
4. 保持简洁，不要过度扩展

只返回重写后的查询，不要添加任何解释。"""),
    ("human", "原始查询：{query}\n\n如果提供了上下文，请考虑上下文：{context}\n\n重写后的查询："),
])


def rewrite_query(
    query: str,
    llm: Optional[BaseChatModel] = None,
    context: Optional[str] = None,
    model: Optional[str] = None,
) -> str:
    """
    使用 LLM 重写查询，使其更专业、更准确、更适合检索
    
    Args:
        query: 原始查询
        llm: LLM 模型实例，如果为 None 则使用配置中的模型
        context: 可选上下文（如对话历史）
        model: 模型字符串（如 "openai:gpt-4o"），如果 llm 为 None 则使用此参数
    
    Returns:
        重写后的查询
    
    Example:
        >>> rewritten = rewrite_query("苹果手机怎么重置")
        >>> print(rewritten)  # "iPhone 如何恢复出厂设置"
    """
    logger.info(f"✏️  重写查询: {query[:50]}...")
    
    # 获取 LLM
    if llm is None:
        # get_chat_model() 需要纯模型名（如 "gpt-5"），不需要 "openai:" 前缀
        # 如果 model 参数包含 ":"，提取模型名
        if model is None:
            model_name = settings.openai_model
        else:
            model_name = model.split(":")[-1] if ":" in model else model
        llm = get_chat_model(model_name)
    
    try:
        # 构建提示词
        prompt = QUERY_REWRITE_PROMPT.format(
            query=query,
            context=context or "无",
        )
        
        # 调用 LLM
        response = llm.invoke(prompt)
        
        # 提取重写后的查询
        rewritten_query = response.content.strip()
        
        logger.info(f"✅ 查询重写完成: {rewritten_query[:50]}...")
        return rewritten_query
        
    except Exception as e:
        logger.error(f"❌ 查询重写失败: {e}")
        # 如果重写失败，返回原查询
        logger.warning("返回原始查询")
        return query


def generate_multi_queries(
    query: str,
    llm: Optional[BaseChatModel] = None,
    num_queries: int = 3,
    model: Optional[str] = None,
) -> List[str]:
    """
    生成多个查询变体（Multi-Query）
    
    使用 LLM 将单个查询扩展为多个不同表达的查询，用于提升检索召回率。
    
    Args:
        query: 原始查询
        llm: LLM 模型实例
        num_queries: 生成的查询数量（默认 3）
        model: 模型字符串
    
    Returns:
        查询变体列表
    
    Example:
        >>> queries = generate_multi_queries("什么是机器学习？", num_queries=3)
        >>> print(queries)
        ['什么是机器学习？', '机器学习的定义是什么？', '如何解释机器学习？']
    """
    logger.info(f"🔄 生成多查询变体: {query[:50]}..., num={num_queries}")
    
    # 获取 LLM
    if llm is None:
        # get_chat_model() 需要纯模型名（如 "gpt-5"），不需要 "openai:" 前缀
        # 如果 model 参数包含 ":"，提取模型名
        if model is None:
            model_name = settings.openai_model
        else:
            model_name = model.split(":")[-1] if ":" in model else model
        llm = get_chat_model(model_name)
    
    # Multi-Query 提示词
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""你是一个查询扩展专家。给定一个查询，生成 {num_queries} 个不同表达的查询变体。

要求：
1. 每个查询变体应该从不同角度表达相同的意思
2. 使用不同的词汇和句式
3. 保持查询的核心意图不变
4. 每个查询应该独立且完整

只返回查询列表，每行一个查询，不要添加编号或其他内容。"""),
        ("human", "原始查询：{query}\n\n生成 {num_queries} 个查询变体："),
    ])
    
    try:
        # 调用 LLM
        response = llm.invoke(prompt.format_messages(
            query=query,
            num_queries=num_queries,
        ))
        
        # 解析响应，提取查询列表
        content = response.content.strip()
        queries = [q.strip() for q in content.split("\n") if q.strip()]
        
        # 确保包含原始查询
        if query not in queries:
            queries.insert(0, query)
        
        # 限制数量
        queries = queries[:num_queries]
        
        logger.info(f"✅ 生成了 {len(queries)} 个查询变体")
        for i, q in enumerate(queries, 1):
            logger.debug(f"   [{i}] {q}")
        
        return queries
        
    except Exception as e:
        logger.error(f"❌ 生成多查询失败: {e}")
        # 如果生成失败，返回原查询
        logger.warning("返回原始查询")
        return [query]


def generate_hypothetical_document(
    query: str,
    llm: Optional[BaseChatModel] = None,
    model: Optional[str] = None,
) -> str:
    """
    生成假设文档（HyDE - Hypothetical Document Embedding）
    
    使用 LLM 根据查询生成一个假设的答案文档，然后对这个假设文档进行 embedding，
    用于检索。这样可以提升检索精度。
    
    Args:
        query: 用户查询
        llm: LLM 模型实例
        model: 模型字符串
    
    Returns:
        假设文档内容
    
    Example:
        >>> hyde_doc = generate_hypothetical_document("什么是机器学习？")
        >>> print(hyde_doc)
        # 生成一个关于机器学习的假设答案文档
    """
    logger.info(f"📝 生成假设文档: {query[:50]}...")
    
    # 获取 LLM
    if llm is None:
        # get_chat_model() 需要纯模型名（如 "gpt-5"），不需要 "openai:" 前缀
        # 如果 model 参数包含 ":"，提取模型名
        if model is None:
            model_name = settings.openai_model
        else:
            model_name = model.split(":")[-1] if ":" in model else model
        llm = get_chat_model(model_name)
    
    # HyDE 提示词
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个文档生成专家。给定一个查询，生成一个假设的答案文档。

要求：
1. 文档应该直接回答查询问题
2. 使用专业、准确的术语
3. 文档应该完整、连贯
4. 长度适中（200-500 字）
5. 不要使用"根据查询"、"用户问"等元语言

只返回文档内容，不要添加任何解释或标记。"""),
        ("human", "查询：{query}\n\n生成假设答案文档："),
    ])
    
    try:
        # 调用 LLM
        response = llm.invoke(prompt.format_messages(query=query))
        
        # 提取假设文档
        hypothetical_doc = response.content.strip()
        
        logger.info(f"✅ 假设文档生成完成: {len(hypothetical_doc)} 字符")
        logger.debug(f"   文档预览: {hypothetical_doc[:100]}...")
        
        return hypothetical_doc
        
    except Exception as e:
        logger.error(f"❌ 生成假设文档失败: {e}")
        raise


def enhance_query(
    query: str,
    method: str = "rewrite",
    llm: Optional[BaseChatModel] = None,
    context: Optional[str] = None,
    num_queries: Optional[int] = None,
    model: Optional[str] = None,
) -> str | List[str]:
    """
    查询增强的统一接口
    
    Args:
        query: 原始查询
        method: 增强方法
            - "rewrite": 查询重写（返回单个字符串）
            - "multi_query": 多查询生成（返回列表）
            - "hyde": 生成假设文档（返回字符串）
        llm: LLM 模型实例
        context: 可选上下文
        num_queries: Multi-Query 的查询数量
        model: 模型字符串
    
    Returns:
        增强后的查询（字符串或列表）
    
    Example:
        >>> # 查询重写
        >>> rewritten = enhance_query("苹果手机怎么重置", method="rewrite")
        >>> 
        >>> # 多查询生成
        >>> queries = enhance_query("什么是机器学习？", method="multi_query", num_queries=3)
        >>> 
        >>> # 生成假设文档
        >>> hyde_doc = enhance_query("什么是机器学习？", method="hyde")
    """
    num_queries = num_queries or settings.multi_query_num_queries
    
    if method == "rewrite":
        return rewrite_query(query, llm=llm, context=context, model=model)
    elif method == "multi_query":
        return generate_multi_queries(query, llm=llm, num_queries=num_queries, model=model)
    elif method == "hyde":
        return generate_hypothetical_document(query, llm=llm, model=model)
    else:
        raise ValueError(f"未知的增强方法: {method}。支持的方法: rewrite, multi_query, hyde")

