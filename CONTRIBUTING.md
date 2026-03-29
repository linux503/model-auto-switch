# 贡献指南

感谢你考虑为 OpenClaw Model Auto-Switch 项目做出贡献！🎉

## 🎯 如何贡献

### 1. 报告问题
- 使用 [GitHub Issues](https://github.com/yourusername/openclaw-model-auto-switch/issues)
- 描述清晰的问题现象
- 提供复现步骤
- 包含相关日志和截图

### 2. 提交功能请求
- 说明使用场景和价值
- 提供参考实现（可选）
- 讨论技术可行性

### 3. 提交代码
- Fork 仓库并创建分支
- 遵循代码规范
- 添加测试用例
- 提交 Pull Request

## 🛠️ 开发环境设置

### 1. 克隆仓库
```bash
git clone https://github.com/yourusername/openclaw-model-auto-switch.git
cd openclaw-model-auto-switch
```

### 2. 安装依赖
```bash
# Python 依赖
pip install -r requirements.txt

# Node.js 依赖
cd admin
npm install
cd ..
```

### 3. 启动开发服务器
```bash
# 启动后台管理系统（开发模式）
cd admin
npm run dev
```

### 4. 运行测试
```bash
# 运行完整测试
./test_all_features.sh

# 运行 Python 测试
python3 -m pytest tests/ -v

# 运行 API 测试
python3 examples/api_client.py demo
```

## 📝 代码规范

### Python 代码
- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- 使用类型提示
- 添加文档字符串
- 最大行长度：88个字符

```python
def example_function(param1: str, param2: int) -> bool:
    """
    函数说明文档
    
    Args:
        param1: 参数1说明
        param2: 参数2说明
        
    Returns:
        返回值说明
    """
    # 代码实现
    return True
```

### JavaScript 代码
- 使用 ES6+ 语法
- 遵循 Airbnb 风格指南
- 添加 JSDoc 注释
- 使用 async/await

```javascript
/**
 * 函数说明文档
 * @param {string} param1 - 参数1说明
 * @param {number} param2 - 参数2说明
 * @returns {boolean} 返回值说明
 */
async function exampleFunction(param1, param2) {
  // 代码实现
  return true;
}
```

### 提交信息
使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<类型>[可选 范围]: <描述>

[可选 正文]

[可选 脚注]
```

类型包括：
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具

示例：
```
feat: 添加模型预测性维护功能

• 实现故障预测算法
• 添加成本优化分析
• 更新相关文档

Closes #123
```

## 🧪 测试要求

### 单元测试
- 覆盖核心功能
- 测试边界条件
- 模拟外部依赖

### 集成测试
- 测试 API 接口
- 测试数据库操作
- 测试外部服务集成

### 端到端测试
- 测试完整工作流
- 测试用户界面
- 测试性能要求

## 📚 文档要求

### 代码文档
- 所有公共函数都需要文档字符串
- 复杂算法需要详细注释
- 配置项需要说明用途

### 用户文档
- 更新 README.md
- 添加使用示例
- 提供故障排除指南

### API 文档
- 描述所有端点
- 提供请求/响应示例
- 说明认证要求

## 🔍 代码审查

### 审查要点
1. **功能正确性**
   - 是否实现需求
   - 是否有边界情况处理
   - 是否有安全漏洞

2. **代码质量**
   - 是否符合代码规范
   - 是否有重复代码
   - 是否有性能问题

3. **测试覆盖**
   - 是否有单元测试
   - 测试是否充分
   - 测试是否通过

4. **文档完整性**
   - 是否有代码注释
   - 是否有用户文档
   - 是否有 API 文档

### 审查流程
1. 创建 Pull Request
2. 等待 CI 测试通过
3. 至少一名维护者审查
4. 根据反馈修改代码
5. 合并到主分支

## 🏗️ 项目结构

了解项目结构有助于贡献：

```
openclaw-model-auto-switch/
├── scripts/                    # 核心 Python 脚本
│   ├── model_manager_enhanced.py      # 主管理脚本
│   ├── model_predictive_maintenance.py # 预测性维护
│   ├── model_api_server.py            # API 服务器
│   └── model_auto_switch.sh           # 定时任务脚本
├── admin/                      # 后台管理系统
│   ├── server.js              # Node.js 后端
│   ├── public/                # 前端文件
│   │   ├── admin.html         # 主界面
│   │   └── admin.js           # 前端逻辑
│   └── package.json           # Node.js 配置
├── examples/                  # 使用示例
│   ├── api_client.py         # API 客户端
│   └── quick_test.sh         # 快速测试
├── tests/                    # 测试文件
│   ├── test_manager.py       # 管理器测试
│   └── test_api.py           # API 测试
├── docs/                     # 文档
│   ├── INSTALL.md           # 安装指南
│   ├── API.md              # API 文档
│   └── ARCHITECTURE.md      # 架构说明
└── references/              # 参考文件
    └── models_registry.json.example # 配置示例
```

## 🚀 开发工作流

### 1. 规划
- 讨论功能需求
- 设计技术方案
- 评估工作量

### 2. 开发
- 创建功能分支
- 实现核心功能
- 编写测试用例

### 3. 测试
- 运行单元测试
- 进行集成测试
- 验证功能正确性

### 4. 文档
- 更新代码注释
- 编写用户文档
- 更新 API 文档

### 5. 提交
- 提交 Pull Request
- 通过代码审查
- 合并到主分支

## 🤝 行为准则

### 我们的承诺
我们致力于为所有人提供友好、尊重的环境，无论年龄、体型、残疾、种族、性别认同和表达、经验水平、国籍、个人外貌、种族、宗教或性取向如何。

### 我们的标准
促进积极环境的行为包括：
- 使用友好和包容的语言
- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

不可接受的行为包括：
- 使用性化语言或图像，以及不受欢迎的性关注或进展
- 挑衅、侮辱/贬损性评论，以及人身或政治攻击
- 公开或私下骚扰
- 未经明确许可发布他人的私人信息
- 在专业环境中不合理的其他行为

## 📞 获取帮助

### 开发问题
- 查看现有文档
- 搜索 GitHub Issues
- 在 Discord 中提问

### 技术讨论
- 加入技术讨论频道
- 参与设计讨论
- 分享学习经验

###  mentorship
- 寻求导师指导
- 参与结对编程
- 学习项目架构

## 🎉 感谢贡献！

你的每一份贡献都让这个项目变得更好。感谢你花时间阅读这份指南，我们期待看到你的贡献！

---

*这份文档基于 [Contributor Covenant](https://www.contributor-covenant.org) 行为准则。*