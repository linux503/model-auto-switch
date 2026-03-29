# model-auto-switch 技能增强计划

## 🎯 基于用户反馈的优化目标

### 核心需求确认
1. ✅ **检查当前使用的模型** - 已实现
2. ✅ **查看所有模型** - 已实现  
3. ✅ **查看模型提问数据** - 需要增强
4. ✅ **自动切换可用模型** - 已实现

## 📋 优化任务清单

### 第一阶段：立即修复 (今天完成)

#### 1. 🔧 **修复 WebSocket 连接问题**
- [ ] 修复 WebSocket 测试脚本语法错误
- [ ] 增强 WebSocket 连接稳定性
- [ ] 添加连接重试机制
- [ ] 优化心跳检测

#### 2. 📊 **增强模型数据统计**
- [ ] 添加模型使用次数统计
- [ ] 记录模型提问数据
- [ ] 显示模型性能历史
- [ ] 添加使用趋势图表

#### 3. 🔍 **改进模型一致性检查**
- [ ] 更精确的模型名称匹配
- [ ] 添加手动同步功能
- [ ] 显示不一致原因
- [ ] 提供修复建议

### 第二阶段：功能增强 (本周内完成)

#### 1. 📈 **模型使用分析**
- [ ] 提问次数统计
- [ ] 响应时间分析
- [ ] 成功率统计
- [ ] 成本分析

#### 2. 🤖 **智能切换优化**
- [ ] 基于历史数据的智能选择
- [ ] 时间敏感优化策略
- [ ] 成本效益分析
- [ ] 预测性切换

#### 3. 🎨 **用户体验改进**
- [ ] 更直观的数据可视化
- [ ] 一键操作优化
- [ ] 移动端适配改进
- [ ] 错误提示友好化

### 第三阶段：企业级功能 (下阶段)

#### 1. 🏢 **多用户支持**
- [ ] 用户权限管理
- [ ] 个人模型偏好
- [ ] 使用配额管理
- [ ] 审计日志

#### 2. 🔐 **安全增强**
- [ ] 生产环境认证
- [ ] API 访问控制
- [ ] 数据加密
- [ ] 安全审计

#### 3. 📡 **集成扩展**
- [ ] Webhook 支持
- [ ] 更多通知渠道
- [ ] 第三方集成
- [ ] 插件系统

## 🚀 立即执行的任务

### 任务 1: 修复 WebSocket 连接
```javascript
// 修复后的 WebSocket 测试脚本
const testWebSocket = async () => {
    try {
        const ws = new WebSocket('ws://localhost:8191');
        ws.onopen = () => {
            console.log('WebSocket 连接成功');
            ws.send(JSON.stringify({ type: 'ping' }));
        };
        ws.onmessage = (event) => {
            console.log('收到消息:', event.data);
        };
        ws.onerror = (error) => {
            console.error('WebSocket 错误:', error);
        };
    } catch (error) {
        console.error('WebSocket 连接异常:', error);
    }
};
```

### 任务 2: 添加模型使用统计
```python
# 模型使用统计功能
class ModelUsageTracker:
    def __init__(self):
        self.usage_data = {}
    
    def record_usage(self, model_id, response_time, success):
        """记录模型使用情况"""
        if model_id not in self.usage_data:
            self.usage_data[model_id] = {
                'total_requests': 0,
                'successful_requests': 0,
                'total_response_time': 0,
                'last_used': None
            }
        
        data = self.usage_data[model_id]
        data['total_requests'] += 1
        data['total_response_time'] += response_time
        data['last_used'] = datetime.now()
        
        if success:
            data['successful_requests'] += 1
    
    def get_stats(self, model_id):
        """获取模型统计信息"""
        if model_id in self.usage_data:
            data = self.usage_data[model_id]
            return {
                'total_requests': data['total_requests'],
                'success_rate': data['successful_requests'] / data['total_requests'] if data['total_requests'] > 0 else 0,
                'avg_response_time': data['total_response_time'] / data['total_requests'] if data['total_requests'] > 0 else 0,
                'last_used': data['last_used']
            }
        return None
```

