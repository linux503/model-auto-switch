# OpenClaw 模型自动切换技能 - 安装与配置指南

## 🚀 快速安装

### 一键安装脚本
```bash
cd /Users/a404/.openclaw/workspace/skills/model-auto-switch
chmod +x install.sh
./install.sh
```

### 手动安装步骤
1. **复制配置文件**
   ```bash
   cp references/models_registry.json.example /Users/a404/.openclaw/workspace/models_registry.json
   ```

2. **设置脚本权限**
   ```bash
   chmod +x scripts/*.py scripts/*.sh
   ```

3. **创建日志目录**
   ```bash
   mkdir -p /Users/a404/.openclaw/workspace/logs
   ```

4. **测试安装**
   ```bash
   python3 scripts/model_manager_enhanced.py status
   ```

## 📋 系统要求

### 软件要求
- Python 3.7+
- OpenClaw 2026.3.13+
- Bash shell
- 现代浏览器（Chrome 90+, Firefox 88+, Safari 14+）

### 权限要求
- 对 `/Users/a404/.openclaw/workspace` 的读写权限
- 执行 `openclaw` 命令的权限
- 创建 cron 任务的权限（可选）

## ⚙️ 详细配置

### 1. 模型注册表配置
编辑 `/Users/a404/.openclaw/workspace/models_registry.json`：

```json
{
  "version": "2.0",
  "models": [
    {
      "id": "M001",
      "name": "deepseek/deepseek-chat",
      "provider": "deepseek",
      "status": "active",
      "priority": 3,
      "last_used": null,
      "added_at": "2026-03-19T15:57:38Z",
      "notes": "默认备用模型"
    }
    // 更多模型...
  ],
  "settings": {
    "auto_switch_enabled": true,
    "check_interval_minutes": 5,
    "max_retries": 3,
    "notify_on_switch": true,
    "telegram_chat_id": "telegram:2039643883"
    // 更多设置...
  }
}
```

### 2. 添加新模型
```bash
# 方法1: 手动编辑注册表
# 在 models_registry.json 的 models 数组中添加新条目

# 方法2: 使用脚本（开发中）
python3 scripts/model_manager_enhanced.py add-model --name "provider/model-name" --priority 5
```

### 3. 配置通知
编辑 `models_registry.json` 中的 `settings` 部分：
```json
{
  "notify_on_switch": true,
  "notify_on_failure": true,
  "telegram_chat_id": "telegram:2039643883"
}
```

确保 OpenClaw 已配置 Telegram 插件。

## 🔧 定时任务配置

### 推荐配置
```bash
# 编辑 crontab
crontab -e

# 添加以下行：
# 每5分钟运行自动检测
*/5 * * * * /Users/a404/.openclaw/workspace/skills/model-auto-switch/scripts/model_auto_switch.sh

# 每天凌晨2点清理旧日志
0 2 * * * find /Users/a404/.openclaw/workspace/logs -name "*.gz" -mtime +7 -delete

# 每天凌晨3点备份注册表
0 3 * * * /Users/a404/.openclaw/workspace/skills/model-auto-switch/scripts/model_manager_enhanced.py backup
```

### 定时任务选项
| 间隔 | 命令 | 用途 |
|------|------|------|
| 1分钟 | `*/1 * * * *` | 高频监控 |
| 5分钟 | `*/5 * * * *` | 推荐配置 |
| 15分钟 | `*/15 * * * *` | 低频监控 |
| 每小时 | `0 * * * *` | 定期检查 |
| 每天 | `0 2 * * *` | 维护任务 |

## 🌐 Web 管理面板

### 启动服务
```bash
# 方法1: 使用 Python 内置服务器
cd /Users/a404/.openclaw/workspace
python3 -m http.server 8090

# 方法2: 使用后台进程
cd /Users/a404/.openclaw/workspace
nohup python3 -m http.server 8090 > /dev/null 2>&1 &

# 方法3: 使用系统服务（高级）
# 创建 systemd 服务文件
```

### 访问地址
- **本地访问**: `http://127.0.0.1:8090/skills/model-auto-switch/scripts/model_web_dashboard_enhanced.html`
- **网络访问**: `http://<你的IP>:8090/skills/model-auto-switch/scripts/model_web_dashboard_enhanced.html`

### 安全建议
1. **本地访问**: 只绑定到 127.0.0.1
2. **认证**: 如果需要外部访问，添加 HTTP 基本认证
3. **HTTPS**: 通过反向代理添加 SSL 证书
4. **防火墙**: 限制访问 IP

## 🛠️ 命令行使用

### 基本命令
```bash
# 显示帮助
python3 scripts/model_manager_enhanced.py --help

# 显示仪表板
python3 scripts/model_manager_enhanced.py dashboard

# 列出所有模型
python3 scripts/model_manager_enhanced.py list

# 显示状态
python3 scripts/model_manager_enhanced.py status
```

