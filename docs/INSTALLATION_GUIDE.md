# 🔧 OpenClaw Model Balancer 安装指南

## 📋 系统要求

### 基础要求
- **操作系统**: macOS, Linux, Windows (WSL2)
- **Python**: 3.7 或更高版本
- **Node.js**: 14.x 或更高版本
- **OpenClaw**: 已安装并运行

### 推荐配置
- **内存**: 4GB RAM 或更高
- **存储**: 1GB 可用空间
- **网络**: 稳定的互联网连接

## 🚀 快速安装

### 方法一：作为 OpenClaw 技能安装（推荐）

#### 步骤 1: 检查 OpenClaw 状态
```bash
# 检查 OpenClaw 是否运行
openclaw status

# 如果未运行，启动 OpenClaw
openclaw gateway start
```

#### 步骤 2: 复制技能到 OpenClaw 目录
```bash
# 复制项目到 OpenClaw 技能目录
cp -r /Users/a404/.openclaw/workspace/skills/model-auto-switch ~/.openclaw/skills/

# 验证复制成功
ls -la ~/.openclaw/skills/model-auto-switch/
```

#### 步骤 3: 重启 OpenClaw 加载技能
```bash
# 重启 OpenClaw 网关
openclaw gateway restart

# 等待重启完成（约10秒）
sleep 10

# 检查状态
openclaw status
```

#### 步骤 4: 安装依赖并启动
```bash
# 进入项目目录
cd ~/.openclaw/skills/model-auto-switch

# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Node.js 依赖
cd admin && npm install

# 返回项目根目录
cd ..

# 启动管理后台
./tools/start_all.sh
```

### 方法二：独立安装

#### 步骤 1: 克隆仓库
```bash
# 克隆 GitHub 仓库
git clone https://github.com/linux503/openclaw-model-balancer.git
cd openclaw-model-balancer
```

#### 步骤 2: 安装依赖
```bash
# 创建 Python 虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Node.js 依赖
cd admin && npm install
cd ..
```

#### 步骤 3: 配置环境
```bash
# 复制示例配置文件
cp config/default.json config/local.json

# 编辑配置文件（可选）
# nano config/local.json
```

#### 步骤 4: 启动系统
```bash
# 启动所有服务
./tools/start_all.sh

# 或手动启动各个组件
# 启动 API 服务器
python scripts/core/model_api_server.py &

# 启动管理后台
cd admin && npm start &
```

## 🔧 配置说明

### 主要配置文件
```json
// config/default.json
{
  "server": {
    "port": 8191,
    "host": "localhost",
    "debug": false
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
```

### 环境变量配置
```bash
# 设置环境变量（可选）
export OMB_PORT=8191
export OMB_HOST=localhost
export OMB_DEBUG=false

# 在启动前设置
./tools/start_all.sh
```

## 🧪 验证安装

### 检查服务状态
```bash
# 使用状态检查脚本
./tools/status.sh

# 或手动检查
curl http://localhost:8191/health
curl http://localhost:8191/api/models
```

### 访问管理界面
1. 打开浏览器
2. 访问: http://localhost:8191/admin
3. 应该看到 OMB 管理仪表板

### 测试 API
```bash
# 测试基本 API
curl http://localhost:8191/api/models/current
curl http://localhost:8191/api/models/list

# 使用 Python 客户端测试
python docs/examples/api_client.py
```

## 🐳 Docker 安装（可选）

### 构建 Docker 镜像
```bash
# 构建镜像
docker build -t openclaw-model-balancer .

# 或使用预构建镜像
docker pull linux503/openclaw-model-balancer:latest
```

### 运行 Docker 容器
```bash
# 运行容器
docker run -d \
  -p 8191:8191 \
  --name omb \
  -v ~/.openclaw/workspace:/data \
  openclaw-model-balancer

# 查看日志
docker logs -f omb
```

## 🔄 更新升级

### 更新代码
```bash
# 进入项目目录
cd ~/.openclaw/skills/model-auto-switch

# 拉取最新代码（如果使用 Git）
git pull origin main

# 更新依赖
pip install -r requirements.txt --upgrade
cd admin && npm update
cd ..

# 重启服务
./tools/stop_all.sh
./tools/start_all.sh
```

### 数据迁移
```bash
# 备份现有数据
cp /Users/a404/.openclaw/workspace/models_registry.json /backup/models_registry_backup.json

# 运行数据迁移脚本（如果有）
python scripts/core/model_manager.py migrate
```

## 🛠️ 故障排除

### 常见问题

#### 1. 端口冲突
```bash
# 检查端口占用
lsof -i :8191

# 停止占用进程或修改端口
# 编辑 config/local.json 修改端口
```

#### 2. 依赖安装失败
```bash
# 更新 pip
pip install --upgrade pip

# 使用国内镜像源（中国用户）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 3. Node.js 版本问题
```bash
# 检查 Node.js 版本
node --version

# 如果版本过低，使用 nvm 升级
nvm install 14
nvm use 14
```

#### 4. 权限问题
```bash
# 确保有读写权限
chmod +x tools/*.sh
chmod +x scripts/core/*.py
```

### 获取帮助
- **GitHub Issues**: https://github.com/linux503/openclaw-model-balancer/issues
- **文档**: 查看 docs/ 目录下的详细文档
- **社区**: OpenClaw Discord 社区

## 📊 安装后操作

### 1. 配置模型注册表
```bash
# 查看当前模型
python scripts/core/model_manager.py list

# 添加新模型
python scripts/core/model_manager.py add --name "gpt-4" --provider "openai" --priority 5
```

### 2. 设置定时任务
```bash
# 添加定时优化任务
(crontab -l 2>/dev/null; echo "*/30 * * * * cd /Users/a404/.openclaw/skills/model-auto-switch && python scripts/core/model_manager.py auto") | crontab -
```

### 3. 集成到工作流
```python
# 在 Python 代码中使用
from docs.examples.api_client import ModelAPIClient

client = ModelAPIClient("http://localhost:8191")
best_model = client.get_best_model()
print(f"推荐模型: {best_model}")
```

## 🎉 安装完成！

### 验证清单
- [ ] 管理界面可访问: http://localhost:8191/admin
- [ ] API 响应正常: `curl http://localhost:8191/health`
- [ ] 模型列表可查看: `python scripts/core/model_manager.py list`
- [ ] 定时任务已设置（可选）
- [ ] 数据备份已配置（可选）

### 下一步
1. 阅读 [用户指南](USER_GUIDE.md) 了解详细功能
2. 查看 [API 文档](API_REFERENCE.md) 学习如何集成
3. 加入社区获取支持和更新

---

**需要帮助？** 访问我们的 [GitHub 仓库](https://github.com/linux503/openclaw-model-balancer) 或联系 [SkillBox.lol](https://skillbox.lol/)