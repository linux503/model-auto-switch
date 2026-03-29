#!/bin/bash
echo "🚀 GitHub 代码推送 - 认证助手"
echo "=========================================="

cd /Users/a404/.openclaw/workspace/skills/model-auto-switch

echo "📊 当前状态:"
echo "  仓库: https://github.com/linux503/model-auto-switch"
echo "  本地分支: $(git branch --show-current)"
echo "  最新提交: $(git log -1 --pretty=format:'%h - %s')"
echo ""

echo "🔐 认证选项:"
echo "1. 使用 GitHub Personal Access Token (PAT)"
echo "2. 使用 SSH 密钥 (需要已配置)"
echo "3. 使用 Git 凭据管理器"
echo ""

read -p "请选择认证方式 (1/2/3): " auth_method

case $auth_method in
    1)
        echo ""
        echo "🔑 使用 GitHub Personal Access Token"
        echo "------------------------------------------"
        echo "1. 访问: https://github.com/settings/tokens"
        echo "2. 点击 'Generate new token'"
        echo "3. 选择权限: repo (全部)"
        echo "4. 生成并复制 token"
        echo ""
        read -p "请输入你的 GitHub PAT: " -r github_token
        
        if [[ -n "$github_token" ]]; then
            echo "🔄 使用 PAT 推送..."
            # 使用 PAT 进行推送
            git push https://linux503:${github_token}@github.com/linux503/model-auto-switch.git main
        else
            echo "❌ 未提供 PAT"
            exit 1
        fi
        ;;
        
    2)
        echo ""
        echo "🔑 使用 SSH 密钥"
        echo "------------------------------------------"
        echo "切换为 SSH 方式..."
        git remote set-url origin git@github.com:linux503/model-auto-switch.git
        git push -u origin main
        ;;
        
    3)
        echo ""
        echo "🔑 使用 Git 凭据管理器"
        echo "------------------------------------------"
        echo "尝试标准推送 (会提示输入用户名/密码)..."
        git push -u origin main
        ;;
        
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
if [ $? -eq 0 ]; then
    echo "✅ 推送成功！"
    echo ""
    echo "🎯 下一步:"
    echo "1. 推送标签: git push origin --tags"
    echo "2. 创建 Release: https://github.com/linux503/model-auto-switch/releases/new"
else
    echo "❌ 推送失败"
    echo "请检查认证信息或网络连接"
fi