### 模型操作
```bash
# 测试当前模型
python3 scripts/model_manager_enhanced.py test

# 测试指定模型
python3 scripts/model_manager_enhanced.py test aicodee/MiniMax-M2.5-highspeed

# 切换到指定模型
python3 scripts/model_manager_enhanced.py switch aicodee/MiniMax-M2.7-highspeed

# 启用/禁用模型
python3 scripts/model_manager_enhanced.py enable M001
python3 scripts/model_manager_enhanced.py disable M002
```

### 自动切换
```bash
# 运行一次自动检测
python3 scripts/model_manager_enhanced.py auto

# 显示切换日志
python3 scripts/model_manager_enhanced.py log 20

# 发送测试通知
python3 scripts/model_manager_enhanced.py notify "测试消息"
```

### 系统管理
```bash
# 备份注册表
python3 scripts/model_manager_enhanced.py backup

# 导出模型列表
python3 scripts/model_manager_enhanced.py export-models

# 重置性能统计
python3 scripts/model_manager_enhanced.py reset-stats
```

## 🔍 故障排除

### 常见问题

#### 1. 脚本无法执行
```bash
# 检查权限
ls -la scripts/model_manager_enhanced.py

# 添加执行权限
chmod +x scripts/model_manager_enhanced.py

# 检查 Python 版本
python3 --version
```

#### 2. 无法连接到 OpenClaw
```bash
# 检查 OpenClaw 状态
openclaw status

# 检查配置文件
openclaw config get --path agents.defaults.model.primary

# 测试 OpenClaw 命令
openclaw session-status
```

#### 3. Web 面板无法加载
```bash
# 检查 HTTP 服务器
ps aux | grep http.server

# 检查端口占用
lsof -i :8090

# 重启服务器
pkill -f "http.server"
cd /Users/a404/.openclaw/workspace && python3 -m http.server 8090 &
```

#### 4. 定时任务不运行
```bash
# 检查 crontab
crontab -l

# 手动测试脚本
/Users/a404/.openclaw/workspace/skills/model-auto-switch/scripts/model_auto_switch.sh

# 检查日志
tail -f /Users/a404/.openclaw/workspace/logs/model_switch.log
```

#### 5. 通知不发送
```bash
# 检查 Telegram 配置
openclaw config get --path plugins.entries.telegram

# 测试消息发送
openclaw message send --channel telegram --to telegram:2039643883 --message "测试"

# 检查通知设置
grep "notify_on_switch" /Users/a404/.openclaw/workspace/models_registry.json
```

### 日志文件
- **主日志**: `/Users/a404/.openclaw/workspace/logs/model_switch.log`
- **错误日志**: 查看控制台输出
- **Web 日志**: 浏览器开发者工具控制台

### 调试模式
```bash
# 启用详细输出
python3 scripts/model_manager_enhanced.py --verbose auto

# 查看调试信息
tail -f /Users/a404/.openclaw/workspace/logs/model_switch.log | grep -i "debug\|error"
```

## 🔄 升级与维护

### 备份策略
1. **自动备份**: 每天自动备份注册表
2. **手动备份**: 重要操作前手动备份
3. **版本控制**: 考虑使用 git 管理配置

### 升级步骤
```bash
# 1. 备份当前配置
cp /Users/a404/.openclaw/workspace/models_registry.json /tmp/models_registry_backup.json

# 2. 更新技能文件
cd /Users/a404/.openclaw/workspace/skills/model-auto-switch
git pull  # 如果使用 git

# 3. 运行升级脚本（如果有）
./upgrade.sh

# 4. 测试新版本
python3 scripts/model_manager_enhanced.py status
```

### 数据清理
```bash
# 清理旧日志（保留7天）
find /Users/a404/.openclaw/workspace/logs -name "*.gz" -mtime +7 -delete

# 清理旧备份（保留30天）
find /Users/a404/.openclaw/workspace/backups -name "*.json" -mtime +30 -delete

# 重置性能统计（谨慎操作）
python3 scripts/model_manager_enhanced.py reset-stats --confirm
```

## 📊 性能优化

### 推荐配置
```json
{
  "check_interval_minutes": 5,
  "max_retries": 3,
  "test_timeout_seconds": 15,
  "max_response_time_ms": 30000,
  "performance_weight_response_time": 0.4,
  "performance_weight_success_rate": 0.6
}
```

### 监控建议
1. **响应时间**: 关注 >3000ms 的模型
2. **成功率**: 关注 <70% 的模型  
3. **切换频率**: 关注频繁切换的模型
4. **资源使用**: 监控 CPU 和内存使用

## 🤝 贡献与支持

### 报告问题
1. 描述问题现象
2. 提供相关日志
3. 说明复现步骤
4. 期望的行为

### 功能建议
1. 描述使用场景
2. 说明价值
3. 提供参考实现（可选）

### 获取帮助
- 查看文档: `README.md` 和 `SKILL.md`
- 检查日志: `/Users/a404/.openclaw/workspace/logs/model_switch.log`
- 在 OpenClaw 会话中请求帮助

## 📝 版本历史

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

---

**安装完成！** 现在你可以：
1. 访问 Web 管理面板
2. 配置定时任务
3. 开始使用自动切换功能

如有问题，请参考故障排除部分或请求帮助。