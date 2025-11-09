"""
统一配置管理模块
使用 Pydantic Settings 管理所有配置项，支持从环境变量和 .env 文件加载
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    应用配置类
    
    所有配置项都可以通过环境变量或 .env 文件设置
    优先级：环境变量 > .env 文件 > 默认值
    """
    
    # ==================== OpenAI 配置 ====================
    openai_api_key: str = Field(
        default="",
        description="OpenAI API 密钥，必须设置"
    )
    
    openai_api_base: str = Field(
        default="https://api.openai.com/v1",
        description="OpenAI API 基础 URL"
    )
    
    openai_model: str = Field(
        default="gpt-4o",
        description="默认使用的 OpenAI 模型"
    )
    
    openai_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="模型温度参数，控制输出的随机性"
    )
    
    openai_max_tokens: Optional[int] = Field(
        default=None,
        description="最大生成 token 数，None 表示使用模型默认值"
    )
    
    openai_streaming: bool = Field(
        default=True,
        description="是否默认启用流式输出"
    )
    
    # ==================== Tavily 搜索配置 ====================
    tavily_api_key: str = Field(
        default="",
        description="Tavily 搜索 API 密钥（可选）"
    )
    
    tavily_max_results: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Tavily 搜索返回的最大结果数"
    )
    
    # ==================== 高德地图配置 ====================
    amap_key: str = Field(
        default="",
        description="高德地图 API 密钥（可选，用于天气查询等服务）"
    )
    
    # ==================== 服务器配置 ====================
    server_host: str = Field(
        default="0.0.0.0",
        description="服务器监听地址"
    )
    
    server_port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="服务器监听端口"
    )
    
    server_reload: bool = Field(
        default=True,
        description="开发模式下是否自动重载"
    )
    
    # ==================== 日志配置 ====================
    log_level: str = Field(
        default="INFO",
        description="日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )
    
    log_file: str = Field(
        default="logs/app.log",
        description="日志文件路径"
    )
    
    log_rotation: str = Field(
        default="100 MB",
        description="日志文件轮转大小"
    )
    
    log_retention: str = Field(
        default="30 days",
        description="日志文件保留时间"
    )
    
    # ==================== 应用配置 ====================
    app_name: str = Field(
        default="LC-StudyLab",
        description="应用名称"
    )
    
    app_version: str = Field(
        default="0.1.0",
        description="应用版本"
    )
    
    debug: bool = Field(
        default=False,
        description="是否启用调试模式"
    )
    
    # ==================== 数据目录配置 ====================
    DATA_DIR: str = Field(
        default="data",
        description="数据存储根目录"
    )
    
    # ==================== Agent 配置 ====================
    agent_max_iterations: int = Field(
        default=15,
        ge=1,
        le=100,
        description="Agent 最大迭代次数"
    )
    
    agent_max_execution_time: Optional[float] = Field(
        default=None,
        description="Agent 最大执行时间（秒），None 表示无限制"
    )
    
    # ==================== RAG 配置 ====================
    # Embedding 配置
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="OpenAI Embedding 模型名称"
    )
    
    embedding_batch_size: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Embedding 批处理大小"
    )
    
    # 文本分块配置
    chunk_size: int = Field(
        default=1000,
        ge=100,
        le=10000,
        description="文本分块大小（字符数）"
    )
    
    chunk_overlap: int = Field(
        default=200,
        ge=0,
        le=1000,
        description="文本分块重叠大小（字符数）"
    )
    
    # 向量库配置
    vector_store_type: str = Field(
        default="faiss",
        description="向量库类型：faiss, inmemory, chroma"
    )
    
    vector_store_path: str = Field(
        default="data/indexes",
        description="向量库存储路径"
    )
    
    # 检索配置
    retriever_search_type: str = Field(
        default="similarity",
        description="检索类型：similarity, mmr, similarity_score_threshold"
    )
    
    retriever_k: int = Field(
        default=4,
        ge=1,
        le=20,
        description="检索返回的文档数量"
    )
    
    retriever_score_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="相似度阈值（仅用于 similarity_score_threshold 模式）"
    )
    
    retriever_fetch_k: int = Field(
        default=20,
        ge=1,
        le=100,
        description="MMR 检索的候选文档数量"
    )
    
    # RAG Agent 配置
    rag_agent_max_iterations: int = Field(
        default=10,
        ge=1,
        le=50,
        description="RAG Agent 最大迭代次数"
    )
    
    rag_agent_return_source_documents: bool = Field(
        default=True,
        description="是否返回来源文档"
    )
    
    # 数据路径配置
    data_documents_path: str = Field(
        default="data/documents",
        description="文档存储路径"
    )
    
    data_uploads_path: str = Field(
        default="data/uploads",
        description="上传文件存储路径"
    )
    
    # Pydantic Settings 配置
    model_config = SettingsConfigDict(
        env_file=".env",  # 从 .env 文件加载
        env_file_encoding="utf-8",
        case_sensitive=False,  # 环境变量不区分大小写
        extra="ignore",  # 忽略额外的环境变量
    )
    
    def validate_required_keys(self) -> None:
        """
        验证必需的配置项是否已设置
        
        Raises:
            ValueError: 如果必需的配置项未设置
        """
        if not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY 未设置！请在环境变量或 .env 文件中设置。"
            )
    
    def get_openai_config(self) -> dict:
        """
        获取 OpenAI 配置字典
        
        Returns:
            包含 OpenAI 配置的字典
        """
        config = {
            "api_key": self.openai_api_key,
            "base_url": self.openai_api_base,
            "model": self.openai_model,
            "temperature": self.openai_temperature,
        }
        
        if self.openai_max_tokens is not None:
            config["max_tokens"] = self.openai_max_tokens
            
        return config
    
    def get_tavily_config(self) -> dict:
        """
        获取 Tavily 配置字典
        
        Returns:
            包含 Tavily 配置的字典
        """
        return {
            "api_key": self.tavily_api_key,
            "max_results": self.tavily_max_results,
        }


# 创建全局配置实例
settings = Settings()


# 在导入时验证必需的配置
def validate_settings() -> None:
    """验证配置的辅助函数"""
    try:
        settings.validate_required_keys()
    except ValueError as e:
        # 在开发环境下，如果没有设置 API Key，只打印警告而不抛出异常
        if settings.debug:
            print(f"⚠️  配置警告: {e}")
        else:
            raise


# 如果不是在测试环境，则验证配置
import sys
if "pytest" not in sys.modules:
    # 延迟验证，允许在导入后再设置环境变量
    pass

