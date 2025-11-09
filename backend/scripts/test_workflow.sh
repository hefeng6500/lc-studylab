#!/bin/bash

# 学习工作流测试脚本启动器

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

# 切换到 backend 目录
cd "$BACKEND_DIR"

# 激活虚拟环境（如果存在）
if [ -d "venv" ]; then
    echo "🔧 激活虚拟环境..."
    source venv/bin/activate
fi

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  警告: .env 文件不存在"
    echo "请复制 env.example 为 .env 并配置必要的环境变量"
    exit 1
fi

# 运行测试
echo "🧪 启动学习工作流测试..."
echo ""

python scripts/test_workflow.py

# 保存退出码
EXIT_CODE=$?

echo ""
echo "测试完成，退出码: $EXIT_CODE"

exit $EXIT_CODE

