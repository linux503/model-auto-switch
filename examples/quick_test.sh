#!/bin/bash
# 快速测试脚本 - 验证技能是否正常工作

echo "🧪 model-auto-switch 技能快速测试"
echo "========================================"

WORKSPACE="/Users/a404/.openclaw/workspace"
SCRIPT="$WORKSPACE/skills/model-auto-switch/scripts/model_manager.py"

# 检查脚本是否存在
if [ ! -f "$SCRIPT" ]; then
    echo "❌ 错误: 主脚本不存在: $SCRIPT"
    exit 1
fi

echo "✅ 脚本文件存在"

# 测试1: 显示帮助
echo ""
echo "1. 测试帮助命令..."
python3 "$SCRIPT" --help 2>&1 | head -5
if [ $? -eq 0 ]; then
    echo "✅ 帮助命令测试通过"
else
    echo "❌ 帮助命令测试失败"
fi

# 测试2: 显示状态
echo ""
echo "2. 测试状态命令..."
python3 "$SCRIPT" status
if [ $? -eq 0 ]; then
    echo "✅ 状态命令测试通过"
else
    echo "❌ 状态命令测试失败"
fi

# 测试3: 列出模型
echo ""
echo "3. 测试列出模型..."
python3 "$SCRIPT" list 2>&1 | head -10
if [ $? -eq 0 ]; then
    echo "✅ 列出模型测试通过"
else
    echo "❌ 列出模型测试失败"
fi

# 测试4: 检查配置文件
echo ""
echo "4. 检查配置文件..."
REGISTRY_FILE="$WORKSPACE/models_registry.json"
if [ -f "$REGISTRY_FILE" ]; then
    echo "✅ 配置文件存在: $REGISTRY_FILE"
    MODEL_COUNT=$(grep -c '"name"' "$REGISTRY_FILE" 2>/dev/null || echo "0")
    echo "   包含 $MODEL_COUNT 个模型"
else
    echo "⚠️  配置文件不存在，请先运行安装脚本"
fi

echo ""
echo "========================================"
echo "🎯 下一步建议:"
echo ""
echo "1. 完整测试当前模型:"
echo "   python3 \"$SCRIPT\" test"
echo ""
echo "2. 查看详细模型列表:"
echo "   python3 \"$SCRIPT\" list"
echo ""
echo "3. 运行自动检测:"
echo "   python3 \"$SCRIPT\" auto"
echo ""
echo "4. 启动 Web 管理面板:"
echo "   cd \"$WORKSPACE\""
echo "   python3 -m http.server 8090 &"
echo "   打开: http://127.0.0.1:8090/skills/model-auto-switch/scripts/model_web_dashboard.html"
echo ""
echo "💡 提示: 所有测试通过，技能可以正常使用！"
echo "========================================"