#!/bin/bash
# OpenClaw Model Auto-Switch 安装脚本

set -e

echo "🚀 OpenClaw Model Auto-Switch 安装程序"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 工具函数
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 检查命令是否存在
check_command() {
    if command -v $1 &> /dev/null; then
        print_success "$1 已安装"
        return 0
    else
        print_error "$1 未安装"
        return 1
    fi
}

# 检查目录
check_directory() {
    if [ -d "$1" ]; then
        print_success "目录存在: $1"
        return 0
    else
        print_warning "目录不存在: $1"
        return 1
    fi
}

# 检查文件
check_file() {
    if [ -f "$1" ]; then
        print_success "文件存在: $1"
        return 0
    else
        print_warning "文件不存在: $1"
        return 1
    fi
}

echo ""
echo "🔍 系统检查"
echo "=========="

# 检查 Python
check_command "python3"
PYTHON_VERSION=$(python3 --version 2>/dev/null | cut -d' ' -f2)
print_info "Python 版本: $PYTHON_VERSION"

# 检查 Node.js
check_command "node"
NODE_VERSION=$(node --version 2>/dev/null)
print_info "Node.js 版本: $NODE_VERSION"

# 检查 npm
check_command "npm"
NPM_VERSION=$(npm --version 2>/dev/null)
print_info "npm 版本: $NPM_VERSION"

# 检查 OpenClaw
if command -v openclaw &> /dev/null; then
    OPENCLAW_VERSION=$(openclaw --version 2>/dev/null | head -1)
    print_success "OpenClaw 已安装: $OPENCLAW_VERSION"
else
    print_warning "OpenClaw 未安装或不在 PATH 中"
fi

echo ""
echo "📁 文件检查"
echo "=========="

# 检查关键文件
check_file "SKILL.md"
check_file "README.md"
check_file "scripts/model_manager_enhanced.py"
check_file "scripts/model_predictive_maintenance.py"
check_file "admin/server.js"
check_file "admin/package.json"

echo ""
echo "📦 安装依赖"
echo "=========="

# 安装 Python 依赖
print_info "检查 Python 依赖..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt 2>/dev/null || print_warning "Python 依赖安装失败（可忽略）"
else
    print_info "创建 requirements.txt..."
    cat > requirements.txt << EOF
# OpenClaw Model Auto-Switch Python 依赖
EOF
fi

# 安装 Node.js 依赖
print_info "安装 Node.js 依赖..."
cd admin
if [ ! -d "node_modules" ]; then
    npm install --silent
    print_success "Node.js 依赖安装完成"
else
    print_success "Node.js 依赖已安装"
fi
cd ..

echo ""
echo "🔧 配置设置"
echo "=========="

# 创建配置文件
CONFIG_FILE="models_registry.json"
if [ ! -f "$CONFIG_FILE" ]; then
    print_info "创建配置文件: $CONFIG_FILE"
    cp references/models_registry.json.example "$CONFIG_FILE"
    print_success "配置文件已创建"
else
    print_success "配置文件已存在: $CONFIG_FILE"
fi

# 创建日志目录
LOG_DIR="logs"
if [ ! -d "$LOG_DIR" ]; then
    print_info "创建日志目录: $LOG_DIR"
    mkdir -p "$LOG_DIR"
    print_success "日志目录已创建"
else
    print_success "日志目录已存在: $LOG_DIR"
fi

# 设置脚本权限
print_info "设置脚本权限..."
chmod +x scripts/*.py scripts/*.sh admin/start.sh 2>/dev/null || true
print_success "脚本权限设置完成"

echo ""
echo "🧪 测试安装"
echo "=========="

# 测试 Python 脚本
print_info "测试 Python 脚本..."
if python3 -m py_compile scripts/model_manager_enhanced.py 2>/dev/null; then
    print_success "Python 脚本语法正确"
else
    print_warning "Python 脚本语法检查失败"
fi

# 测试 Node.js 服务器
print_info "测试 Node.js 服务器..."
cd admin
if node -c server.js 2>/dev/null; then
    print_success "Node.js 服务器语法正确"
else
    print_warning "Node.js 服务器语法检查失败"
fi
cd ..

echo ""
echo "🚀 安装完成！"
echo "============"

print_success "OpenClaw Model Auto-Switch 安装完成！"

echo ""
echo "📋 下一步操作:"
echo "1. 启动后台管理系统:"
echo "   cd admin && ./start.sh"
echo ""
echo "2. 访问管理界面:"
echo "   http://localhost:8191/admin"
echo ""
echo "3. 配置定时任务 (可选):"
echo "   crontab -e"
echo "   添加: */5 * * * * $(pwd)/scripts/model_auto_switch.sh"
echo ""
echo "4. 测试功能:"
echo "   python3 scripts/model_manager_enhanced.py status"
echo "   python3 examples/api_client.py demo"
echo ""
echo "📚 文档:"
echo "• 详细指南: INSTALL.md"
echo "• API 文档: docs/API.md"
echo "• 技能说明: SKILL.md"
echo ""
echo "💡 提示:"
echo "• 确保 OpenClaw 正在运行"
echo "• 检查防火墙设置 (端口 8191)"
echo "• 定期查看 logs/ 目录"
echo ""
echo "=========================================="
echo "🎉 安装完成！开始使用 OpenClaw Model Auto-Switch 吧！"
echo "=========================================="

exit 0