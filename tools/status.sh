#!/bin/bash

# model-auto-switch 技能状态检查脚本

set -e

echo "🔍 检查 model-auto-switch 技能状态..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

print_section() {
    echo ""
    echo -e "${CYAN}=== $1 ===${NC}"
    echo ""
}

# 检查进程状态
check_process_status() {
    print_section "进程状态"
    
    # 检查管理后台
    if [ -f "admin/.admin_pid" ]; then
        ADMIN_PID=$(cat admin/.admin_pid)
        if ps -p $ADMIN_PID > /dev/null; then
            echo -e "✅ 管理后台: 运行中 (PID: $ADMIN_PID)"
            
            # 获取进程信息
            PROCESS_INFO=$(ps -p $ADMIN_PID -o pid,user,%cpu,%mem,etime,command | tail -1)
            echo "   进程信息: $PROCESS_INFO"
        else
            echo -e "❌ 管理后台: PID 文件存在但进程未运行 (PID: $ADMIN_PID)"
        fi
    else
        # 尝试查找进程
        ADMIN_PIDS=$(ps aux | grep "node server.js" | grep -v grep | awk '{print $2}')
        if [ -n "$ADMIN_PIDS" ]; then
            echo -e "⚠️  管理后台: 运行中但无 PID 文件"
            for pid in $ADMIN_PIDS; do
                echo "   进程 PID: $pid"
            done
        else
            echo -e "❌ 管理后台: 未运行"
        fi
    fi
    
    echo ""
    
    # 检查 API 服务器
    if [ -f ".api_pid" ]; then
        API_PID=$(cat .api_pid)
        if ps -p $API_PID > /dev/null; then
            echo -e "✅ API 服务器: 运行中 (PID: $API_PID)"
            
            # 获取进程信息
            PROCESS_INFO=$(ps -p $API_PID -o pid,user,%cpu,%mem,etime,command | tail -1)
            echo "   进程信息: $PROCESS_INFO"
        else
            echo -e "❌ API 服务器: PID 文件存在但进程未运行 (PID: $API_PID)"
        fi
    else
        # 尝试查找进程
        API_PIDS=$(ps aux | grep "model_api_server.py" | grep -v grep | awk '{print $2}')
        if [ -n "$API_PIDS" ]; then
            echo -e "⚠️  API 服务器: 运行中但无 PID 文件"
            for pid in $API_PIDS; do
                echo "   进程 PID: $pid"
            done
        else
            echo -e "❌ API 服务器: 未运行"
        fi
    fi
}

# 检查端口占用
check_port_status() {
    print_section "端口状态"
    
    # 检查端口 8191 (管理后台)
    if lsof -i :8191 > /dev/null 2>&1; then
        PORT_INFO=$(lsof -i :8191 | grep LISTEN | head -1)
        echo -e "✅ 端口 8191: 被占用"
        echo "   占用信息: $PORT_INFO"
    else
        echo -e "❌ 端口 8191: 空闲"
    fi
    
    echo ""
    
    # 检查端口 8190 (API 服务器)
    if lsof -i :8190 > /dev/null 2>&1; then
        PORT_INFO=$(lsof -i :8190 | grep LISTEN | head -1)
        echo -e "✅ 端口 8190: 被占用"
        echo "   占用信息: $PORT_INFO"
    else
        echo -e "❌ 端口 8190: 空闲"
    fi
}

# 检查服务健康
check_service_health() {
    print_section "服务健康检查"
    
    # 检查管理后台健康
    echo "检查管理后台健康状态..."
    if curl -s --max-time 5 http://localhost:8191/api/health > /dev/null 2>&1; then
        HEALTH_RESPONSE=$(curl -s http://localhost:8191/api/health)
        STATUS=$(echo $HEALTH_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])")
        VERSION=$(echo $HEALTH_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['version'])")
        
        if [ "$STATUS" = "healthy" ]; then
            echo -e "✅ 管理后台: 健康 (版本: $VERSION)"
        else
            echo -e "⚠️  管理后台: 状态异常 ($STATUS)"
        fi
    else
        echo -e "❌ 管理后台: 无法访问"
    fi
    
    echo ""
    
    # 检查 API 服务器健康
    echo "检查 API 服务器健康状态..."
    if curl -s --max-time 5 http://localhost:8190/health > /dev/null 2>&1; then
        echo -e "✅ API 服务器: 可访问"
    else
        echo -e "❌ API 服务器: 无法访问 (可能未启用)"
    fi
}

