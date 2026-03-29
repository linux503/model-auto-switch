# openclaw-model-balancer 用户指南

## 🚀 快速开始

### 1. 启动服务
```bash
cd /Users/a404/.openclaw/workspace/skills/openclaw-model-balancer
./start_all.sh
```

### 2. 访问管理后台
- **管理界面**: http://localhost:8191/admin
- **API 文档**: http://localhost:8191/api
- **WebSocket**: ws://localhost:8191

### 3. 查看服务状态
```bash
./status.sh
```

## 📊 核心功能使用

### 1. 查看当前模型
**管理后台**: 仪表板显示当前使用的模型
**API**: `GET /api/models` 返回当前模型信息

### 2. 查看所有模型
**管理后台**: "模型管理"标签页显示所有模型
**API**: `GET /api/models` 返回完整模型列表

### 3. 查看模型使用数据
**管理后台**: "使用统计"标签页显示使用数据
**API**: `GET /api/models/usage` 返回使用统计

### 4. 自动切换模型
系统会自动检测模型状态并切换到最佳可用模型

## 🖥️ 管理后台使用指南

### 仪表板
- **系统概览**: 总模型数、活跃模型数
- **当前模型**: 显示注册表和OpenClaw当前模型
- **一致性检查**: 自动检查模型一致性
- **实时状态**: WebSocket驱动的实时更新

### 模型管理
1. **查看模型列表**: 所有模型的详细信息
2. **测试模型**: 点击"测试"按钮验证模型可用性
3. **切换模型**: 手动切换到指定模型
4. **启用/禁用**: 控制模型的使用状态

### 使用统计
1. **总体统计**: 总请求数、平均成功率、平均响应时间
2. **模型排行**: 按使用次数排序的模型列表
3. **详细数据**: 每个模型的详细使用统计
4. **数据导出**: 导出CSV格式的使用数据

### 性能分析
- **性能报告**: 详细的性能统计
- **趋势分析**: 性能变化趋势图表
- **优化建议**: 基于数据的优化建议

### 系统日志
- **实时查看**: 实时日志查看器
- **级别过滤**: 按级别过滤日志
- **搜索功能**: 全文搜索日志内容

### 系统设置
- **基本设置**: 自动切换、检测间隔等
- **通知设置**: 告警通知配置
- **维护工具**: 备份、恢复、清理工具

## 🔧 API 使用指南

### 基础端点
```bash
# 健康检查
curl http://localhost:8191/api/health

# 获取模型列表
curl http://localhost:8191/api/models

# 获取使用统计
curl http://localhost:8191/api/models/usage

# 测试模型
curl -X POST http://localhost:8191/api/models/test \
  -H "Content-Type: application/json" \
  -d '{"modelId": "M001"}'

# 切换模型
curl -X POST http://localhost:8191/api/models/switch \
  -H "Content-Type: application/json" \
  -d '{"modelId": "M001", "reason": "manual"}'

# 记录模型使用
curl -X POST http://localhost:8191/api/models/usage \
  -H "Content-Type: application/json" \
  -d '{"modelId": "M001", "responseTime": 1200, "success": true}'
```

### WebSocket 实时通信
```javascript
// 连接WebSocket
const socket = io('ws://localhost:8191');

// 监听事件
socket.on('system-status', (data) => {
    console.log('系统状态更新:', data);
});

socket.on('models-data', (data) => {
    console.log('模型数据更新:', data);
});

socket.on('model-switched', (data) => {
    console.log('模型切换事件:', data);
});

// 发送请求
socket.emit('request-system-status');
socket.emit('request-models');
```

## 🛠️ 运维管理

### 服务管理
```bash
# 启动所有服务
./start_all.sh

# 停止所有服务
./stop_all.sh

# 重启所有服务
./start_all.sh restart

# 查看服务状态
./status.sh
```

### 监控和告警
1. **健康检查**: 定期检查服务状态
2. **性能监控**: 监控响应时间和成功率
3. **错误告警**: 检测并通知系统错误
4. **资源监控**: 监控系统资源使用情况

### 数据备份
```bash
# 备份模型注册表
cp /Users/a404/.openclaw/workspace/models_registry.json ./backup/

# 备份使用数据
cp /Users/a404/.openclaw/workspace/logs/model_usage.json ./backup/
```

## 🔍 故障排除

### 常见问题

#### 1. 管理后台无法访问
```bash
# 检查服务状态
./status.sh

# 重启服务
./stop_all.sh && ./start_all.sh

# 检查端口占用
lsof -i :8191
```

