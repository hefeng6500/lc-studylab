#!/bin/bash

# LC-StudyLab Docker 一键启动脚本

set -e

echo "=========================================="
echo "LC-StudyLab Docker 部署脚本"
echo "=========================================="
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: 未检测到 Docker，请先安装 Docker"
    echo "   安装指南: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ 错误: 未检测到 Docker Compose，请先安装 Docker Compose"
    echo "   安装指南: https://docs.docker.com/compose/install/"
    exit 1
fi

# 检查 .env 文件是否存在
if [ ! -f .env ]; then
    echo "📝 创建 .env 文件..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ 已从 .env.example 创建 .env 文件"
        echo ""
        echo "⚠️  请编辑 .env 文件，填写必要的配置（特别是 OPENAI_API_KEY）"
        echo "   编辑完成后，再次运行此脚本"
        exit 0
    else
        echo "❌ 错误: 未找到 .env.example 文件"
        exit 1
    fi
fi

# 检查 OPENAI_API_KEY 是否配置
if ! grep -q "OPENAI_API_KEY=.*[^=]$" .env 2>/dev/null || grep -q "OPENAI_API_KEY=$" .env 2>/dev/null || grep -q "OPENAI_API_KEY=your-" .env 2>/dev/null; then
    echo "⚠️  警告: OPENAI_API_KEY 未配置或使用默认值"
    echo "   请编辑 .env 文件，填写您的 OpenAI API Key"
    read -p "   是否继续？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "🚀 开始构建和启动服务..."
echo ""

# 构建并启动服务
if docker compose version &> /dev/null; then
    docker compose up -d --build
else
    docker-compose up -d --build
fi

echo ""
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
echo ""
echo "📊 服务状态:"
if docker compose version &> /dev/null; then
    docker compose ps
else
    docker-compose ps
fi

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo ""
echo "访问地址:"
echo "  - 前端应用: http://localhost:3000"
echo "  - 后端 API: http://localhost:8000"
echo "  - API 文档: http://localhost:8000/docs"
echo ""
echo "常用命令:"
echo "  - 查看日志: docker-compose logs -f"
echo "  - 停止服务: docker-compose down"
echo "  - 重启服务: docker-compose restart"
echo ""
echo "详细文档请查看: DOCKER.md"

