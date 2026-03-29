#!/bin/bash
# 项目清理和整理脚本

set -e

echo "🧹 开始清理和整理项目结构..."
echo "=========================================="

cd "$(dirname "$0")"

# 1. 创建新的目录结构
echo "📁 创建新的目录结构..."
mkdir -p docs
mkdir -p src
mkdir -p scripts/core
mkdir -p scripts/tools
mkdir -p tests
mkdir -p examples
mkdir -p config
mkdir -p tools

# 2. 移动文档文件到 docs/
echo "📄 整理文档文件..."
mv -f AI_OPTIMIZATION_COMPLETED.md docs/
mv -f AI_OPTIMIZATION_TEST_REPORT.md docs/
mv -f AUTO_SWITCH_OPTIMIZATION_PLAN.md docs/
mv -f ENHANCEMENT_PLAN.md docs/
mv -f FINAL_IMPROVEMENT_SUMMARY.md docs/
mv -f FINAL_RELEASE_SUMMARY.md docs/
mv -f FINAL_SUMMARY.md docs/
mv -f GITHUB_LOGIN_AND_PUBLISH_GUIDE.md docs/
mv -f GITHUB_RELEASE_CHECKLIST.md docs/
mv -f GITHUB_RELEASE_GUIDE.md docs/
mv -f GITHUB_RELEASE_INSTRUCTIONS.md docs/
mv -f GITHUB_RELEASE_SUMMARY.md docs/
mv -f IMPROVEMENT_CHECKLIST.md docs/
mv -f LOW_PRIORITY_MODELS_REMOVAL.md docs/
mv -f OPTIMIZATION_SUMMARY.md docs/
mv -f RELEASE_v3.1.0.md docs/
mv -f SIMPLE_LOGIN_GUIDE.md docs/
mv -f SMART_SWITCH_TEST_REPORT.md docs/
mv -f USER_GUIDE.md docs/
mv -f SKILL_ENHANCED.md docs/

# 保留核心文档在根目录
# README.md, SKILL.md, CHANGELOG.md, CONTRIBUTING.md, INSTALL.md, LICENSE 保留

# 3. 移动脚本文件
echo "🐍 整理 Python 脚本..."
mv -f scripts/model_ai_optimizer.py scripts/core/
mv -f scripts/model_manager_enhanced.py scripts/core/model_manager.py
mv -f scripts/model_predictive_maintenance.py scripts/core/
mv -f scripts/model_api_server.py scripts/core/

# 4. 移动测试文件
echo "🧪 整理测试文件..."
mv -f test_all_models.py tests/
mv -f test_auto_switch.py tests/
mv -f test_failover_scenario.py tests/
mv -f quick_model_test.py tests/quick_test.py

# 5. 移动工具脚本
echo "🔧 整理工具脚本..."
mv -f final_publish.sh tools/
mv -f one_click_publish.sh tools/
mv -f publish_to_github.sh tools/
mv -f push_with_auth.sh tools/
mv -f safe_publish_to_github.sh tools/
mv -f COPY_PASTE_COMMANDS.sh tools/
mv -f start_all.sh tools/
mv -f status.sh tools/
mv -f stop_all.sh tools/
mv -f test_all_features.sh tools/

# 6. 清理重复的 JavaScript 文件
echo "🧹 清理重复的 JavaScript 文件..."
# 保留 admin_simple.js 作为主要文件，删除其他版本
cd admin/public
rm -f admin_complete.js admin_fixed.js admin_new.js debug.js
# 重命名 admin_simple.js 为 admin.js (如果不存在)
if [ ! -f admin.js ]; then
    mv admin_simple.js admin.js 2>/dev/null || true
fi
cd ../..

# 7. 清理重复的 HTML 测试文件
echo "🧹 清理重复的 HTML 测试文件..."
cd admin/public
# 只保留主要文件，删除测试页面
rm -f diagnose.html final_test.html page_preview.html test.html websocket_test.html
cd ../..

# 8. 清理旧的脚本文件
echo "🧹 清理旧的脚本文件..."
rm -f scripts/model_manager.py scripts/model_manager_fixed.py
rm -f scripts/model_auto_switch.sh
rm -f scripts/model_web_dashboard.html scripts/model_web_dashboard_enhanced.html scripts/model_web_dashboard_enhanced.js

# 9. 清理旧的测试文件
echo "🧹 清理旧的测试文件..."
rm -f test_websocket_fixed.py test_websocket_simple.js