#### 2. 模型切换失败
```bash
# 检查模型注册表
cat /Users/a404/.openclaw/workspace/models_registry.json | jq '.models'

# 测试模型连通性
python3 scripts/model_manager_enhanced.py test M001

# 查看日志
tail -f /Users/a404/.openclaw/workspace/logs/model_switch.log
```

#### 3. WebSocket 连接问题
```bash
# 测试WebSocket连接
open http://localhost:8191/websocket_test.html

# 检查服务器日志
tail -f admin/server.log
```

#### 4. 使用数据不显示
```bash
# 检查使用数据文件
ls -la /Users/a404/.openclaw/workspace/logs/model_usage.json

# 测试API端点
curl http://localhost:8191/api/models/usage
```

### 日志分析
```bash
# 查看实时日志
tail -f /Users/a404/.openclaw/workspace/logs/model_switch.log

# 搜索错误日志
grep -i "error" /Users/a404/.openclaw/workspace/logs/model_switch.log

# 搜索特定模型日志
grep "M001" /Users/a404/.openclaw/workspace/logs/model_switch.log
```

## 📈 最佳实践

### 1. 模型配置
- **优先级设置**: 根据模型性能设置优先级
- **启用状态**: 只启用稳定可用的模型
- **测试频率**: 定期测试模型可用性

### 2. 自动切换策略
- **检测间隔**: 设置合理的检测间隔（建议5-10分钟）
- **切换阈值**: 设置适当的切换阈值
- **回退策略**: 配置合理的回退机制

### 3. 监控告警
- **关键指标**: 监控成功率、响应时间、可用性
- **告警阈值**: 设置合理的告警阈值
- **通知渠道**: 配置多种通知渠道

### 4. 数据管理
- **定期备份**: 定期备份重要数据
- **数据清理**: 定期清理旧数据
- **数据分析**: 定期分析使用数据

## 🎯 高级功能

### 1. 智能切换算法
系统使用多维度评分算法：
- **响应时间权重**: 40%
- **成功率权重**: 60%
- **优先级加权**: 结合配置优先级
- **成本优化**: 考虑模型使用成本

### 2. 预测性维护
- **性能趋势分析**: 预测模型性能变化
- **故障预测**: 基于历史数据预测故障
- **预防性切换**: 在故障前切换到备用模型

### 3. 成本优化
- **成本分析**: 分析模型使用成本
- **效益评估**: 评估性能与成本的平衡
- **优化建议**: 提供成本优化建议

## 🔮 扩展和集成

### 1. API 集成
```python
# Python 客户端示例
import requests

class ModelSwitchClient:
    def __init__(self, base_url="http://localhost:8191"):
        self.base_url = base_url
    
    def get_models(self):
        response = requests.get(f"{self.base_url}/api/models")
        return response.json()
    
    def switch_model(self, model_id, reason="manual"):
        data = {"modelId": model_id, "reason": reason}
        response = requests.post(f"{self.base_url}/api/models/switch", json=data)
        return response.json()
```

### 2. Webhook 集成
```bash
# 配置Webhook接收切换通知
curl -X POST http://localhost:8191/api/settings \
  -H "Content-Type: application/json" \
  -d '{"webhook_url": "https://your-webhook-url"}'
```

### 3. 通知渠道
- **Telegram**: 发送切换通知到Telegram
- **Email**: 发送邮件通知
- **Slack**: 发送Slack消息
- **Webhook**: 自定义Webhook通知

## 📚 学习资源

### 文档
- **SKILL_ENHANCED.md**: 完整技术文档
- **SKILL.md**: 简洁版技能说明
- **USER_GUIDE.md**: 用户指南（本文档）
- **API文档**: http://localhost:8191/api

### 示例
- **测试页面**: http://localhost:8191/test.html
- **诊断页面**: http://localhost:8191/diagnose.html
- **WebSocket测试**: http://localhost:8191/websocket_test.html

### 社区支持
- **OpenClaw Discord**: 社区讨论和支持
- **GitHub Issues**: 问题报告和功能请求
- **文档反馈**: 文档改进建议

## 🎉 开始使用！

### 第一步：启动服务
```bash
cd /Users/a404/.openclaw/workspace/skills/openclaw-model-balancer
./start_all.sh
```

### 第二步：访问管理后台
打开浏览器访问：http://localhost:8191/admin

### 第三步：配置模型
1. 检查模型列表
2. 测试模型可用性
3. 设置模型优先级
4. 启用自动切换

### 第四步：监控和优化
1. 查看使用统计
2. 分析性能数据
3. 优化切换策略
4. 设置告警通知

---

**祝您使用愉快！** 🚀

如果有任何问题或建议，请随时联系我们。

**最后更新**: 2026-03-29  
**版本**: 1.0  
**技能版本**: v3.0.0