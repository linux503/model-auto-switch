# OpenClaw Model Auto-Switch Admin

OpenClaw 模型自动切换系统的现代化后台管理界面。

## 🚀 功能特性

### 📊 仪表板
- 实时系统状态监控
- 模型统计概览
- 最近操作记录
- 系统警告提示

### 🤖 模型管理
- 完整的模型列表展示
- 模型状态管理（启用/禁用）
- 一键测试和切换
- 模型详情查看
- 添加新模型

### 📈 性能分析
- 整体性能统计
- 最佳表现者排行
- 需要关注的模型
- 优化建议

### 📝 系统日志
- 实时日志查看
- 按级别过滤（信息/警告/错误）
- 日志搜索功能
- 自动滚动

### ⚙️ 系统设置
- 自动切换配置
- 通知设置
- 系统维护功能
- 备份和恢复

### 🔌 API 管理
- 完整的 API 端点列表
- 在线 API 测试工具
- 实时 WebSocket 连接

## 🛠️ 技术栈

- **后端**: Node.js + Express
- **前端**: Bootstrap 5 + Vanilla JavaScript
- **实时通信**: Socket.io
- **图表**: Chart.js
- **样式**: Material Design Icons + Bootstrap Icons

## 🚀 快速开始

### 1. 安装依赖
```bash
cd admin
npm install
```

### 2. 启动服务器
```bash
# 使用启动脚本
./start.sh

# 或直接使用 npm
npm start
```

### 3. 访问管理界面
打开浏览器访问：http://localhost:8191/admin

## 📁 项目结构

```
admin/
├── package.json          # 项目依赖
├── server.js            # 主服务器文件
├── start.sh             # 启动脚本
├── README.md            # 本文档
├── public/              # 静态文件
│   ├── admin.html       # 主界面
│   ├── admin.js         # 前端逻辑
│   └── (其他静态资源)
└── node_modules/        # 依赖包
```

## 🔧 配置

### 环境变量
```bash
# 服务器端口（默认: 8191）
PORT=8191

# 工作空间路径（默认: /Users/a404/.openclaw/workspace）
WORKSPACE_PATH=/path/to/workspace

# 运行环境（development/production）
NODE_ENV=development
```

### 配置文件
后台管理系统会自动读取以下配置文件：
- `/Users/a404/.openclaw/workspace/models_registry.json` - 模型注册表
- `/Users/a404/.openclaw/workspace/logs/model_switch.log` - 系统日志

## 🔌 API 接口

### 主要端点

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/api/system/info` | 系统信息 |
| GET | `/api/models` | 获取模型列表 |
| POST | `/api/models/switch` | 切换模型 |
| POST | `/api/models/test` | 测试模型 |
| GET | `/api/performance` | 性能报告 |
| GET | `/api/logs` | 系统日志 |
| POST | `/api/auto-switch/run` | 运行自动切换 |
| GET | `/api/settings` | 获取设置 |
| POST | `/api/settings/update` | 更新设置 |
| POST | `/api/backup` | 创建备份 |

### WebSocket 事件

| 事件 | 描述 |
|------|------|
| `connect` | 连接建立 |
| `disconnect` | 连接断开 |
| `system-status` | 系统状态更新 |
| `model-switched` | 模型切换通知 |
| `model-tested` | 模型测试结果 |
| `auto-switch-run` | 自动切换执行 |
| `settings-updated` | 设置更新通知 |

## 🎨 界面截图

### 仪表板
![仪表板](https://via.placeholder.com/800x400/4361ee/ffffff?text=Dashboard)

### 模型管理
![模型管理](https://via.placeholder.com/800x400/3a0ca3/ffffff?text=Model+Management)

### 性能分析
![性能分析](https://via.placeholder.com/800x400/4cc9f0/000000?text=Performance+Analysis)

## 🔒 安全性

### 开发环境
- 默认跳过认证
- 仅限本地访问
- 简单的会话管理

### 生产环境建议
1. 启用认证系统
2. 配置 HTTPS
3. 设置访问控制
4. 定期备份数据
5. 监控系统日志

## 🐛 故障排除

### 常见问题

#### 1. 端口被占用
```bash
# 查看占用进程
lsof -i :8191

# 停止进程
kill -9 <PID>
```

#### 2. 依赖安装失败
```bash
# 清理缓存并重试
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

#### 3. 无法连接到 OpenClaw
确保 OpenClaw 正在运行：
```bash
openclaw status
```

#### 4. WebSocket 连接失败
检查防火墙设置，确保端口 8191 可访问。

### 日志位置
- 服务器日志: 控制台输出
- 应用日志: `/Users/a404/.openclaw/workspace/logs/model_switch.log`
- 错误日志: 浏览器开发者工具控制台

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

如有问题，请：
1. 查看本文档
2. 检查日志文件
3. 提交 Issue
4. 联系维护者

---

**Happy Managing!** 🚀