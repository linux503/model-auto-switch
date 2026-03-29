#!/bin/bash

# OpenClaw Model Auto-Switch - GitHub发布脚本
# 版本: v3.0.0
# 作者: OpenClaw Community

set -e  # 遇到错误时退出

echo "🚀 OpenClaw Model Auto-Switch GitHub发布脚本"
echo "=========================================="

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

# 函数：检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "命令 '$1' 未安装"
        exit 1
    fi
}

# 函数：检查Git状态
check_git_status() {
    if [ ! -d ".git" ]; then
        print_error "当前目录不是Git仓库"
        exit 1
    fi
    
    # 检查是否有未提交的更改
    if [[ -n $(git status --porcelain) ]]; then
        print_warning "有未提交的更改"
        read -p "是否继续？(y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "发布取消"
            exit 0
        fi
    fi
}

# 函数：检查GitHub CLI状态
check_gh_status() {
    if ! gh auth status &> /dev/null; then
        print_error "GitHub CLI未登录"
        echo "请运行: gh auth login"
        exit 1
    fi
}

# 函数：创建GitHub仓库
create_github_repo() {
    local repo_name="openclaw-openclaw-model-balancer"
    
    print_info "检查GitHub仓库是否存在..."
    
    if gh repo view $repo_name &> /dev/null; then
        print_warning "仓库 '$repo_name' 已存在"
        read -p "是否继续使用现有仓库？(y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "请手动处理现有仓库"
            exit 1
        fi
    else
        print_info "创建GitHub仓库: $repo_name"
        
        gh repo create $repo_name \
            --public \
            --description "Enterprise-grade AI model auto-switching and management platform for OpenClaw" \
            --homepage "https://openclaw.ai" \
            --license "MIT" \
            --push \
            --source=. \
            --remote=origin
            
        if [ $? -eq 0 ]; then
            print_success "GitHub仓库创建成功"
        else
            print_error "GitHub仓库创建失败"
            exit 1
        fi
    fi
}

# 函数：推送代码到GitHub
push_to_github() {
    print_info "推送代码到GitHub..."
    
    # 添加所有文件
    git add .
    
    # 提交更改
    git commit -m "feat: initial release v3.0.0" || {
        print_warning "没有新的更改需要提交"
    }
    
    # 推送到GitHub
    git push -u origin main
    
    if [ $? -eq 0 ]; then
        print_success "代码推送成功"
    else
        print_error "代码推送失败"
        exit 1
    fi
}

# 函数：创建Git标签
create_git_tag() {
    local version="v3.0.0"
    
    print_info "创建Git标签: $version"
    
    # 检查标签是否已存在
    if git tag -l | grep -q "^$version$"; then
        print_warning "标签 '$version' 已存在"
        read -p "是否删除并重新创建？(y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git tag -d $version
            git push origin --delete $version
        else
            return 0
        fi
    fi
    
    # 创建标签
    git tag -a $version -m "OpenClaw Model Auto-Switch $version"
    git push origin $version
    
    if [ $? -eq 0 ]; then
        print_success "Git标签创建成功"
    else
        print_error "Git标签创建失败"
        exit 1
    fi
}

# 函数：创建GitHub Release
create_github_release() {
    local version="v3.0.0"
    
    print_info "创建GitHub Release: $version"
    
    # 检查Release是否已存在
    if gh release view $version &> /dev/null; then
        print_warning "Release '$version' 已存在"
        read -p "是否删除并重新创建？(y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            gh release delete $version --yes
        else
            return 0
        fi
    fi
    
    # 创建Release
    gh release create $version \
        --title "OpenClaw Model Auto-Switch $version" \
        --notes-file GITHUB_RELEASE_SUMMARY.md \
        --target main
    
    if [ $? -eq 0 ]; then
        print_success "GitHub Release创建成功"
    else
        print_error "GitHub Release创建失败"
        exit 1
    fi
}

# 函数：创建ZIP包
create_zip_package() {
    local version="v3.0.0"
    local zip_file="openclaw-openclaw-model-balancer-$version.zip"
    
    print_info "创建ZIP包: $zip_file"
    
    # 排除不需要的文件
    zip -r $zip_file . \
        -x "*.git*" \
        -x "admin/node_modules/*" \
        -x "*.DS_Store" \
        -x "*.log" \
        -x "*.tmp" \
        -x "*.swp" \
        -x "*~" \
        -x "publish_to_github.sh"
    
    if [ $? -eq 0 ]; then
        print_success "ZIP包创建成功"
        echo "文件大小: $(du -h $zip_file | cut -f1)"
    else
        print_error "ZIP包创建失败"
        exit 1
    fi
}

# 函数：上传Release资产
upload_release_assets() {
    local version="v3.0.0"
    local zip_file="openclaw-openclaw-model-balancer-$version.zip"
    
    if [ ! -f "$zip_file" ]; then
        print_warning "ZIP包不存在，跳过上传"
        return 0
    fi
    
    print_info "上传Release资产: $zip_file"
    
    gh release upload $version $zip_file
    
    if [ $? -eq 0 ]; then
        print_success "Release资产上传成功"
        # 清理临时文件
        rm -f $zip_file
    else
        print_error "Release资产上传失败"
        print_warning "ZIP包保留在: $zip_file"
    fi
}

# 函数：显示发布总结
show_release_summary() {
    local repo_name="openclaw-openclaw-model-balancer"
    local version="v3.0.0"
    
    echo ""
    echo "🎉 发布完成！"
    echo "=========================================="
    echo "📦 项目名称: $repo_name"
    echo "🏷️  版本: $version"
    echo "🌐 GitHub地址: https://github.com/$(gh api user | jq -r '.login')/$repo_name"
    echo "📄 Release地址: https://github.com/$(gh api user | jq -r '.login')/$repo_name/releases/tag/$version"
    echo ""
    echo "📋 下一步操作:"
    echo "1. 访问GitHub仓库检查发布结果"
    echo "2. 更新项目描述和标签"
    echo "3. 在社区分享项目链接"
    echo "4. 监控Issues和Pull Requests"
    echo ""
    echo "💡 提示: 运行以下命令查看仓库:"
    echo "  gh repo view $repo_name --web"
    echo ""
}

# 主函数
main() {
    echo ""
    print_info "开始发布 OpenClaw Model Auto-Switch v3.0.0"
    echo ""
    
    # 检查必要命令
    print_info "检查系统依赖..."
    check_command git
    check_command gh
    check_command zip
    check_command jq
    
    # 检查Git状态
    print_info "检查Git状态..."
    check_git_status
    
    # 检查GitHub CLI状态
    print_info "检查GitHub CLI状态..."
    check_gh_status
    
    # 创建GitHub仓库
    create_github_repo
    
    # 推送代码到GitHub
    push_to_github
    
    # 创建Git标签
    create_git_tag
    
    # 创建GitHub Release
    create_github_release
    
    # 创建ZIP包
    create_zip_package
    
    # 上传Release资产
    upload_release_assets
    
    # 显示发布总结
    show_release_summary
    
    print_success "发布流程完成！"
}

# 运行主函数
main "$@"