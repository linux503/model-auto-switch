#!/bin/bash
# OpenClaw Model Balancer 品牌化脚本

set -e

echo "🎨 OpenClaw Model Balancer 品牌化工具"
echo "=========================================="

cd "$(dirname "$0")"

# 配置
OLD_NAME="model-auto-switch"
NEW_NAME="openclaw-model-balancer"
BRAND_NAME="OpenClaw Model Balancer"
SHORT_NAME="OMB"
VERSION="v4.0.0"

echo "📋 品牌化配置:"
echo "  旧名称: $OLD_NAME"
echo "  新名称: $NEW_NAME"
echo "  品牌名: $BRAND_NAME"
echo "  简称: $SHORT_NAME"
echo "  版本: $VERSION"
echo ""

# 确认
read -p "是否开始品牌化? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 用户取消"
    exit 0
fi

echo "🔍 备份当前状态..."
BACKUP_DIR="../${OLD_NAME}_backup_$(date +%Y%m%d_%H%M%S)"
cp -r . "$BACKUP_DIR"
echo "✅ 备份创建到: $BACKUP_DIR"

echo ""
echo "🔄 开始品牌化..."

# 1. 更新 README.md
echo "📄 更新 README.md..."
if [ -f README_BRANDED.md ]; then
    mv README_BRANDED.md README.md
    echo "✅ README 已品牌化"
else
    echo "⚠️  品牌化 README 不存在，跳过"
fi

# 2. 更新 SKILL.md
echo "📄 更新 SKILL.md..."
if [ -f SKILL.md ]; then
    sed -i '' "s/AI 优化的自动切换模型技能/$BRAND_NAME/g" SKILL.md
    sed -i '' "s/model-auto-switch/$NEW_NAME/g" SKILL.md
    echo "✅ SKILL.md 已更新"
fi

# 3. 更新 package.json
echo "📦 更新 package.json..."
if [ -f admin/package.json ]; then
    sed -i '' "s/\"name\": \".*\"/\"name\": \"$NEW_NAME\"/g" admin/package.json
    sed -i '' "s/\"description\": \".*\"/\"description\": \"$BRAND_NAME - Intelligent AI Model Load Balancing\"/g" admin/package.json
    echo "✅ package.json 已更新"
fi

# 4. 更新配置文件
echo "⚙️  更新配置文件..."
if [ -f config/default.json ]; then
    sed -i '' "s/\"model-auto-switch\"/\"$NEW_NAME\"/g" config/default.json
    echo "✅ 配置文件已更新"
fi

# 5. 更新 Python 脚本中的引用
echo "🐍 更新 Python 脚本..."
find scripts/ -name "*.py" -type f | while read file; do
    if [ -f "$file" ]; then
        sed -i '' "s/model-auto-switch/$NEW_NAME/g" "$file"
        sed -i '' "s/AI 优化的自动切换模型技能/$BRAND_NAME/g" "$file"
    fi
done
echo "✅ Python 脚本已更新"

# 6. 更新 Shell 脚本
echo "🐚 更新 Shell 脚本..."
find tools/ -name "*.sh" -type f | while read file; do
    if [ -f "$file" ]; then
        sed -i '' "s/model-auto-switch/$NEW_NAME/g" "$file"
        sed -i '' "s/AI 优化的自动切换模型技能/$BRAND_NAME/g" "$file"
    fi
done
echo "✅ Shell 脚本已更新"

# 7. 更新文档文件
echo "📚 更新文档文件..."
find docs/ -name "*.md" -type f | while read file; do
    if [ -f "$file" ]; then
        sed -i '' "s/model-auto-switch/$NEW_NAME/g" "$file"
        sed -i '' "s/AI 优化的自动切换模型技能/$BRAND_NAME/g" "$file"
    fi
done
echo "✅ 文档文件已更新"

# 8. 更新 JavaScript 文件
echo "📜 更新 JavaScript 文件..."
if [ -f admin/public/admin.js ]; then
    sed -i '' "s/model-auto-switch/$NEW_NAME/g" admin/public/admin.js
    sed -i '' "s/AI 优化的自动切换模型技能/$BRAND_NAME/g" admin/public/admin.js
    echo "✅ JavaScript 文件已更新"
fi

