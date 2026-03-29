#!/bin/bash

# openclaw-model-balancer 技能停止脚本

set -e

echo "🛑 停止 openclaw-model-balancer 技能..."

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

# 停止管理后台
stop_admin_panel() {
    print_info "停止管理后台..."
    
    if [ -f "admin/.admin_pid" ]; then
        ADMIN_PID=$(cat admin/.admin_pid)
        if ps -p $ADMIN_PID > /dev/null; then
            kill $ADMIN_PID
            sleep 1
            if ps -p $ADMIN_PID > /dev/null; then
                kill -9 $ADMIN_PID
                print_warning "强制停止管理后台 (PID: $ADMIN_PID)"
            else
                print_success "管理后台已停止 (PID: $ADMIN_PID)"
            fi
        else
            print_warning "管理后台进程不存在 (PID: $ADMIN_PID)"
        fi
        rm -f admin/.admin_pid
    else
        # 尝试查找并停止进程
        ADMIN_PIDS=$(ps aux | grep "node server.js" | grep -v grep | awk '{print $2}')
        if [ -n "$ADMIN_PIDS" ]; then
            for pid in $ADMIN_PIDS; do
                kill $pid
                print_success "停止管理后台进程 (PID: $pid)"
            done
        else
            print_info "管理后台未运行"
        fi
    fi
}

# 停止 API 服务器
stop_api_server() {
    print_info "停止 API 服务器..."
    
    if [ -f ".api_pid" ]; then
        API_PID=$(cat .api_pid)
        if ps -p $API_PID > /dev/null; then
            kill $API_PID
            sleep 1
            if ps -p $API_PID > /dev/null; then
                kill -9 $API_PID
                print_warning "强制停止 API 服务器 (PID: $API_PID)"
            else
                print_success "API 服务器已停止 (PID: $API_PID)"
            fi
        else
            print_warning "API 服务器进程不存在 (PID: $API_PID)"
        fi
        rm -f .api_pid
    else
        # 尝试查找并停止进程
        API_PIDS=$(ps aux | grep "model_api_server.py" | grep -v grep | awk '{print $2}')
        if [ -n "$API_PIDS" ]; then
            for pid in $API_PIDS; do
                kill $pid
                print_success "停止 API 服务器进程 (PID: $pid)"
            done
        else
            print_info "API 服务器未运行"
        fi
    fi
}

# 停止所有相关进程
stop_all_processes() {
    print_info "停止所有相关进程..."
    
    # 停止 Python 进程
    PYTHON_PROCESSES=(
        "model_api_server.py"
        "model_manager_enhanced.py"
        "model_predictive_maintenance.py"
    )
    
    for process in "${PYTHON_PROCESSES[@]}"; do
        PIDS=$(ps aux | grep "$process" | grep -v grep | awk '{print $2}')
        if [ -n "$PIDS" ]; then
            for pid in $PIDS; do
                kill $pid 2>/dev/null && print_success "停止 $process (PID: $pid)" || true
            done
        fi
    done
    
    # 停止 Node.js 进程
    NODE_PROCESSES=$(ps aux | grep "node" | grep -v grep | awk '{print $2}')
    if [ -n "$NODE_PROCESSES" ]; then
        for pid in $NODE_PROCESSES; do
            # 检查是否是我们的服务器
            if lsof -p $pid | grep -q ":8191"; then
                kill $pid 2>/dev/null && print_success "停止 Node.js 服务器 (PID: $pid)" || true
            fi
        done
    fi
}

# 清理临时文件
cleanup() {
    print_info "清理临时文件..."
    
    rm -f admin/.admin_pid
    rm -f .api_pid
    rm -f .*.pid 2>/dev/null || true
    
    print_success "清理完成"
}

# 验证停止
verify_stop() {
    print_info "验证服务已停止..."
    
    # 检查端口占用
    if lsof -i :8191 > /dev/null 2>&1; then
        print_warning "端口 8191 仍被占用"
        return 1
    fi
    
    if lsof -i :8190 > /dev/null 2>&1; then
        print_warning "端口 8190 仍被占用"
        return 1
    fi
    
    # 检查进程
    if ps aux | grep -E "(node server.js|model_api_server.py)" | grep -v grep > /dev/null; then
        print_warning "仍有相关进程在运行"
        return 1
    fi
    
    print_success "所有服务已成功停止"
    return 0
}

# 显示停止状态
show_stop_status() {
    echo ""
    echo "=========================================="
    echo "       服务停止状态报告        "
    echo "=========================================="
    echo ""
    
    # 检查管理后台
    if [ -f "admin/.admin_pid" ]; then
        echo "❌ 管理后台: PID 文件仍存在"
    else
        echo "✅ 管理后台: PID 文件已清理"
    fi
    
    # 检查 API 服务器
    if [ -f ".api_pid" ]; then
        echo "❌ API 服务器: PID 文件仍存在"
    else
        echo "✅ API 服务器: PID 文件已清理"
    fi
    
    # 检查端口占用
    echo ""
    echo "端口占用检查:"
    if lsof -i :8191 > /dev/null 2>&1; then
        echo "❌ 端口 8191: 被占用"
    else
        echo "✅ 端口 8191: 空闲"
    fi
    
    if lsof -i :8190 > /dev/null 2>&1; then
        echo "❌ 端口 8190: 被占用"
    else
        echo "✅ 端口 8190: 空闲"
    fi
    
    echo ""
    echo "=========================================="
}

# 主函数
main() {
    echo ""
    echo "=========================================="
    echo "   openclaw-model-balancer 技能停止脚本 v1.0   "
    echo "=========================================="
    echo ""
    
    # 检查参数
    case "$1" in
        force|-f|--force)
            FORCE=true
            print_warning "强制停止模式"
            ;;
        help|--help|-h)
            echo "用法: $0 [options]"
            echo ""
            echo "选项:"
            echo "  force    强制停止所有进程"
            echo "  help     显示帮助信息"
            echo ""
            exit 0
            ;;
    esac
    
    # 停止服务
    stop_admin_panel
    stop_api_server
    
    # 如果需要，停止所有进程
    if [ "$FORCE" = true ]; then
        stop_all_processes
    fi
    
    # 清理临时文件
    cleanup
    
    # 验证停止
    if verify_stop; then
        print_success "✅ 所有服务已成功停止"
    else
        print_warning "⚠️  部分服务可能未完全停止"
        if [ "$FORCE" != true ]; then
            echo ""
            echo "如需强制停止，请运行: $0 force"
        fi
    fi
    
    # 显示状态
    show_stop_status
    
    echo ""
    print_success "停止操作完成！"
    echo ""
}

# 运行主函数
main "$@"