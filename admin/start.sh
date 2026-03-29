#!/bin/bash
# OpenClaw Model Auto-Switch Admin 启动脚本

set -e

echo "🚀 启动 OpenClaw 模型管理后台"
echo "=========================================="

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 错误: Node.js 未安装"
    echo "请先安装 Node.js: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js 版本: $(node --version)"

# 检查工作目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 工作目录: $(pwd)"

# 检查 package.json
if [ ! -f "package.json" ]; then
    echo "❌ 错误: package.json 不存在"
    exit 1
fi

# 安装依赖
echo "📦 检查依赖..."
if [ ! -d "node_modules" ]; then
    echo "正在安装依赖..."
    npm install
else
    echo "✅ 依赖已安装"
fi

# 检查端口占用
PORT=8191
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  端口 $PORT 已被占用"
    echo "正在尝试停止现有进程..."
    lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# 启动服务器
echo "🚀 启动服务器..."
echo "=========================================="
echo "管理界面: http://localhost:$PORT/admin"
echo "API 地址: http://localhost:$PORT/api"
echo "WebSocket: ws://localhost:$PORT"
echo "=========================================="
echo "按 Ctrl+C 停止服务器"
echo ""

# 启动服务器
npm start