### 任务 3: 增强模型一致性检查
```javascript
// 增强的模型一致性检查
function checkModelConsistency(registryModel, openclawModel) {
    const results = {
        consistent: false,
        reason: '',
        suggestions: []
    };
    
    if (!registryModel || !openclawModel || openclawModel === 'None') {
        results.reason = '模型信息不完整';
        results.suggestions = ['检查模型配置', '运行模型扫描'];
        return results;
    }
    
    // 标准化模型名称
    const normalize = (name) => {
        return name.toLowerCase()
            .replace(/[\/\-_]/g, '')
            .replace(/\s+/g, '');
    };
    
    const normRegistry = normalize(registryModel);
    const normOpenclaw = normalize(openclawModel);
    
    // 检查匹配
    if (normRegistry === normOpenclaw) {
        results.consistent = true;
        results.reason = '模型完全匹配';
    } else if (normRegistry.includes(normOpenclaw) || normOpenclaw.includes(normRegistry)) {
        results.consistent = true;
        results.reason = '模型部分匹配';
        results.suggestions = ['模型名称可能有变体'];
    } else {
        results.reason = '模型不匹配';
        results.suggestions = [
            '检查OpenClaw配置',
            '手动同步模型',
            '运行自动检测'
        ];
    }
    
    return results;
}
```

## 📊 进度跟踪

### 今日完成 (2026-03-29)
- [x] 修复 API 返回当前模型信息
- [x] 添加 OpenClaw 实际模型显示
- [x] 创建模型一致性检查
- [x] 更新管理后台界面
- [x] 创建完整的测试套件

### 今日剩余任务
- [ ] 修复 WebSocket 测试脚本
- [ ] 添加模型使用统计 API
- [ ] 更新管理后台显示使用数据
- [ ] 创建使用数据导出功能

## 🎯 成功标准

### 技术标准
- ✅ WebSocket 连接成功率 > 99%
- ✅ API 响应时间 < 100ms
- ✅ 数据一致性检查准确率 > 95%
- ✅ 系统可用性 > 99.9%

### 功能标准
- ✅ 实时显示当前使用模型
- ✅ 完整模型列表和状态
- ✅ 模型使用数据统计
- ✅ 智能自动切换
- ✅ 友好的管理界面

### 用户体验标准
- ✅ 操作简单直观
- ✅ 错误提示清晰
- ✅ 响应迅速
- ✅ 数据可视化良好

## 🔧 技术实现细节

### 数据存储优化
```json
{
  "model_usage": {
    "M001": {
      "total_requests": 150,
      "successful_requests": 148,
      "total_response_time_ms": 180000,
      "last_10_responses": [1200, 1100, 1300, ...],
      "cost_analysis": {
        "estimated_cost": 0.15,
        "cost_per_request": 0.001
      }
    }
  }
}
```

### API 扩展
```
GET /api/models/usage/:modelId
GET /api/models/stats
GET /api/models/trends
POST /api/models/sync
```

### 前端增强
- 使用 Chart.js 显示使用趋势
- 实时更新使用统计数据
- 交互式数据过滤
- 导出功能

## 📞 用户反馈收集

### 需要确认的问题
1. 模型使用数据的具体需求？
2. 是否需要实时提问数据流？
3. 自动切换的敏感度偏好？
4. 其他功能需求？

### 建议的改进
1. 添加模型性能评分系统
2. 创建模型健康报告
3. 添加批量操作功能
4. 支持模型分组

## 🚀 下一步行动

### 立即执行
1. 修复 WebSocket 连接问题
2. 部署增强的 API 端点
3. 更新管理后台界面
4. 测试所有新功能

### 短期计划
1. 收集用户反馈
2. 优化性能
3. 添加更多可视化
4. 完善文档

### 长期愿景
1. 建立完整的模型生态系统
2. 支持更多 AI 平台
3. 创建社区版本
4. 提供企业级支持

---

**最后更新**: 2026-03-29  
**状态**: 进行中  
**优先级**: 高