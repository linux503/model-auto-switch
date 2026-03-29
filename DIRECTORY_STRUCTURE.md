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