# 检查系统资源
check_system_resources() {
    print_section "系统资源"
    
    # 检查内存使用
    MEMORY_USAGE=$(free -m | awk 'NR==2{printf "%.1f%%", $3*100/$2}')
    echo "内存使用: $MEMORY_USAGE"
    
    # 检查 CPU 使用
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    echo "CPU 使用: ${CPU_USAGE}%"
    
    # 检查磁盘空间
    DISK_USAGE=$(df -h / | awk 'NR==2{print $5}')
    echo "磁盘使用: $DISK_USAGE"
    
    echo ""
    
    # 检查技能目录大小
    SKILL_SIZE=$(du -sh . | awk '{print $1}')
    echo "技能目录大小: $SKILL_SIZE"
    
    # 检查日志文件大小
    if [ -d "/Users/a404/.openclaw/workspace/logs" ]; then
        LOG_SIZE=$(du -sh /Users/a404/.openclaw/workspace/logs 2>/dev/null | awk '{print $1}' || echo "N/A")
        echo "日志目录大小: $LOG_SIZE"
    fi
}

# 检查配置文件
check_config_files() {
    print_section "配置文件"
    
    # 检查模型注册表
    if [ -f "/Users/a404/.openclaw/workspace/models_registry.json" ]; then
        MODEL_COUNT=$(cat /Users/a404/.openclaw/workspace/models_registry.json | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('models', [])))" 2>/dev/null || echo "错误")
        echo "模型注册表: 存在 ($MODEL_COUNT 个模型)"
    else
        echo "模型注册表: 不存在"
    fi
    
    # 检查技能配置文件
    CONFIG_FILES=(
        "SKILL.md"
        "SKILL_ENHANCED.md"
        "admin/package.json"
        "admin/server.js"
        "scripts/model_manager_enhanced.py"
    )
    
    echo ""
    echo "技能配置文件:"
    for file in "${CONFIG_FILES[@]}"; do
        if [ -f "$file" ]; then
            SIZE=$(du -h "$file" | awk '{print $1}')
            echo "  ✅ $file ($SIZE)"
        else
            echo "  ❌ $file (缺失)"
        fi
    done
}

# 检查网络连接
check_network_connectivity() {
    print_section "网络连接"
    
    # 检查本地连接
    echo "检查本地连接..."
    if ping -c 1 -W 1 localhost > /dev/null 2>&1; then
        echo -e "✅ 本地网络: 正常"
    else
        echo -e "❌ 本地网络: 异常"
    fi
    
    # 检查外部连接
    echo "检查外部连接..."
    if curl -s --max-time 5 https://api.deepseek.com > /dev/null 2>&1; then
        echo -e "✅ 外部网络: 正常"
    else
        echo -e "⚠️  外部网络: 可能受限"
    fi
}

# 显示汇总信息
show_summary() {
    print_section "状态汇总"
    
    echo "📊 服务状态汇总:"
    echo ""
    
    # 管理后台状态
    if curl -s --max-time 2 http://localhost:8191/api/health > /dev/null 2>&1; then
        echo -e "  🟢 管理后台: 运行正常"
        echo "     地址: http://localhost:8191/admin"
        echo "     API: http://localhost:8191/api"
    else
        echo -e "  🔴 管理后台: 未运行"
    fi
    
    echo ""
    
    # API 服务器状态
    if curl -s --max-time 2 http://localhost:8190/health > /dev/null 2>&1; then
        echo -e "  🟢 API 服务器: 运行正常"
        echo "     地址: http://localhost:8190"
    else
        echo -e "  ⚫ API 服务器: 未启用"
    fi
    
    echo ""
    
    # 系统状态
    echo "  📈 系统状态:"
    echo "     模型数量: $(cat /Users/a404/.openclaw/workspace/models_registry.json 2>/dev/null | python3 -c \"import sys, json; data=json.load(sys.stdin); print(len(data.get('models', [])))\" 2>/dev/null || echo '未知')"
    echo "     技能版本: v3.0.0"
    echo "     运行时间: $(ps -o etime= -p $(cat admin/.admin_pid 2>/dev/null) 2>/dev/null || echo '未知')"
    
    echo ""
    echo "🔧 管理命令:"
    echo "  ./start_all.sh     # 启动所有服务"
    echo "  ./stop_all.sh      # 停止所有服务"
    echo "  ./status.sh        # 查看状态 (当前命令)"
}

# 主函数
main() {
    echo ""
    echo "=========================================="
    echo "   model-auto-switch 技能状态检查 v1.0   "
    echo "=========================================="
    echo ""
    
    # 检查参数
    case "$1" in
        brief|--brief|-b)
            print_section "简要状态"
            check_service_health
            show_summary
            exit 0
            ;;
        help|--help|-h)
            echo "用法: $0 [options]"
            echo ""
            echo "选项:"
            echo "  brief    显示简要状态"
            echo "  help     显示帮助信息"
            echo ""
            exit 0
            ;;
    esac
    
    # 运行所有检查
    check_process_status
    check_port_status
    check_service_health
    check_system_resources
    check_config_files
    check_network_connectivity
    
    # 显示汇总信息
    show_summary
    
    echo ""
    print_success "状态检查完成！"
    echo ""
}

# 运行主函数
main "$@"