# 9. 更新 HTML 文件
echo "🌐 更新 HTML 文件..."
find admin/public/ -name "*.html" -type f | while read file; do
    if [ -f "$file" ]; then
        sed -i '' "s/model-auto-switch/$NEW_NAME/g" "$file"
        sed -i '' "s/AI 优化的自动切换模型技能/$BRAND_NAME/g" "$file"
        sed -i '' "s/<title>.*<\/title>/<title>$BRAND_NAME<\/title>/g" "$file"
    fi
done
echo "✅ HTML 文件已更新"

# 10. 更新 server.js
echo "🖥️ 更新 server.js..."
if [ -f admin/server.js ]; then
    sed -i '' "s/model-auto-switch/$NEW_NAME/g" admin/server.js
    sed -i '' "s/AI 优化的自动切换模型技能/$BRAND_NAME/g" admin/server.js
    echo "✅ server.js 已更新"
fi

# 11. 创建品牌标识文件
echo "🎨 创建品牌标识文件..."
cat > BRAND_GUIDELINES.md << EOF
# 🎨 OpenClaw Model Balancer 品牌指南

## 品牌标识
- **全称**: OpenClaw Model Balancer
- **简称**: OMB
- **标语**: Intelligent AI Model Load Balancing for OpenClaw
- **中文名**: OpenClaw 模型负载均衡器

## 品牌颜色
- **主色**: OpenClaw 蓝 (#2D5BFF)
- **辅助色**: 科技蓝 (#4A90E2)
- **强调色**: 成功绿 (#00C853)
- **背景色**: 深灰 (#1A1A1A)

## 品牌字体
- **标题**: Inter Bold
- **正文**: Inter Regular
- **代码**: JetBrains Mono

## 品牌使用规范
1. 在正式文档中使用全称 "OpenClaw Model Balancer"
2. 在代码和配置中使用简称 "OMB"
3. 在界面中显示品牌标语
4. 保持品牌颜色一致性

## 文件命名规范
- 项目目录: \`openclaw-model-balancer\`
- 代码模块: \`omb_\` 前缀
- 配置文件: \`omb.config.\` 前缀
- 文档文件: 包含 "OMB" 标识
EOF
echo "✅ 品牌指南已创建"

# 12. 更新版本文件
echo "🏷️ 更新版本信息..."
cat > VERSION << EOF
$VERSION
$BRAND_NAME
Build: $(date +%Y-%m-%d_%H:%M:%S)
EOF
echo "✅ 版本文件已创建"

echo ""
echo "=========================================="
echo "🎉 品牌化完成！"
echo ""
echo "📋 完成的工作:"
echo "  1. ✅ 更新了 README.md 为品牌化版本"
echo "  2. ✅ 更新了 SKILL.md 和文档"
echo "  3. ✅ 更新了 package.json 配置"
echo "  4. ✅ 更新了所有代码文件引用"
echo "  5. ✅ 更新了配置和脚本文件"
echo "  6. ✅ 创建了品牌指南"
echo "  7. ✅ 创建了版本文件"
echo ""
echo "📁 项目现在使用新名称: $BRAND_NAME ($SHORT_NAME)"
echo "📁 目录名称保持: $OLD_NAME (Git 历史保留)"
echo ""
echo "🚀 下一步操作:"
echo "  1. 测试所有功能是否正常"
echo "  2. 提交更改到 Git"
echo "  3. 更新 GitHub 仓库名称"
echo "  4. 创建新版本标签 $VERSION"
echo ""
echo "🔧 测试命令:"
echo "  ./tools/start_all.sh"
echo "  ./tests/quick_test.py"
echo ""
echo "📤 提交命令:"
echo "  git add ."
echo "  git commit -m \"🎨 品牌化: 重命名为 OpenClaw Model Balancer (OMB)\""
echo "  git tag -a \"$VERSION\" -m \"Release $VERSION - $BRAND_NAME\""
echo "  git push origin main --tags"
echo ""
echo "🌐 GitHub 仓库重命名:"
echo "  访问: https://github.com/linux503/$OLD_NAME/settings"
echo "  修改 Repository name 为: $NEW_NAME"
echo ""
echo "=========================================="
echo "🎨 $BRAND_NAME 品牌化完成！"