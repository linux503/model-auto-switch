# 🚀 openclaw-model-balancer - OpenClaw 企业级模型自动切换与管理平台

<div align="center">

![版本](https://img.shields.io/badge/版本-v3.0.0-blue)
![状态](https://img.shields.io/badge/状态-生产就绪-green)
![许可证](https://img.shields.io/badge/许可证-MIT-yellow)

**智能 AI 模型管理 · 高可用性保障 · 企业级解决方案**

</div>

## 🎯 概述

**openclaw-model-balancer** 是一个完整的企业级 AI 模型自动切换和管理平台，为 OpenClaw 提供智能的模型故障转移、性能优化和集中管理功能。确保 AI 服务的高可用性和稳定性。

## ✨ 核心功能

### 🧠 智能切换引擎
- **多维度评分**: 响应时间 + 成功率 = 综合评分
- **优先级管理**: 结合配置优先级和实际性能
- **成本优化**: 考虑模型使用成本的经济性选择
- **预测性维护**: 基于历史数据预测模型故障

### 📊 高级监控
- **实时仪表板**: WebSocket 驱动的实时数据
- **性能趋势分析**: 可视化性能变化
- **健康状态监控**: 模型可用性和响应时间
- **自动告警**: 性能下降或故障时自动通知

### 🏢 企业级特性
- **集中管理**: 统一的模型注册表和配置
- **完整监控**: 实时仪表板、性能图表、日志系统
- **API 驱动**: RESTful API 支持系统集成
- **安全认证**: 完整的会话管理和权限控制

## 🚀 快速开始

### 安装和启动
```bash
# 进入技能目录
cd /Users/a404/.openclaw/workspace/skills/openclaw-model-balancer

# 启动管理后台
cd admin && ./start.sh

# 访问管理界面
# 地址: http://localhost:8191/admin
```

### 基本使用
```bash
# 查看系统状态
python3 scripts/model_manager_enhanced.py status

# 列出所有模型
python3 scripts/model_manager_enhanced.py list

# 测试模型
python3 scripts/model_manager_enhanced.py test M001

# 切换模型
python3 scripts/model_manager_enhanced.py switch M002
```

## 🖥️ 管理后台

### 访问地址
- **管理界面**: http://localhost:8191/admin
- **API 文档**: http://localhost:8191/api
- **WebSocket**: ws://localhost:8191

### 功能模块
1. **📊 仪表板** - 系统概览和实时状态
2. **🤖 模型管理** - 所有模型列表和操作
3. **📈 性能分析** - 性能报告和趋势图表
4. **📝 系统日志** - 实时日志查看和搜索
5. **⚙️ 系统设置** - 配置管理和维护工具
6. **🔌 API 管理** - API 测试和文档

## 🔧 配置指南

### 模型注册表
配置文件: `/Users/a404/.openclaw/workspace/models_registry.json`

```json
{
  "models": [
    {
      "id": "M001",
      "name": "deepseek/deepseek-chat",
      "provider": "deepseek",
      "status": "active",
      "priority": 3,
      "last_used": "2026-03-29T09:49:00Z",
      "notes": "默认备用模型"
    }
  ],
  "settings": {
    "auto_switch_enabled": true,
    "check_interval_minutes": 5,
    "max_retries": 3
  }
}
```

## 📚 API 文档

### 基础端点
- `GET /api/health` - 健康检查
- `GET /api/models` - 获取模型列表
- `POST /api/models/switch` - 切换模型
- `GET /api/performance` - 获取性能报告

### 示例使用
```bash
# 健康检查
curl http://localhost:8191/api/health

# 获取模型列表
curl http://localhost:8191/api/models

# 切换模型
curl -X POST http://localhost:8191/api/models/switch \
  -H "Content-Type: application/json" \
  -d '{"modelId": "M001", "reason": "manual"}'
```

## 🔍 故障排除

### 常见问题

#### 1. 管理后台无法访问
```bash
# 检查服务器状态
ps aux | grep "node server.js"

# 重启服务器
cd admin && pkill -f "node server.js" && ./start.sh
```

#### 2. 模型切换失败
```bash
# 检查模型注册表
cat /Users/a404/.openclaw/workspace/models_registry.json | jq '.models'

# 测试模型连通性
python3 scripts/model_manager_enhanced.py test M001 --verbose
```

#### 3. 查看日志
```bash
# 实时查看日志
tail -f /Users/a404/.openclaw/workspace/logs/model_switch.log

# 搜索错误日志
grep -i "error" /Users/a404/.openclaw/workspace/logs/model_switch.log
```

## 📈 性能指标

| 指标 | 目标值 | 状态 |
|------|--------|------|
| **服务可用性** | > 99.9% | ✅ |
| **平均响应时间** | < 2000ms | ✅ |
| **模型切换成功率** | > 99% | ✅ |
| **API 响应时间** | < 100ms | ✅ |

## 🤝 贡献指南

### 开发流程
1. 创建功能分支
2. 编写测试用例
3. 实现功能代码
4. 运行测试套件
5. 提交代码审查

### 代码规范
- 遵循 PEP 8 (Python)
- 遵循 Airbnb 规范 (JavaScript)
- 添加文档字符串
- 编写单元测试

## 📄 许可证

本项目采用 MIT 许可证。有关完整许可证文本，请参阅 [LICENSE](LICENSE) 文件。

## 📞 支持与联系

- **GitHub Issues**: 问题报告和功能请求
- **文档**: 本项目 README 和 SKILL_ENHANCED.md
- **社区**: OpenClaw Discord 社区

---

<div align="center">

**感谢使用 openclaw-model-balancer！** 🚀

如果这个项目对你有帮助，请考虑：
- ⭐ 给项目点个星
- 🐛 报告问题
- 💡 提出功能建议
- 🔧 贡献代码

**让 AI 服务更可靠，一起构建更好的未来！**

</div>