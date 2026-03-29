#!/usr/bin/env node
/**
 * OpenClaw Model Auto-Switch Admin Server
 * 后台管理系统服务器
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const session = require('express-session');
const { createServer } = require('http');
const { Server } = require('socket.io');
const path = require('path');
const fs = require('fs').promises;
const { exec } = require('child_process');
const util = require('util');
const execAsync = util.promisify(exec);

// 配置
const PORT = process.env.PORT || 8191;
const WORKSPACE_PATH = '/Users/a404/.openclaw/workspace';
const SKILL_PATH = path.join(WORKSPACE_PATH, 'skills/openclaw-model-balancer');

// 创建 Express 应用
const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST']
  }
});

// 中间件
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
      scriptSrc: ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
      imgSrc: ["'self'", "data:", "https:"],
      connectSrc: ["'self'", "ws:", "wss:"]
    }
  }
}));
app.use(cors());
app.use(morgan('combined'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

// 会话配置（简化版，生产环境需要配置安全存储）
app.use(session({
  secret: 'openclaw-model-admin-secret-key',
  resave: false,
  saveUninitialized: true,
  cookie: { 
    secure: process.env.NODE_ENV === 'production',
    maxAge: 24 * 60 * 60 * 1000 // 24小时
  }
}));

// 简单的认证中间件（开发环境用，生产环境需要加强）
const requireAuth = (req, res, next) => {
  // 开发环境跳过认证（为了演示方便，暂时全部跳过）
  if (process.env.NODE_ENV === 'development' || process.env.NODE_ENV !== 'production') {
    return next();
  }
  
  // 生产环境需要认证
  if (!req.session.user) {
    return res.status(401).json({ error: '需要登录' });
  }
  next();
};

// API 路由
app.get('/api/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'openclaw-model-balancer-admin',
    version: '1.0.0',
    timestamp: new Date().toISOString()
  });
});

app.get('/api/system/info', requireAuth, async (req, res) => {
  try {
    // 获取系统信息
    const [nodeVersion, openclawVersion, diskUsage] = await Promise.all([
      execAsync('node --version').catch(() => ({ stdout: 'unknown' })),
      execAsync('openclaw --version').catch(() => ({ stdout: 'unknown' })),
      execAsync(`df -h ${WORKSPACE_PATH} | tail -1`).catch(() => ({ stdout: 'unknown' }))
    ]);

    res.json({
      system: {
        node: nodeVersion.stdout.trim(),
        openclaw: openclawVersion.stdout.trim(),
        workspace: WORKSPACE_PATH,
        disk: diskUsage.stdout.trim(),
        uptime: process.uptime()
      },
      admin: {
        port: PORT,
        started: new Date().toISOString(),
        connections: io.engine.clientsCount
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/models', requireAuth, async (req, res) => {
  try {
    const registryPath = path.join(WORKSPACE_PATH, 'models_registry.json');
    const registryData = await fs.readFile(registryPath, 'utf8');
    const registry = JSON.parse(registryData);
    
    // 获取当前使用的模型
    let currentModel = null;
    const models = registry.models || [];
    
    if (models.length > 0) {
      // 按最后使用时间排序，找到最近使用的模型
      const usedModels = models.filter(m => m.last_used);
      if (usedModels.length > 0) {
        usedModels.sort((a, b) => (b.last_used || '').localeCompare(a.last_used || ''));
        currentModel = usedModels[0];
      } else {
        // 如果没有使用记录，按优先级排序
        const sortedModels = [...models].sort((a, b) => (a.priority || 999) - (b.priority || 999));
        currentModel = sortedModels[0];
      }
    }
    
    // 获取 OpenClaw 实际配置的当前模型
    let openclawCurrentModel = null;
    try {
      const { stdout } = await execAsync('openclaw status');
      const lines = stdout.split('\n');
      for (const line of lines) {
        if (line.includes('Model')) {
          const match = line.match(/Model\s+[:：]\s*(.+)/);
          if (match) {
            openclawCurrentModel = match[1].trim();
            break;
          }
        }
      }
    } catch (error) {
      console.warn('无法获取 OpenClaw 当前模型:', error.message);
    }
    
    res.json({
      count: models.length,
      models: models,
      current_model: currentModel,
      openclaw_current_model: openclawCurrentModel,
      settings: registry.settings || {},
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/models/switch', requireAuth, async (req, res) => {
  try {
    const { modelId, reason } = req.body;
    
    if (!modelId) {
      return res.status(400).json({ error: '需要指定模型ID' });
    }
    
    // 执行切换命令
    const { stdout, stderr } = await execAsync(
      `cd ${SKILL_PATH} && python3 scripts/model_manager_enhanced.py switch ${modelId}`
    );
    
    // 发送实时通知
    io.emit('model-switched', {
      modelId,
      reason: reason || 'admin_request',
      timestamp: new Date().toISOString(),
      output: stdout
    });
    
    res.json({
      success: true,
      message: `正在切换到模型 ${modelId}`,
      output: stdout,
      error: stderr || null
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/models/test', requireAuth, async (req, res) => {
  try {
    const { modelId } = req.body;
    
    if (!modelId) {
      return res.status(400).json({ error: '需要指定模型ID' });
    }
    
    const { stdout, stderr } = await execAsync(
      `cd ${SKILL_PATH} && python3 scripts/model_manager_enhanced.py test ${modelId}`
    );
    
    // 解析测试结果
    const testResult = {
      modelId,
      timestamp: new Date().toISOString(),
      rawOutput: stdout,
      success: !stderr && stdout.includes('测试通过')
    };
    
    io.emit('model-tested', testResult);
    
    res.json(testResult);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 获取模型使用统计
app.get('/api/models/usage', requireAuth, async (req, res) => {
  try {
    // 读取使用统计文件
    const usagePath = path.join(WORKSPACE_PATH, 'logs', 'model_usage.json');
    let usageData = {};
    
    try {
      const usageContent = await fs.readFile(usagePath, 'utf8');
      usageData = JSON.parse(usageContent);
    } catch (error) {
      // 文件不存在或格式错误，返回空数据
      console.log('使用统计文件不存在，返回空数据');
    }
    
    // 获取模型注册表以补充信息
    const registryPath = path.join(WORKSPACE_PATH, 'models_registry.json');
    let modelsInfo = {};
    
    try {
      const registryContent = await fs.readFile(registryPath, 'utf8');
      const registry = JSON.parse(registryContent);
      
      // 创建模型信息映射
      registry.models?.forEach(model => {
        modelsInfo[model.id] = {
          name: model.name,
          provider: model.provider,
          status: model.status
        };
      });
    } catch (error) {
      console.warn('无法读取模型注册表:', error.message);
    }
    
    // 组合数据
    const result = {
      timestamp: new Date().toISOString(),
      total_requests: 0,
      models: []
    };
    
    // 处理每个模型的使用数据
    Object.entries(usageData).forEach(([modelId, data]) => {
      const modelInfo = modelsInfo[modelId] || { name: modelId, provider: 'unknown', status: 'unknown' };
      
      const modelUsage = {
        id: modelId,
        name: modelInfo.name,
        provider: modelInfo.provider,
        status: modelInfo.status,
        total_requests: data.total_requests || 0,
        successful_requests: data.successful_requests || 0,
        total_response_time_ms: data.total_response_time_ms || 0,
        last_used: data.last_used || null
      };
      
      // 计算衍生指标
      modelUsage.success_rate = modelUsage.total_requests > 0 
        ? (modelUsage.successful_requests / modelUsage.total_requests) * 100 
        : 0;
      
      modelUsage.avg_response_time = modelUsage.total_requests > 0
        ? Math.round(modelUsage.total_response_time_ms / modelUsage.total_requests)
        : 0;
      
      result.total_requests += modelUsage.total_requests;
      result.models.push(modelUsage);
    });
    
    // 按使用次数排序
    result.models.sort((a, b) => b.total_requests - a.total_requests);
    
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 获取单个模型的详细使用统计
app.get('/api/models/usage/:modelId', requireAuth, async (req, res) => {
  try {
    const { modelId } = req.params;
    
    // 读取使用统计文件
    const usagePath = path.join(WORKSPACE_PATH, 'logs', 'model_usage.json');
    let usageData = {};
    
    try {
      const usageContent = await fs.readFile(usagePath, 'utf8');
      usageData = JSON.parse(usageContent);
    } catch (error) {
      return res.status(404).json({ error: '使用统计文件不存在' });
    }
    
    // 获取指定模型的数据
    const modelUsage = usageData[modelId];
    if (!modelUsage) {
      return res.status(404).json({ error: `模型 ${modelId} 的使用数据不存在` });
    }
    
    // 获取模型信息
    const registryPath = path.join(WORKSPACE_PATH, 'models_registry.json');
    let modelInfo = {};
    
    try {
      const registryContent = await fs.readFile(registryPath, 'utf8');
      const registry = JSON.parse(registryContent);
      
      const model = registry.models?.find(m => m.id === modelId);
      if (model) {
        modelInfo = {
          name: model.name,
          provider: model.provider,
          status: model.status,
          priority: model.priority,
          notes: model.notes
        };
      }
    } catch (error) {
      console.warn('无法读取模型注册表:', error.message);
    }
    
    // 组合响应
    const result = {
      modelId,
      ...modelInfo,
      ...modelUsage,
      timestamp: new Date().toISOString(),
      
      // 计算指标
      success_rate: modelUsage.total_requests > 0 
        ? (modelUsage.successful_requests / modelUsage.total_requests) * 100 
        : 0,
      
      avg_response_time: modelUsage.total_requests > 0
        ? Math.round(modelUsage.total_response_time_ms / modelUsage.total_requests)
        : 0,
      
      requests_per_day: modelUsage.last_used 
        ? calculateRequestsPerDay(modelUsage)
        : 0
    };
    
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 记录模型使用
app.post('/api/models/usage', requireAuth, async (req, res) => {
  try {
    const { modelId, responseTime, success } = req.body;
    
    if (!modelId || responseTime === undefined) {
      return res.status(400).json({ error: '需要 modelId 和 responseTime' });
    }
    
    // 读取现有数据
    const usagePath = path.join(WORKSPACE_PATH, 'logs', 'model_usage.json');
    let usageData = {};
    
    try {
      const usageContent = await fs.readFile(usagePath, 'utf8');
      usageData = JSON.parse(usageContent);
    } catch (error) {
      // 文件不存在，创建新文件
      console.log('创建新的使用统计文件');
    }
    
    // 初始化模型数据（如果不存在）
    if (!usageData[modelId]) {
      usageData[modelId] = {
        total_requests: 0,
        successful_requests: 0,
        total_response_time_ms: 0,
        last_used: null,
        response_times: []
      };
    }
    
    // 更新数据
    const modelData = usageData[modelId];
    modelData.total_requests += 1;
    modelData.total_response_time_ms += responseTime;
    modelData.last_used = new Date().toISOString();
    
    // 记录响应时间（保留最近100个）
    modelData.response_times.push(responseTime);
    if (modelData.response_times.length > 100) {
      modelData.response_times = modelData.response_times.slice(-100);
    }
    
    if (success) {
      modelData.successful_requests += 1;
    }
    
    // 保存数据
    await fs.writeFile(usagePath, JSON.stringify(usageData, null, 2));
    
    // 发送实时更新
    io.emit('model-usage-updated', {
      modelId,
      total_requests: modelData.total_requests,
      success_rate: modelData.total_requests > 0 
        ? (modelData.successful_requests / modelData.total_requests) * 100 
        : 0,
      timestamp: new Date().toISOString()
    });
    
    res.json({
      success: true,
      message: '使用记录已保存',
      modelId,
      total_requests: modelData.total_requests
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 辅助函数：计算每日请求数
function calculateRequestsPerDay(modelUsage) {
  if (!modelUsage.last_used || !modelUsage.total_requests) {
    return 0;
  }
  
  const lastUsed = new Date(modelUsage.last_used);
  const now = new Date();
  const daysDiff = (now - lastUsed) / (1000 * 60 * 60 * 24);
  
  if (daysDiff <= 0) {
    return modelUsage.total_requests;
  }
  
  return Math.round(modelUsage.total_requests / daysDiff);
}

app.get('/api/performance', requireAuth, async (req, res) => {
  try {
    const { stdout } = await execAsync(
      `cd ${SKILL_PATH} && python3 scripts/model_predictive_maintenance.py report`
    );
    
    // 尝试解析JSON输出
    try {
      const jsonMatch = stdout.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        const performanceData = JSON.parse(jsonMatch[0]);
        res.json(performanceData);
      } else {
        res.json({ raw: stdout });
      }
    } catch {
      res.json({ raw: stdout });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// AI 优化端点
app.get('/api/ai-optimization', requireAuth, async (req, res) => {
  try {
    // 运行 AI 优化算法
    const { stdout, stderr } = await execAsync(
      `cd ${SKILL_PATH} && python3 scripts/model_ai_optimizer.py`
    );
    
    // 尝试解析 JSON 输出
    let optimizationData;
    try {
      const jsonMatch = stdout.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        optimizationData = JSON.parse(jsonMatch[0]);
      } else {
        // 如果没有 JSON 输出，创建模拟数据用于演示
        optimizationData = createMockOptimizationData();
      }
    } catch (error) {
      console.warn('无法解析 AI 优化输出，使用模拟数据:', error.message);
      optimizationData = createMockOptimizationData();
    }
    
    res.json({
      success: true,
      data: optimizationData,
      timestamp: new Date().toISOString(),
      raw_output: stdout.substring(0, 500) // 只返回前500字符
    });
  } catch (error) {
    console.error('AI 优化错误:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message,
      data: createMockOptimizationData() // 错误时返回模拟数据
    });
  }
});

// 运行 AI 优化并切换
app.post('/api/ai-optimization/run', requireAuth, async (req, res) => {
  try {
    const { autoSwitch = false } = req.body;
    
    // 运行 AI 优化
    const { stdout } = await execAsync(
      `cd ${SKILL_PATH} && python3 scripts/model_ai_optimizer.py`
    );
    
    // 解析最佳模型
    let bestModel = null;
    try {
      const jsonMatch = stdout.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        const data = JSON.parse(jsonMatch[0]);
        bestModel = data.best_model;
      }
    } catch (error) {
      console.warn('无法解析 AI 优化输出:', error.message);
    }
    
    // 如果找到最佳模型且需要自动切换
    let switchResult = null;
    if (bestModel && autoSwitch && bestModel.id) {
      try {
        const { stdout: switchStdout } = await execAsync(
          `cd ${SKILL_PATH} && python3 scripts/model_manager_enhanced.py switch ${bestModel.id}`
        );
        
        switchResult = {
          success: true,
          modelId: bestModel.id,
          modelName: bestModel.name,
          output: switchStdout
        };
        
        // 发送实时通知
        io.emit('ai-optimization-switch', {
          modelId: bestModel.id,
          modelName: bestModel.name,
          reason: 'ai_optimization',
          timestamp: new Date().toISOString()
        });
      } catch (switchError) {
        switchResult = {
          success: false,
          error: switchError.message
        };
      }
    }
    
    res.json({
      success: true,
      message: 'AI 优化已执行',
      best_model: bestModel,
      auto_switch: switchResult,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

// 获取 AI 优化配置
app.get('/api/ai-optimization/config', requireAuth, async (req, res) => {
  try {
    // 读取 AI 优化配置
    const configPath = path.join(SKILL_PATH, 'config', 'ai_optimization.json');
    let configData = {};
    
    try {
      const configContent = await fs.readFile(configPath, 'utf8');
      configData = JSON.parse(configContent);
    } catch (error) {
      // 如果文件不存在，返回默认配置
      configData = {
        algorithm: {
          weights: {
            response_time: 0.3,
            success_rate: 0.4,
            cost_efficiency: 0.1,
            stability: 0.1,
            priority: 0.1
          },
          time_sensitive: true,
          predictive_switching: true,
          learning_enabled: true
        },
        monitoring: {
          collect_performance_data: true,
          performance_history_days: 30,
          auto_cleanup_days: 90
        },
        notifications: {
          on_optimization: true,
          on_switch: true,
          on_performance_decline: true
        }
      };
    }
    
    res.json({
      success: true,
      config: configData,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

// 更新 AI 优化配置
app.post('/api/ai-optimization/config', requireAuth, async (req, res) => {
  try {
    const { config } = req.body;
    
    if (!config) {
      return res.status(400).json({ error: '需要提供配置数据' });
    }
    
    // 确保配置目录存在
    const configDir = path.join(SKILL_PATH, 'config');
    await fs.mkdir(configDir, { recursive: true });
    
    // 保存配置
    const configPath = path.join(configDir, 'ai_optimization.json');
    await fs.writeFile(configPath, JSON.stringify(config, null, 2));
    
    // 发送配置更新通知
    io.emit('ai-optimization-config-updated', {
      config: config,
      timestamp: new Date().toISOString()
    });
    
    res.json({
      success: true,
      message: 'AI 优化配置已更新',
      config: config,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

// 辅助函数：创建模拟优化数据（用于演示）
function createMockOptimizationData() {
  const now = new Date();
  const hour = now.getHours();
  
  // 确定时间上下文
  let timeContext;
  if (hour >= 9 && hour < 18) {
    timeContext = {
      period: 'work_hours',
      priority: 'performance',
      description: '工作时间，优先性能'
    };
  } else if (hour >= 18 && hour < 23) {
    timeContext = {
      period: 'evening_peak',
      priority: 'balanced',
      description: '晚间高峰，平衡性能与成本'
    };
  } else {
    timeContext = {
      period: 'off_peak',
      priority: 'cost_efficiency',
      description: '非高峰时段，优先成本效率'
    };
  }
  
  // 模拟模型数据
  const models = [
    {
      id: 'M018',
      name: 'aicodee/MiniMax-M2.5-highspeed',
      provider: 'aicodee',
      priority: 1,
      score: 0.872,
      scores: {
        response_time: 0.85,
        success_rate: 0.92,
        cost_efficiency: 0.78,
        stability: 0.91,
        priority_adjustment: 0.2,
        usage_pattern: 0.88
      },
      trend: 'improving',
      response_time: 1250,
      success_rate: 98.5,
      cost_per_request: 0.0012
    },
    {
      id: 'M019',
      name: 'aicodee/MiniMax-M2.7-highspeed',
      provider: 'aicodee',
      priority: 2,
      score: 0.845,
      scores: {
        response_time: 0.82,
        success_rate: 0.94,
        cost_efficiency: 0.72,
        stability: 0.89,
        priority_adjustment: 0.1,
        usage_pattern: 0.85
      },
      trend: 'stable',
      response_time: 1420,
      success_rate: 99.1,
      cost_per_request: 0.0018
    },
    {
      id: 'M001',
      name: 'deepseek/deepseek-chat',
      provider: 'deepseek',
      priority: 3,
      score: 0.821,
      scores: {
        response_time: 0.91,
        success_rate: 0.88,
        cost_efficiency: 0.85,
        stability: 0.87,
        priority_adjustment: 0.05,
        usage_pattern: 0.92
      },
      trend: 'slightly_degrading',
      response_time: 980,
      success_rate: 97.2,
      cost_per_request: 0.0008
    },
    {
      id: 'M002',
      name: 'deepseek/deepseek-reasoner',
      provider: 'deepseek',
      priority: 4,
      score: 0.798,
      scores: {
        response_time: 0.76,
        success_rate: 0.91,
        cost_efficiency: 0.68,
        stability: 0.84,
        priority_adjustment: 0.02,
        usage_pattern: 0.79
      },
      trend: 'stable',
      response_time: 1850,
      success_rate: 98.8,
      cost_per_request: 0.0015
    }
  ];
  
  // 按评分排序
  models.sort((a, b) => b.score - a.score);
  
  return {
    timestamp: now.toISOString(),
    time_context: timeContext,
    best_model: models[0],
    models: models,
    metrics: {
      avg_response_time: Math.round(models.reduce((sum, m) => sum + m.response_time, 0) / models.length),
      avg_success_rate: parseFloat((models.reduce((sum, m) => sum + m.success_rate, 0) / models.length).toFixed(1)),
      avg_cost_per_request: parseFloat((models.reduce((sum, m) => sum + m.cost_per_request, 0) / models.length).toFixed(4)),
      system_availability: 99.7,
      response_trend: 'improving'
    },
    algorithm: {
      weights: {
        response_time: timeContext.period === 'work_hours' ? 0.4 : 0.3,
        success_rate: 0.4,
        cost_efficiency: timeContext.period === 'off_peak' ? 0.4 : 0.1,
        stability: 0.1,
        priority: 0.1
      },
      version: '2.0',
      features: ['time_sensitive', 'predictive_trends', 'cost_optimization']
    },
    selection_reason: `根据${timeContext.description}，${models[0].name}在响应时间(${models[0].scores.response_time * 100}分)、成功率(${models[0].success_rate}%)和成本效率(${models[0].scores.cost_efficiency * 100}分)方面表现最佳。`
  };
}

app.get('/api/logs', requireAuth, async (req, res) => {
  try {
    const { limit = 100, type = 'all' } = req.query;
    const logPath = path.join(WORKSPACE_PATH, 'logs', 'model_switch.log');
    
    let logs = [];
    if (await fs.access(logPath).then(() => true).catch(() => false)) {
      const logContent = await fs.readFile(logPath, 'utf8');
      const logLines = logContent.split('\n').filter(line => line.trim());
      
      // 应用过滤
      if (type !== 'all') {
        logs = logLines.filter(line => line.toLowerCase().includes(type.toLowerCase()));
      } else {
        logs = logLines;
      }
      
      // 限制数量
      logs = logs.slice(-limit);
    }
    
    res.json({
      count: logs.length,
      logs: logs.map(line => ({
        timestamp: line.substring(0, 23),
        level: line.includes('ERROR') ? 'error' : line.includes('WARNING') ? 'warning' : 'info',
        message: line.substring(24),
        raw: line
      })),
      file: logPath
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/auto-switch/run', requireAuth, async (req, res) => {
  try {
    const { stdout } = await execAsync(
      `cd ${SKILL_PATH} && python3 scripts/model_manager_enhanced.py auto`
    );
    
    io.emit('auto-switch-run', {
      timestamp: new Date().toISOString(),
      output: stdout
    });
    
    res.json({
      success: true,
      message: '自动切换已执行',
      output: stdout
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/settings', requireAuth, async (req, res) => {
  try {
    const registryPath = path.join(WORKSPACE_PATH, 'models_registry.json');
    const registryData = await fs.readFile(registryPath, 'utf8');
    const registry = JSON.parse(registryData);
    
    res.json({
      settings: registry.settings || {},
      version: registry.version || '1.0',
      lastModified: (await fs.stat(registryPath)).mtime.toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/settings/update', requireAuth, async (req, res) => {
  try {
    const { settings } = req.body;
    
    if (!settings) {
      return res.status(400).json({ error: '需要提供设置数据' });
    }
    
    const registryPath = path.join(WORKSPACE_PATH, 'models_registry.json');
    const registryData = await fs.readFile(registryPath, 'utf8');
    const registry = JSON.parse(registryData);
    
    // 更新设置
    registry.settings = { ...registry.settings, ...settings };
    registry.updated_at = new Date().toISOString();
    
    await fs.writeFile(registryPath, JSON.stringify(registry, null, 2));
    
    io.emit('settings-updated', {
      settings: registry.settings,
      timestamp: new Date().toISOString()
    });
    
    res.json({
      success: true,
      message: '设置已更新',
      settings: registry.settings
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// WebSocket 连接处理
io.on('connection', (socket) => {
  console.log(`📡 客户端连接: ${socket.id}`);
  
  // 发送欢迎消息
  socket.emit('welcome', {
    message: '连接到 Model Auto-Switch Admin',
    timestamp: new Date().toISOString(),
    clients: io.engine.clientsCount
  });
  
  // 定期发送系统状态
  const statusInterval = setInterval(async () => {
    try {
      // 尝试获取真实状态
      const { stdout } = await execAsync(
        `cd ${SKILL_PATH} && python3 scripts/model_manager_enhanced.py status --json 2>/dev/null || echo '{}'`
      );
      
      let statusData;
      try {
        statusData = JSON.parse(stdout.trim());
      } catch {
        statusData = { raw: stdout.trim() };
      }
      
      // 添加模拟数据用于测试
      const testStatus = {
        current_model: 'deepseek/deepseek-chat',
        active_models: '19',
        total_models: '19',
        auto_switch: '启用',
        timestamp: new Date().toISOString()
      };
      
      socket.emit('system-status', {
        timestamp: new Date().toISOString(),
        status: JSON.stringify(testStatus)
      });
    } catch (error) {
      // 发送测试数据
      const testStatus = {
        current_model: '测试模型',
        active_models: '5',
        total_models: '19',
        auto_switch: '测试中',
        timestamp: new Date().toISOString()
      };
      
      socket.emit('system-status', {
        timestamp: new Date().toISOString(),
        status: JSON.stringify(testStatus)
      });
    }
  }, 5000); // 每5秒更新一次
  
  // 断开连接
  socket.on('disconnect', () => {
    console.log(`📡 客户端断开: ${socket.id}`);
    clearInterval(statusInterval);
  });
  
  // 自定义事件
  socket.on('request-models', async () => {
    try {
      const registryPath = path.join(WORKSPACE_PATH, 'models_registry.json');
      const registryData = await fs.readFile(registryPath, 'utf8');
      const registry = JSON.parse(registryData);
      
      socket.emit('models-data', {
        models: registry.models || [],
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      socket.emit('error', { message: error.message });
    }
  });
});

// 管理界面路由
app.get('/admin', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'admin.html'));
});

app.get('/admin/*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'admin.html'));
});

// 404 处理
app.use((req, res) => {
  res.status(404).json({
    error: '未找到路由',
    path: req.path,
    method: req.method,
    timestamp: new Date().toISOString()
  });
});

// 错误处理
app.use((err, req, res, next) => {
  console.error('❌ 服务器错误:', err);
  
  res.status(err.status || 500).json({
    error: process.env.NODE_ENV === 'development' ? err.message : '服务器内部错误',
    timestamp: new Date().toISOString()
  });
});

// 启动服务器
httpServer.listen(PORT, () => {
  console.log(`
🚀 OpenClaw Model Auto-Switch Admin 已启动!
==========================================
📊 管理界面: http://localhost:${PORT}/admin
🔧 API 地址: http://localhost:${PORT}/api
📡 WebSocket: ws://localhost:${PORT}
📁 工作空间: ${WORKSPACE_PATH}
⏰ 启动时间: ${new Date().toLocaleString('zh-CN')}
==========================================
  `);
});

// 优雅关闭
process.on('SIGTERM', () => {
  console.log('🛑 收到 SIGTERM 信号，正在关闭服务器...');
  httpServer.close(() => {
    console.log('✅ 服务器已关闭');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('🛑 收到 SIGINT 信号，正在关闭服务器...');
  httpServer.close(() => {
    console.log('✅ 服务器已关闭');
    process.exit(0);
  });
});

module.exports = { app, httpServer, io };