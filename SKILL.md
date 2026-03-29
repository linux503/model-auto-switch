# model-auto-switch - OpenClaw 模型自动切换与管理技能

## 概述

为 OpenClaw 提供完整的模型自动切换策略和管理系统。当主模型不可用时，自动切换到备用模型，确保服务持续可用。

## 功能特性

### 🚀 核心功能
- **自动故障转移** - 主模型不可用时自动切换到备用模型
- **优先级管理** - 按优先级顺序尝试备用模型
- **状态监控** - 实时监控所有模型状态
- **切换日志** - 记录所有切换操作
- **手动控制** - 支持手动切换、测试、启用/禁用

### 📊 管理界面
- **Web 管理面板** - 可视化界面，实时监控
- **CLI 工具** - 命令行接口，适合脚本集成
- **定时任务** - 自动检测和切换

### 🔧 配置管理
- **模型注册表** - 统一管理所有模型信息
- **优先级设置** - 自定义切换顺序
- **通知机制** - 切换时发送通知（可选）

## 快速开始

### 安装技能
```bash
# 技能已安装在本地
cd /Users/a404/.openclaw/workspace/skills/model-auto-switch
```

### 初始化系统
```bash
# 1. 复制示例配置文件
cp references/models_registry.json.example /Users/a404/.openclaw/workspace/models_registry.json

# 2. 运行初始化检测
python3 scripts/model_manager.py auto
```

### 基本使用
```bash
# 列出所有模型
python3 scripts/model_manager.py list

# 测试当前模型
python3 scripts/model_manager.py test

# 手动切换模型
python3 scripts/model_manager.py switch aicodee/MiniMax-M2.7-highspeed

# 运行自动检测
python3 scripts/model_manager.py auto
```

## 详细使用指南

### 1. 模型注册表管理
模型注册表 (`models_registry.json`) 存储所有模型信息：

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
      "added_at": "2026-03-19T15:57:38Z",
      "notes": "默认备用模型"
    }
  ],
  "switch_log": [],
  "settings": {
    "auto_switch_enabled": true,
    "check_interval_minutes": 5,
    "max_retries": 3,
    "notify_on_switch": true
  }
}
```

### 2. CLI 命令参考

#### 模型管理
```bash
# 列出所有模型
python3 scripts/model_manager.py list

# 显示系统状态
python3 scripts/model_manager.py status

# 测试指定模型
python3 scripts/model_manager.py test aicodee/MiniMax-M2.5-highspeed

# 切换到指定模型
python3 scripts/model_manager.py switch aicodee/MiniMax-M2.7-highspeed

# 启用/禁用模型
python3 scripts/model_manager.py enable M001
python3 scripts/model_manager.py disable M002
```

#### 自动切换
```bash
# 运行自动检测（如果需要则切换）
python3 scripts/model_manager.py auto

# 显示切换日志
python3 scripts/model_manager.py log 20
```

### 3. Web 管理面板
```bash
# 启动本地服务器
cd /Users/a404/.openclaw/workspace
python3 -m http.server 8090

# 访问管理面板
http://127.0.0.1:8090/skills/model-auto-switch/scripts/model_web_dashboard.html
```

### 4. 定时任务配置
```bash
# 编辑 crontab
crontab -e

# 每5分钟运行一次自动检测
*/5 * * * * /Users/a404/.openclaw/workspace/skills/model-auto-switch/scripts/model_auto_switch.sh

# 每天凌晨清理旧日志
0 2 * * * find /Users/a404/.openclaw/workspace/logs -name "*.gz" -mtime +7 -delete
```

## 配置说明

### 模型优先级
- **优先级 1-2**: 主模型和主要备用模型
- **优先级 3-5**: 常用备用模型  
- **优先级 6-10**: 一般备用模型
- **优先级 11+**: 备用模型

### 自动切换设置
```json
{
  "auto_switch_enabled": true,      // 是否启用自动切换
  "check_interval_minutes": 5,      // 检测间隔（分钟）
  "max_retries": 3,                 // 最大重试次数
  "notify_on_switch": true          // 切换时是否通知
}
```

## 集成到 OpenClaw

### 作为技能调用
```bash
# 在 OpenClaw 会话中
使用 model-auto-switch 技能

# 或通过命令
openclaw skill run model-auto-switch --action list
```

### 添加到 HEARTBEAT.md
```markdown
# 每30分钟检查一次模型状态
- 运行模型自动检测: python3 /Users/a404/.openclaw/workspace/skills/model-auto-switch/scripts/model_manager.py auto
```

### 创建快捷命令
在 OpenClaw 配置中添加：
```json
{
  "commands": {
    "custom": {
      "model-status": "python3 /Users/a404/.openclaw/workspace/skills/model-auto-switch/scripts/model_manager.py status",
      "model-switch": "python3 /Users/a404/.openclaw/workspace/skills/model-auto-switch/scripts/model_manager.py switch"
    }
  }
}
```

## 故障排除

### 常见问题

#### 1. 模型测试失败
```bash
# 检查网络连接
ping api.deepseek.com

# 检查 API Key 配置
openclaw config get --path auth.profiles.deepseek:default
```

#### 2. 自动切换不工作
```bash
# 检查日志文件
tail -f /Users/a404/.openclaw/workspace/logs/model_switch.log

