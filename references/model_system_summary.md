# OpenClaw 模型管理系统 - 系统说明

## 系统架构

### 1. 核心组件
- **模型注册表** (`models_registry.json`)
  - 记录所有模型信息（ID、名称、状态、优先级等）
  - 存储切换日志
  - 保存系统设置

- **模型管理器** (`model_manager.py`)
  - Python 脚本，提供 CLI 接口
  - 功能：检测、切换、测试、管理模型
  - 支持自动切换策略

- **自动切换脚本** (`model_auto_switch.sh`)
  - Shell 脚本，适合 cron 任务
  - 定期运行模型检测
  - 日志轮转管理

- **Web 管理面板** (`model_web_dashboard.html`)
  - 可视化界面
  - 实时监控模型状态
  - 支持手动操作

### 2. 数据流
```
用户操作/定时任务 → model_manager.py → OpenClaw 配置
        ↓
models_registry.json (记录状态和日志)
        ↓
Web 面板 (可视化展示)
```

## 功能特性

### 自动切换策略
1. **定期检测**：可配置检测间隔（默认5分钟）
2. **故障转移**：主模型不可用时自动切换到备用模型
3. **优先级排序**：按优先级顺序尝试备用模型
4. **状态记录**：记录每次切换的原因和时间

### 模型管理
1. **统一注册**：每个模型有唯一 ID 和详细元数据
2. **状态控制**：可启用/禁用特定模型
3. **优先级设置**：数字越小优先级越高
4. **使用统计**：记录最后使用时间

### 监控与告警
1. **实时状态**：Web 面板显示当前模型和备用模型状态
2. **切换日志**：记录所有切换操作（成功/失败）
3. **通知机制**：切换时可发送通知（需配置）

## 使用方法

### CLI 命令
```bash
# 列出所有模型
python3 scripts/model_manager.py list

# 测试当前模型
python3 scripts/model_manager.py test

# 测试指定模型
python3 scripts/model_manager.py test aicodee/MiniMax-M2.5-highspeed

# 切换到指定模型
python3 scripts/model_manager.py switch aicodee/MiniMax-M2.7-highspeed

# 运行自动检测
python3 scripts/model_manager.py auto

# 显示切换日志
python3 scripts/model_manager.py log 20

# 启用/禁用模型
python3 scripts/model_manager.py enable M001
python3 scripts/model_manager.py disable M002

# 显示系统状态
python3 scripts/model_manager.py status
```

### 定时任务配置
```bash
# 编辑 crontab
crontab -e

# 每5分钟运行一次自动检测
*/5 * * * * /Users/a404/.openclaw/workspace/scripts/model_auto_switch.sh

# 每天凌晨清理旧日志
0 2 * * * find /Users/a404/.openclaw/workspace/logs -name "*.gz" -mtime +7 -delete
```

### Web 面板访问
```bash
# 启动本地服务器
cd /Users/a404/.openclaw/workspace
python3 -m http.server 8090

# 访问地址
http://127.0.0.1:8090/scripts/model_web_dashboard.html
```

## 配置说明

### 模型注册表结构
```json
{
  "models": [
    {
      "id": "M001",                    // 唯一标识符
      "name": "deepseek/deepseek-chat", // 完整模型名称
      "provider": "deepseek",          // 提供商
      "model_id": "deepseek-chat",     // 模型ID
      "added_at": "2026-03-19T15:57:38Z", // 添加时间
      "status": "active",              // 状态: active/disabled
      "last_used": "2026-03-29T09:49:00Z", // 最后使用时间
      "priority": 3,                   // 优先级（数字越小优先级越高）
      "notes": "默认备用模型"           // 备注
    }
  ],
  "switch_log": [
    {
      "timestamp": "2026-03-29T18:04:30Z",
      "from": "deepseek/deepseek-chat",
      "to": "aicodee/MiniMax-M2.5-highspeed",
      "reason": "配置更新",
      "success": true
    }
  ],
  "settings": {
    "auto_switch_enabled": true,       // 是否启用自动切换
    "check_interval_minutes": 5,       // 检测间隔（分钟）
    "max_retries": 3,                  // 最大重试次数
    "notify_on_switch": true,          // 切换时是否通知
    "default_priority_order": "priority_asc" // 优先级排序方式
  }
}
```

### 优先级规则
1. **优先级 1-2**：主模型和主要备用模型
2. **优先级 3-5**：常用备用模型
3. **优先级 6-10**：一般备用模型
4. **优先级 11+**：备用模型

## 故障排除

### 常见问题
1. **模型测试失败**
   - 检查 API Key 是否有效
   - 检查网络连接
   - 确认模型名称正确

2. **自动切换不工作**
   - 检查 `auto_switch_enabled` 设置
   - 查看日志文件 `/Users/a404/.openclaw/workspace/logs/model_switch.log`
   - 确认 cron 任务正常运行

3. **Web 面板无法加载**
   - 确认 HTTP 服务器已启动
   - 检查文件路径是否正确
   - 查看浏览器控制台错误

### 日志文件
- **主日志**: `/Users/a404/.openclaw/workspace/logs/model_switch.log`
- **自动轮转**: 超过10MB自动压缩
- **保留策略**: 保留最近7天的压缩日志

## 扩展建议

### 1. 集成通知
```python
# 在 model_manager.py 中集成 Telegram 通知
def send_telegram_notification(message):
    subprocess.run([
        "openclaw", "message", "send",
        "--channel", "telegram",
        "--to", "telegram:2039643883",
        "--message", f"模型切换通知: {message}"
    ])
```

### 2. 性能监控
- 记录模型响应时间
- 统计成功率
- 预测模型可用性

### 3. 智能切换
- 基于历史成功率选择模型
- 考虑 API 成本
- 时间敏感切换（高峰时段使用稳定模型）

### 4. 多用户支持
- 用户特定的模型偏好
- 权限管理
- 使用配额

## 安全考虑
1. **API Key 保护**: 注册表中只存储模型名称，不存储 API Key
2. **访问控制**: Web 面板建议本地访问或添加认证
3. **日志脱敏**: 日志中不记录敏感信息
4. **输入验证**: 所有用户输入都经过验证

## 维护计划
1. **每日**: 检查日志文件大小
2. **每周**: 验证所有模型状态
3. **每月**: 清理旧日志和优化注册表
4. **每季度**: 评估和调整优先级设置

---

**最后更新**: 2026-03-29  
**版本**: 1.0  
**作者**: OpenClaw 助手