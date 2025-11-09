#!/usr/bin/env python3
"""
智能天气查询测试脚本
测试上下文记忆和精准的时间范围查询
"""

import sys
import asyncio
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents import create_base_agent
from core.tools import ALL_TOOLS
from config import setup_logging, get_logger

# 初始化日志
setup_logging()
logger = get_logger(__name__)


async def test_context_memory():
    """测试上下文记忆功能"""
    logger.info("=" * 70)
    logger.info("测试场景：上下文记忆 + 智能天气查询")
    logger.info("=" * 70)
    
    # 创建 Agent（使用所有工具）
    agent = create_base_agent(tools=ALL_TOOLS, prompt_mode="default")
    
    # 模拟对话历史（用于存储上下文）
    chat_history = []
    
    # 第一轮：询问明天深圳的天气
    print("\n" + "=" * 70)
    print("👤 用户: 帮我查询一下明天深圳的天气")
    print("=" * 70)
    
    from langchain_core.messages import HumanMessage, AIMessage
    
    user_msg_1 = "帮我查询一下明天深圳的天气"
    response_1 = await agent.ainvoke(
        input_text=user_msg_1,
        chat_history=chat_history,
    )
    
    print(f"\n🤖 助手: {response_1}\n")
    
    # 更新对话历史
    chat_history.append(HumanMessage(content=user_msg_1))
    chat_history.append(AIMessage(content=response_1))
    
    # 第二轮：询问后天（应该自动记住深圳）
    print("\n" + "=" * 70)
    print("👤 用户: 后天呢？")
    print("=" * 70)
    
    user_msg_2 = "后天呢？"
    response_2 = await agent.ainvoke(
        input_text=user_msg_2,
        chat_history=chat_history,
    )
    
    print(f"\n🤖 助手: {response_2}\n")
    
    # 更新对话历史
    chat_history.append(HumanMessage(content=user_msg_2))
    chat_history.append(AIMessage(content=response_2))
    
    # 第三轮：询问今天（应该继续记住深圳）
    print("\n" + "=" * 70)
    print("👤 用户: 那今天怎么样？")
    print("=" * 70)
    
    user_msg_3 = "那今天怎么样？"
    response_3 = await agent.ainvoke(
        input_text=user_msg_3,
        chat_history=chat_history,
    )
    
    print(f"\n🤖 助手: {response_3}\n")
    
    logger.info("=" * 70)
    logger.info("✅ 上下文记忆测试完成！")
    logger.info("=" * 70)


async def test_single_day_query():
    """测试单日天气查询的准确性"""
    logger.info("\n" + "=" * 70)
    logger.info("测试场景：单日天气查询（应该只返回一天，不返回多天）")
    logger.info("=" * 70)
    
    agent = create_base_agent(tools=ALL_TOOLS, prompt_mode="default")
    
    test_queries = [
        "明天北京天气怎么样？",
        "后天上海会下雨吗？",
        "今天广州的温度是多少？",
    ]
    
    for query in test_queries:
        print("\n" + "-" * 70)
        print(f"👤 用户: {query}")
        print("-" * 70)
        
        response = await agent.ainvoke(input_text=query, chat_history=[])
        print(f"\n🤖 助手: {response}\n")
    
    logger.info("=" * 70)
    logger.info("✅ 单日天气查询测试完成！")
    logger.info("=" * 70)


async def main():
    """主测试函数"""
    print("\n" + "🌟" * 35)
    print("   智能天气查询 + 上下文记忆测试")
    print("🌟" * 35 + "\n")
    
    # 测试 1：上下文记忆
    await test_context_memory()
    
    # 等待一下
    await asyncio.sleep(2)
    
    # 测试 2：单日查询准确性
    await test_single_day_query()
    
    print("\n" + "🎉" * 35)
    print("   所有测试完成！")
    print("🎉" * 35 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 测试中断")
    except Exception as e:
        logger.error(f"测试出错: {e}", exc_info=True)
        print(f"\n❌ 测试失败: {e}")