# 手动运行检测
python3 scripts/model_manager.py auto --verbose
```

#### 3. Web 面板无法加载
```bash
# 检查 HTTP 服务器
ps aux | grep http.server

# 检查文件权限
ls -la scripts/model_web_dashboard.html
```

### 日志文件
- **主日志**: `/Users/a404/.openclaw/workspace/logs/model_switch.log`
- **自动轮转**: 超过10MB自动压缩
- **保留策略**: 保留最近7天的压缩日志

## 扩展开发

### 添加新功能
1. **通知集成** - 添加 Telegram/Slack 通知
2. **性能监控** - 记录模型响应时间和成功率
3. **智能切换** - 基于历史数据选择最佳模型
4. **多用户支持** - 用户特定的模型偏好

### 代码结构
```
scripts/
├── model_manager.py      # 主管理脚本
├── model_auto_switch.sh  # 自动切换脚本
└── model_web_dashboard.html  # Web 管理界面

references/
└── models_registry.json.example  # 配置文件示例
```

## 增强版特性 (v2.0)

### 🧠 智能切换算法
- **性能评分系统**: 基于响应时间和成功率计算模型评分
- **优先级加权**: 考虑模型优先级和性能数据
- **智能选择**: 自动选择最佳可用模型
- **故障预测**: 基于历史数据预测模型可靠性

### 📊 高级监控
- **实时性能统计**: 响应时间、成功率、测试次数
- **趋势分析**: 性能变化趋势图表
- **模型评分**: 综合评分系统 (0.0-1.0)
- **详细日志**: 完整的操作和错误日志

### 🎨 增强版 Web 面板
- **现代化界面**: 深色主题，响应式设计
- **实时仪表板**: 状态概览、性能图表、最佳模型推荐
- **交互式操作**: 一键测试、切换、启用/禁用
- **多标签页**: 仪表板、模型列表、日志、设置、性能分析
- **可视化图表**: 性能趋势、模型分布、成功率排行

### 🔔 通知集成
- **切换通知**: 模型切换时发送 Telegram 通知
- **故障通知**: 模型不可用时发送警报
- **性能警报**: 性能不达标时发送警告
- **自定义配置**: 可配置通知内容和接收者

### 🔧 系统管理
- **自动备份**: 定期备份注册表数据
- **日志轮转**: 自动清理旧日志
- **设置管理**: 完整的系统设置界面
- **数据导出**: 导出模型列表为 CSV
- **批量操作**: 批量启用/禁用模型

### 🛡️ 可靠性增强
- **错误恢复**: 自动重试和故障恢复
- **数据验证**: 配置文件完整性检查
- **安全备份**: 重要操作前自动备份
- **状态持久化**: 重启后恢复状态

## 🖥️ 后台管理系统 (v3.0)

### 现代化管理界面
- **专业仪表板**: 实时监控、统计概览、最近操作
- **响应式设计**: 支持桌面和移动设备
- **深色主题**: 现代化 UI，保护眼睛
- **实时更新**: WebSocket 实时数据推送

### 完整功能模块
- **📊 仪表板**: 系统概览、实时状态、警告提示
- **🤖 模型管理**: 列表展示、状态管理、一键操作
- **📈 性能分析**: 统计报告、最佳表现者、优化建议
- **📝 系统日志**: 实时查看、级别过滤、搜索功能
- **⚙️ 系统设置**: 配置管理、维护工具、备份恢复
- **🔌 API 管理**: 端点列表、在线测试、文档查看

### 技术特性
- **Node.js 后端**: Express 服务器，RESTful API
- **实时通信**: Socket.io WebSocket 支持
- **现代化前端**: Bootstrap 5 + Vanilla JavaScript
- **完整认证**: 会话管理和权限控制（开发环境可跳过）
- **错误处理**: 完整的错误捕获和用户提示

### 部署选项
1. **本地运行**: `cd admin && ./start.sh`
2. **生产部署**: 配置环境变量，启用 HTTPS
3. **Docker 部署**: 支持容器化部署（计划中）

## 版本历史

### v3.0 (2026-03-29) - 后台管理版
- ✅ 完整的后台管理系统
- ✅ Node.js + Express 服务器
- ✅ 实时 WebSocket 通信
- ✅ 现代化管理界面
- ✅ 完整的 API 文档
- ✅ 一键启动脚本

### v2.0 (2026-03-29) - 增强版
- ✅ 智能自动切换算法
- ✅ 性能统计与评分系统  
- ✅ 增强版 Web 管理面板
- ✅ 通知集成
- ✅ 备份与恢复功能
- ✅ 详细的配置指南

### v1.0 (2026-03-29) - 基础版
- ✅ 基础自动切换功能
- ✅ 简单 Web 管理面板
- ✅ 基本命令行工具
- ✅ 定时任务支持

## 支持与反馈

### 获取帮助
- 查看详细文档: `references/README.md`
- 检查日志文件: `/Users/a404/.openclaw/workspace/logs/model_switch.log`
- 在 OpenClaw 会话中请求帮助

### 报告问题
1. 描述问题现象
2. 提供相关日志
3. 说明复现步骤
4. 期望的行为

---

**技能作者**: OpenClaw 助手  
**最后更新**: 2026-03-29  
**版本**: 1.0