# 10. 更新文件引用
echo "🔄 更新文件引用..."
# 更新 admin/server.js 中的引用
if [ -f admin/server.js ]; then
    sed -i '' 's/admin_simple\.js/admin.js/g' admin/server.js 2>/dev/null || true
fi

# 11. 创建配置文件
echo "⚙️  创建配置文件..."
cat > config/default.json << 'EOF'
{
  "server": {
    "port": 8191,
    "host": "localhost"
  },
  "models": {
    "registry_path": "/Users/a404/.openclaw/workspace/models_registry.json",
    "performance_db": "/Users/a404/.openclaw/workspace/logs/model_performance.json"
  },
  "ai_optimization": {
    "weights": {
      "response_time": 0.3,
      "success_rate": 0.4,
      "cost_efficiency": 0.1,
      "stability": 0.1,
      "priority": 0.1
    },
    "time_sensitive": true
  }
}
EOF

# 12. 创建目录说明文件
echo "📋 创建目录说明文件..."
cat > DIRECTORY_STRUCTURE.md << 'EOF'
# 📁 项目目录结构

## 根目录
- `README.md` - 项目主文档
- `SKILL.md` - 技能功能说明
- `CHANGELOG.md` - 版本变更日志
- `CONTRIBUTING.md` - 贡献指南
- `INSTALL.md` - 安装指南
- `LICENSE` - 许可证文件
- `package.json` - Node.js 包配置
- `DIRECTORY_STRUCTURE.md` - 本文件

## 主要目录

### 📄 docs/ - 文档目录
- 技术文档、用户指南、发布说明等
- 所有 `.md` 文档文件都放在这里

### 🐍 src/ - 源代码目录
- 核心业务逻辑代码
- 模块化的 Python/JavaScript 代码

### 🔧 scripts/ - 脚本目录
- `core/` - 核心脚本 (模型管理、AI优化等)
- `tools/` - 工具脚本 (发布、测试、维护等)

### 🧪 tests/ - 测试目录
- 单元测试、集成测试、性能测试
- 测试脚本和测试数据

### 🎯 examples/ - 示例目录
- 使用示例和代码片段
- API 调用示例

### ⚙️ config/ - 配置目录
- 配置文件和环境配置
- 默认配置和示例配置

### 🖥️ admin/ - 管理后台
- Web 管理界面
- API 服务器和前端代码

### 🛠️ tools/ - 工具目录
- 开发工具和实用脚本
- 构建、部署、维护脚本

## 文件命名规范

### Python 脚本
- 核心功能: `module_name.py`
- 工具脚本: `tool_name.py`
- 测试脚本: `test_module_name.py`

### Shell 脚本
- 功能脚本: `function_name.sh`
- 工具脚本: `tool_name.sh`
- 部署脚本: `deploy_*.sh`

### 文档文件
- 技术文档: `topic_name.md`
- 用户指南: `guide_name.md`
- 发布说明: `release_vX.Y.Z.md`

## Git 忽略规则
- 临时文件、缓存文件、日志文件
- 敏感配置文件 (使用 .env 或环境变量)
- 构建产物和依赖目录
EOF

# 13. 创建 .gitignore 更新
echo "📝 更新 .gitignore..."
cat >> .gitignore << 'EOF'

# 项目整理后忽略规则
config/local.json
config/secrets.json
*.log
logs/
tmp/
temp/
*.tmp
*.temp
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
.DS_Store
Thumbs.db
EOF

# 14. 验证整理结果
echo "✅ 整理完成！验证结果..."
echo ""
echo "📁 新的目录结构:"
find . -type f -name "*.md" -o -name "*.py" -o -name "*.js" -o -name "*.html" -o -name "*.sh" -o -name "*.json" | grep -v node_modules | sort | head -30

echo ""
echo "📊 文件统计:"
echo "  文档文件: $(find docs -name "*.md" | wc -l) 个"
echo "  Python 脚本: $(find scripts -name "*.py" | wc -l) 个"
echo "  测试文件: $(find tests -name "*.py" | wc -l) 个"
echo "  工具脚本: $(find tools -name "*.sh" | wc -l) 个"

echo ""
echo "=========================================="
echo "🎉 项目整理完成！"
echo ""
echo "📋 主要变化:"
echo "  1. 创建了清晰的目录结构"
echo "  2. 删除了重复和临时文件"
echo "  3. 统一了文件命名规范"
echo "  4. 更新了配置和文档"
echo ""
echo "🚀 下一步: 提交更改到 Git"