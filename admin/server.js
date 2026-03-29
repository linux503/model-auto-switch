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
const SKILL_PATH = path.join(WORKSPACE_PATH, 'skills/model-auto-switch');

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
    service: 'model-auto-switch-admin',
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
    
    res.json({
      count: registry.models?.length || 0,
      models: registry.models || [],
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
      const { stdout } = await execAsync(
        `cd ${SKILL_PATH} && python3 scripts/model_manager_enhanced.py status --json 2>/dev/null || echo '{}'`
      );
      
      socket.emit('system-status', {
        timestamp: new Date().toISOString(),
        status: stdout.trim() || '{}'
      });
    } catch (error) {
      socket.emit('system-status', {
        timestamp: new Date().toISOString(),
        error: error.message
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