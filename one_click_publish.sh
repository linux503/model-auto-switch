#!/bin/bash
# 一键发布脚本 - 最简单版本

set -e

echo "=========================================="
echo "🚀 AI 优化的自动切换模型技能 - 一键发布"
echo "=========================================="
echo ""

# 显示当前状态
echo "📊 当前项目状态:"
echo "  目录: $(pwd)"
echo "  Git 分支: $(git branch --show-current)"
echo "  最新提交: $(git log -1 --pretty=format:'%h - %s')"
echo "  版本标签: v3.1.0"
echo ""

echo "📋 发布前检查:"
echo "------------------------------------------"

# 检查 Git 状态
if ! git status &> /dev/null; then
    echo "❌ 错误: 当前目录不是 Git 仓库"
    exit 1
fi

# 检查未提交的更改
if [[ -n $(git status --porcelain) ]]; then
    echo "⚠️  警告: 有未提交的更改"
    echo "    建议先提交所有更改"
    read -p "    是否继续? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 用户取消"
        exit 0
    fi
else
    echo "✅ 所有更改已提交"
fi

echo ""
echo "=========================================="
echo "📝 发布步骤 (请按顺序执行):"
echo "=========================================="
echo ""

echo "第1步: 🔐 登录 GitHub"
echo "------------------------------------------"
echo "1. 打开浏览器访问: https://github.com/login"
echo "2. 输入你的 GitHub 用户名和密码"
echo "3. 完成登录"
echo ""
read -p "是否已完成 GitHub 登录? (按回车继续) "

echo ""
echo "第2步: 📦 创建 GitHub 仓库"
echo "------------------------------------------"
echo "1. 访问: https://github.com/new"
echo "2. 填写仓库信息:"
echo "   - Repository name: model-auto-switch"
echo "   - Description: AI 优化的自动切换模型技能"
echo "   - 不要勾选 'Initialize this repository with a README'"
echo "3. 点击 'Create repository'"
echo "4. 复制生成的仓库 URL (HTTPS 格式)"
echo ""
read -p "是否已创建仓库并复制了 URL? (按回车继续) "

echo ""
echo "第3步: ⚙️  配置远程仓库"
echo "------------------------------------------"
echo "请输入你的 GitHub 用户名:"
read -r github_username

echo ""
echo "将执行以下命令:"
echo "  git remote add origin https://github.com/${github_username}/model-auto-switch.git"
echo ""
read -p "是否继续? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 用户取消"
    exit 0
fi

# 执行配置
echo "⚙️  配置远程仓库..."
git remote add origin "https://github.com/${github_username}/model-auto-switch.git" 2>/dev/null || {
    echo "⚠️  远程仓库已存在，更新配置..."
    git remote set-url origin "https://github.com/${github_username}/model-auto-switch.git"
}
echo "✅ 远程仓库配置完成"

echo ""
echo "第4步: 📤 推送代码到 GitHub"
echo "------------------------------------------"
echo "将执行以下命令:"
echo "  1. git push -u origin main"
echo "  2. git push origin --tags"
echo ""
read -p "是否开始推送? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 用户取消"
    exit 0
fi

# 执行推送
echo "📤 正在推送代码..."
if git push -u origin main; then
    echo "✅ 代码推送成功"
else
    echo "❌ 代码推送失败"
    echo "尝试强制推送..."
    read -p "是否强制推送? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push -u origin main --force
        echo "✅ 强制推送成功"
    else
        echo "❌ 推送取消"
        exit 1
    fi
fi

echo ""
echo "📤 正在推送标签..."
if git push origin --tags; then
    echo "✅ 标签推送成功"
else
    echo "⚠️  标签推送可能有问题，但可以继续"
fi

echo ""
echo "第5步: 🎉 创建 GitHub Release"
echo "------------------------------------------"
echo "1. 访问: https://github.com/${github_username}/model-auto-switch/releases/new"
echo "2. 选择标签: v3.1.0"
echo "3. 标题: v3.1.0 - AI 优化的自动切换模型技能"
echo "4. 描述: 复制以下文件内容:"
echo "   cat RELEASE_v3.1.0.md | pbcopy"
echo "5. 点击 'Publish release'"
echo ""
echo "📋 发布说明文件: RELEASE_v3.1.0.md"
echo "📖 详细指南: GITHUB_LOGIN_AND_PUBLISH_GUIDE.md"
echo ""

echo "=========================================="
echo "✅ 本地发布步骤完成!"
echo "=========================================="
echo ""
echo "📊 发布状态:"
echo "  ✅ 代码已准备就绪"
echo "  ✅ 文档已完整"
echo "  ✅ 远程仓库已配置"
echo "  🔄 需要手动完成 GitHub 操作"
echo ""
echo "🔗 重要链接:"
echo "  GitHub 仓库: https://github.com/${github_username}/model-auto-switch"
echo "  创建 Release: https://github.com/${github_username}/model-auto-switch/releases/new"
echo "  项目主页: http://localhost:8191/admin (本地)"
echo ""
echo "📞 如需帮助:"
echo "  1. 查看 GITHUB_LOGIN_AND_PUBLISH_GUIDE.md"
echo "  2. 运行 ./final_publish.sh 查看详细步骤"
echo "  3. 联系技术支持"
echo ""
echo "🎉 祝您发布成功!"
echo "=========================================="

# 可选: 自动打开浏览器
read -p "是否打开 GitHub 仓库页面? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    open "https://github.com/${github_username}/model-auto-switch"
fi