#!/bin/bash

# model-auto-switch 技能启动脚本
# 一键启动所有服务

set -e

echo "🚀 启动 model-auto-switch 技能..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数：打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    print_info "检查系统依赖..."
    
    # 检查 Python
    if command -v python3 &> /dev/null; then
        python_version=$(python3 --version | awk '{print $2}')
        print_success "Python $python_version 已安装"
    else
        print_error "Python3 未安装，请先安装 Python3"
        exit 1
    fi
    
    # 检查 Node.js
    if command -v node &> /dev/null; then
        node_version=$(node --version)
        print_success "Node.js $node_version 已安装"
    else
        print_warning "Node.js 未安装，管理后台将无法启动"
    fi
    
    # 检查 curl
    if command -v curl &> /dev/null; then
        print_success "curl 已安装"
    else
        print_warning "curl 未安装，部分功能可能受限"
    fi
    
    # 检查 jq
    if command -v jq &> /dev/null; then
        print_success "jq 已安装"
    else
        print_warning "jq 未安装，JSON 处理功能可能受限"
    fi
}

# 检查服务状态
check_service_status() {
    print_info "检查服务状态..."
    
    # 检查管理后台
    if curl -s http://localhost:8191/api/health > /dev/null 2>&1; then
        print_success "管理后台正在运行"
        return 0
    else
        print_warning "管理后台未运行"
        return 1
    fi
}

# 启动管理后台
start_admin_panel() {
    print_info "启动管理后台..."
    
    cd admin
    
    # 检查 Node.js 依赖
    if [ ! -d "node_modules" ]; then
        print_warning "Node.js 依赖未安装，正在安装..."
        npm install
    fi
    
    # 启动服务器
    NODE_ENV=development node server.js &
    ADMIN_PID=$!
    
    # 等待服务器启动
    sleep 3
    
    # 检查是否启动成功
    if curl -s http://localhost:8191/api/health > /dev/null 2>&1; then
        print_success "管理后台启动成功 (PID: $ADMIN_PID)"
        echo $ADMIN_PID > .admin_pid
    else
        print_error "管理后台启动失败"
        return 1
    fi
    
    cd ..
}

# 启动 API 服务器
start_api_server() {
    print_info "启动 API 服务器..."
    
    # 检查 Python 依赖
    if [ ! -f "requirements.txt" ]; then
        print_warning "未找到 requirements.txt，跳过 API 服务器启动"
        return 0
    fi
    
    # 启动 API 服务器
    python3 scripts/model_api_server.py &
    API_PID=$!
    
    sleep 2
    
    # 检查是否启动成功
    if curl -s http://localhost:8190/health > /dev/null 2>&1; then
        print_success "API 服务器启动成功 (PID: $API_PID)"
        echo $API_PID > .api_pid
    else
        print_warning "API 服务器启动失败或未启用"
    fi
}

# 显示服务信息
show_service_info() {
    echo ""
    echo "=========================================="
    echo "        model-auto-switch 服务信息        "
    echo "=========================================="
    echo ""
    
    # 管理后台信息
    if [ -f "admin/.admin_pid" ]; then
        ADMIN_PID=$(cat admin/.admin_pid)
        if ps -p $ADMIN_PID > /dev/null; then
            echo "✅ 管理后台: 运行中 (PID: $ADMIN_PID)"
            echo "   访问地址: http://localhost:8191/admin"
            echo "   API 地址: http://localhost:8191/api"
            echo "   WebSocket: ws://localhost:8191"
        else
            echo "❌ 管理后台: 已停止"
        fi
    else
        echo "❌ 管理后台: 未启动"
    fi
    
    echo ""
    
    # API 服务器信息
    if [ -f ".api_pid" ]; then
        API_PID=$(cat .api_pid)
        if ps -p $API_PID > /dev/null; then
            echo "✅ API 服务器: 运行中 (PID: $API_PID)"
            echo "   访问地址: http://localhost:8190"
        else
            echo "❌ API 服务器: 已停止"
        fi
    else
        echo "⚠️  API 服务器: 未启用"
    fi
    
    echo ""
    echo "=========================================="
    echo "常用命令:"
    echo "  ./stop_all.sh          # 停止所有服务"
    echo "  ./restart.sh           # 重启所有服务"
    echo "  ./status.sh            # 查看服务状态"
    echo ""
    echo "测试页面:"
    echo "  http://localhost:8191/test.html"
    echo "  http://localhost:8191/final_test.html"
    echo ""
    echo "文档:"
    echo "  SKILL.md              # 技能说明"
    echo "  SKILL_ENHANCED.md     # 详细文档"
    echo "=========================================="
}

# 停止服务
stop_services() {
    print_info "停止服务..."
    
    # 停止管理后台
    if [ -f "admin/.admin_pid" ]; then
        ADMIN_PID=$(cat admin/.admin_pid)
        if ps -p $ADMIN_PID > /dev/null; then
            kill $ADMIN_PID
            print_success "管理后台已停止 (PID: $ADMIN_PID)"
        fi
        rm -f admin/.admin_pid
    fi
    
    # 停止 API 服务器
    if [ -f ".api_pid" ]; then
        API_PID=$(cat .api_pid)
        if ps -p $API_PID > /dev/null; then
            kill $API_PID
            print_success "API 服务器已停止 (PID: $API_PID)"
        fi
        rm -f .api_pid
    fi
}

# 清理临时文件
cleanup() {
    print_info "清理临时文件..."
    
    rm -f admin/.admin_pid
    rm -f .api_pid
    
    print_success "清理完成"
}

# 主函数
main() {
    echo ""
    echo "=========================================="
    echo "   model-auto-switch 技能启动脚本 v1.0   "
    echo "=========================================="
    echo ""
    
    # 检查参数
    case "$1" in
        stop)
            stop_services
            cleanup
            exit 0
            ;;
        restart)
            stop_services
            sleep 2
            ;;
        status)
            check_service_status
            show_service_info
            exit 0
            ;;
        help|--help|-h)
            echo "用法: $0 [command]"
            echo ""
            echo "命令:"
            echo "  start    启动所有服务 (默认)"
            echo "  stop     停止所有服务"
            echo "  restart  重启所有服务"
            echo "  status   查看服务状态"
            echo "  help     显示帮助信息"
            echo ""
            exit 0
            ;;
    esac
    
    # 检查依赖
    check_dependencies
    
    # 检查是否已在运行
    if check_service_status; then
        print_warning "服务已在运行，尝试重启..."
        stop_services
        sleep 2
    fi
    
    # 启动服务
    start_admin_panel
    start_api_server
    
    # 显示服务信息
    show_service_info
    
    # 设置退出时的清理
    trap 'print_info "正在停止服务..."; stop_services; cleanup; print_success "服务已停止"' EXIT
    
    echo ""
    print_success "所有服务启动完成！"
    echo ""
    
    # 保持脚本运行
    if [ "$1" != "daemon" ]; then
        echo "按 Ctrl+C 停止服务"
        wait
    fi
}

# 运行主函数
main "$@"