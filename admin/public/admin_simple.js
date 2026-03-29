// OpenClaw 模型管理后台 - 简化修复版

console.log('🚀 OpenClaw 管理后台初始化...');

// 全局状态
let socket = null;
let modelsData = [];

// DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ DOM加载完成');
    initialize();
});

// 初始化应用
function initialize() {
    console.log('🔧 初始化应用...');
    
    // 设置基本事件
    setupBasicEvents();
    
    // 连接WebSocket
    connectWebSocket();
    
    // 加载初始数据
    loadInitialData();
    
    // 启动时钟
    startClock();
    
    console.log('✅ 初始化完成');
}

// 设置基本事件
function setupBasicEvents() {
    console.log('⚙️ 设置事件监听器...');
    
    // 标签页切换
    document.querySelectorAll('.nav-link[data-tab]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const tab = this.getAttribute('data-tab');
            console.log('切换标签页:', tab);
            switchTab(tab);
        });
    });
    
    // 刷新按钮
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            console.log('刷新数据');
            refreshData();
        });
    }
    
    // 模型刷新按钮
    const refreshModelsBtn = document.getElementById('refreshModelsBtn');
    if (refreshModelsBtn) {
        refreshModelsBtn.addEventListener('click', loadModels);
    }
    
    // 使用统计刷新按钮
    const refreshUsageBtn = document.getElementById('refreshUsageBtn');
    if (refreshUsageBtn) {
        refreshUsageBtn.addEventListener('click', loadUsageStats);
    }
    
    // 使用统计导出按钮
    const exportUsageBtn = document.getElementById('exportUsageBtn');
    if (exportUsageBtn) {
        exportUsageBtn.addEventListener('click', exportUsageData);
    }
}

// 切换标签页
function switchTab(tabName) {
    console.log('切换到标签页:', tabName);
    
    // 更新导航
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('data-tab') === tabName) {
            link.classList.add('active');
        }
    });
    
    // 显示对应内容
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    
    const targetTab = document.getElementById(tabName + 'Tab');
    if (targetTab) {
        targetTab.classList.add('active');
    }
    
    // 加载数据
    if (tabName === 'dashboard') {
        loadDashboardData();
    } else if (tabName === 'models') {
        loadModels();
    } else if (tabName === 'usage') {
        loadUsageStats();
    }
}

// 连接WebSocket
function connectWebSocket() {
    console.log('🔌 连接WebSocket...');
    
    try {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}`;
        
        socket = io(wsUrl);
        
        socket.on('connect', () => {
            console.log('✅ WebSocket连接成功');
            updateConnectionStatus(true);
            showMessage('连接成功', '已连接到实时服务', 'success');
        });
        
        socket.on('disconnect', () => {
            console.log('⚠️ WebSocket连接断开');
            updateConnectionStatus(false);
            showMessage('连接断开', '实时服务已断开', 'warning');
        });
        
        socket.on('system-status', (data) => {
            console.log('📊 收到系统状态:', data);
            updateRealtimeStatus(data);
        });
        
        socket.on('models-data', (data) => {
            console.log('📦 收到模型数据:', data.count, '个模型');
            modelsData = data.models || [];
            updateDashboard(data);
        });
        
    } catch (error) {
        console.error('❌ WebSocket连接失败:', error);
        showMessage('连接失败', '无法连接实时服务', 'danger');
    }
}

// 更新连接状态
function updateConnectionStatus(connected) {
    const statusElement = document.getElementById('connectionStatus');
    const textElement = document.getElementById('connectionText');
    
    if (statusElement && textElement) {
        if (connected) {
            statusElement.className = 'connection-status connected';
            textElement.textContent = '已连接';
            textElement.className = 'text-success';
        } else {
            statusElement.className = 'connection-status disconnected';
            textElement.textContent = '未连接';
            textElement.className = 'text-warning';
        }
    }
}

// 加载初始数据
function loadInitialData() {
    console.log('📥 加载初始数据...');
    loadDashboardData();
}

// 加载仪表板数据
async function loadDashboardData() {
    console.log('📊 加载仪表板数据...');
    
    try {
        const response = await fetch('/api/models');
        if (response.ok) {
            const data = await response.json();
            console.log('✅ 仪表板数据加载成功:', data.count, '个模型');
            updateDashboard(data);
        } else {
            console.error('❌ 仪表板数据加载失败:', response.status);
            showMessage('错误', '加载仪表板数据失败', 'danger');
        }
    } catch (error) {
        console.error('❌ 仪表板数据加载异常:', error);
        showMessage('错误', '加载数据异常', 'danger');
    }
}

// 更新仪表板
function updateDashboard(data) {
    console.log('🔄 更新仪表板...');
    
    if (!data) {
        console.warn('⚠️ 没有数据可更新');
        return;
    }
    
    const totalModels = data.count || 0;
    const activeModels = data.models?.filter(m => m.status === 'active').length || 0;
    
    console.log('📈 统计信息:', { totalModels, activeModels });
    
    // 更新统计卡片
    updateElement('totalModels', totalModels);
    updateElement('activeModels', activeModels);
    
    // 更新进度条
    updateProgressBar('activeModelsProgress', totalModels, activeModels);
    
    // 更新当前模型
    updateCurrentModel(data);
    
    // 更新成功率
    updateSuccessRate(data.models);
    
    // 如果当前在模型标签页，更新表格
    const currentTab = document.querySelector('.nav-link.active')?.getAttribute('data-tab');
    if (currentTab === 'models' && data.models) {
        updateModelsTable(data.models);
    }
}

// 更新元素
function updateElement(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
        console.log(`✅ 更新 ${id}: ${value}`);
    } else {
        console.error(`❌ 找不到元素: ${id}`);
    }
}

// 更新进度条
function updateProgressBar(elementId, total, active) {
    const element = document.getElementById(elementId);
    if (element && total > 0) {
        const percentage = (active / total) * 100;
        element.style.width = `${percentage}%`;
        console.log(`📊 进度条更新: ${percentage}%`);
    }
}

// 更新当前模型
function updateCurrentModel(data) {
    let currentModel = '未设置';
    let openclawCurrentModel = '未知';
    
    // 显示注册表中的当前模型
    if (data.current_model) {
        currentModel = data.current_model.name;
        if (currentModel.length > 20) {
            currentModel = currentModel.substring(0, 20) + '...';
        }
    }
    
    // 显示 OpenClaw 实际使用的模型
    if (data.openclaw_current_model && data.openclaw_current_model !== 'None') {
        openclawCurrentModel = data.openclaw_current_model;
        if (openclawCurrentModel.length > 20) {
            openclawCurrentModel = openclawCurrentModel.substring(0, 20) + '...';
        }
    }
    
    updateElement('currentModel', currentModel);
    updateElement('openclawCurrentModel', openclawCurrentModel);
    
    // 更新状态卡片
    updateStatusCards(data);
}

// 更新状态卡片
function updateStatusCards(data) {
    // 检查模型一致性
    const registryModel = data.current_model?.name || '';
    const openclawModel = data.openclaw_current_model || '';
    
    let consistencyStatus = '一致';
    let consistencyClass = 'text-success';
    
    if (registryModel && openclawModel && openclawModel !== 'None') {
        // 简单检查模型名称是否匹配
        const registryName = registryModel.toLowerCase();
        const openclawName = openclawModel.toLowerCase();
        
        if (!registryName.includes(openclawName) && !openclawName.includes(registryName)) {
            consistencyStatus = '不一致';
            consistencyClass = 'text-warning';
        }
    }
    
    // 更新一致性状态
    const consistencyElement = document.getElementById('modelConsistency');
    if (consistencyElement) {
        consistencyElement.textContent = consistencyStatus;
        consistencyElement.className = consistencyClass;
    }
}

// 更新成功率
function updateSuccessRate(models) {
    let overallSuccessRate = 0;
    
    if (models && models.length > 0) {
        const modelsWithPerformance = models.filter(m => m.performance && m.performance.success_rate);
        if (modelsWithPerformance.length > 0) {
            const totalRate = modelsWithPerformance.reduce((sum, m) => sum + m.performance.success_rate, 0);
            overallSuccessRate = (totalRate / modelsWithPerformance.length) * 100;
        }
    }
    
    updateElement('successRate', overallSuccessRate.toFixed(1) + '%');
}

// 加载模型数据
async function loadModels() {
    console.log('📋 加载模型数据...');
    
    const tbody = document.getElementById('modelsTableBody');
    if (!tbody) {
        console.error('❌ 找不到模型表格容器');
        return;
    }
    
    // 显示加载状态
    tbody.innerHTML = `
        <tr>
            <td colspan="7" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">加载中...</span>
                </div>
                <p class="mt-3 text-muted">正在加载模型数据...</p>
            </td>
        </tr>
    `;
    
    try {
        const response = await fetch('/api/models');
        if (response.ok) {
            const data = await response.json();
            console.log('✅ 模型数据加载成功:', data.count, '个模型');
            modelsData = data.models || [];
            updateModelsTable(modelsData);
            showMessage('成功', `已加载 ${data.count} 个模型`, 'success');
        } else {
            console.error('❌ 模型数据加载失败:', response.status);
            showError(tbody, '加载模型数据失败');
            showMessage('错误', '加载模型数据失败', 'danger');
        }
    } catch (error) {
        console.error('❌ 模型数据加载异常:', error);
        showError(tbody, '加载模型数据异常');
        showMessage('错误', '加载模型数据异常', 'danger');
    }
}

// 更新模型表格
function updateModelsTable(models) {
    console.log('🔄 更新模型表格:', models?.length, '个模型');
    
    const tbody = document.getElementById('modelsTableBody');
    if (!tbody) {
        console.error('❌ 找不到模型表格容器');
        return;
    }
    
    if (!models || models.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center py-5 text-muted">
                    <i class="bi bi-inbox display-4"></i>
                    <div class="mt-3">暂无模型数据</div>
                </td>
            </tr>
        `;
        return;
    }
    
    let html = '';
    models.forEach(model => {
        const lastUsed = model.last_used ? 
            new Date(model.last_used).toLocaleDateString('zh-CN') + ' ' + 
            new Date(model.last_used).toLocaleTimeString('zh-CN', {hour: '2-digit', minute: '2-digit'}) : 
            '从未使用';
        
        const statusBadge = model.status === 'active' ? 
            '<span class="badge bg-success">活跃</span>' : 
            '<span class="badge bg-secondary">禁用</span>';
        
        html += `
            <tr>
                <td><strong>${model.id}</strong></td>
                <td>
                    <div class="d-flex align-items-center">
                        <div class="model-icon me-3">
                            <i class="bi bi-robot fs-4 text-primary"></i>
                        </div>
                        <div>
                            <div class="fw-bold">${model.name}</div>
                            ${model.notes ? `<small class="text-muted">${model.notes}</small>` : ''}
                        </div>
                    </div>
                </td>
                <td><span class="badge bg-secondary">${model.provider}</span></td>
                <td>${statusBadge}</td>
                <td>
                    <span class="badge bg-${model.priority <= 3 ? 'danger' : model.priority <= 6 ? 'warning' : 'secondary'}">
                        优先级 ${model.priority}
                    </span>
                </td>
                <td><small class="text-muted">${lastUsed}</small></td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" title="测试模型">
                            <i class="bi bi-play-circle"></i>
                        </button>
                        <button class="btn btn-outline-success" title="切换到该模型">
                            <i class="bi bi-arrow-right-circle"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    });
    
    tbody.innerHTML = html;
    console.log('✅ 模型表格更新完成');
}

// 显示错误
function showError(container, message) {
    if (container) {
        container.innerHTML = `
            <tr>
                <td colspan="7" class="text-center py-5">
                    <i class="bi bi-exclamation-triangle text-warning fs-1"></i>
                    <p class="mt-3 text-danger">${message}</p>
                    <button class="btn btn-outline-primary mt-2" onclick="loadModels()">
                        <i class="bi bi-arrow-clockwise"></i> 重试
                    </button>
                </td>
            </tr>
        `;
    }
}

// 更新实时状态
function updateRealtimeStatus(data) {
    console.log('🔄 更新实时状态:', data);
    
    const container = document.getElementById('realtimeStatus');
    if (!container) return;
    
    try {
        let status = {};
        try {
            status = JSON.parse(data.status || '{}');
        } catch {
            status = { raw: data.status };
        }
        
        let html = '';
        
        if (status.raw) {
            html = `
                <div class="alert alert-info">
                    <i class="bi bi-info-circle"></i>
                    ${status.raw}
                </div>
            `;
        } else {
            const currentModel = status.current_model || '未设置';
            const activeModels = status.active_models || '0';
            const totalModels = status.total_models || '19';
            const autoSwitch = status.auto_switch || '未知';
            
            html = `
                <div class="row">
                    <div class="col-md-6">
                        <div class="status-item mb-4">
                            <div class="d-flex align-items-center mb-2">
                                <i class="bi bi-robot text-primary me-2"></i>
                                <small class="text-muted">当前模型</small>
                            </div>
                            <div class="h4 fw-bold">${currentModel}</div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="status-item mb-4">
                            <div class="d-flex align-items-center mb-2">
                                <i class="bi bi-check-circle text-success me-2"></i>
                                <small class="text-muted">活跃模型</small>
                            </div>
                            <div class="h4 fw-bold">${activeModels}<span class="h6 text-muted">/${totalModels}</span></div>
                        </div>
                    </div>
                </div>
            `;
        }
        
        container.innerHTML = html;
        console.log('✅ 实时状态更新完成');
    } catch (error) {
        console.error('❌ 更新实时状态错误:', error);
        container.innerHTML = `
            <div class="alert alert-warning">
                <i class="bi bi-exclamation-triangle"></i>
                实时状态解析错误
            </div>
        `;
    }
}

// 显示消息
function showMessage(title, message, type = 'info') {
    console.log(`💬 显示消息: ${title} - ${message}`);
    
    // 简单的alert替代
    alert(`${title}: ${message}`);
}

// 启动时钟
function startClock() {
    console.log('⏰ 启动时钟');
    
    function updateClock() {
        const element = document.getElementById('serverTime');
        if (element) {
            const now = new Date();
            element.textContent = now.toLocaleTimeString('zh-CN', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        }
    }
    
    updateClock();
    setInterval(updateClock, 1000);
}

// 刷新数据
function refreshData() {
    console.log('🔄 刷新数据');
    loadDashboardData();
    showMessage('刷新', '数据已刷新', 'info');
}

// 加载使用统计
async function loadUsageStats() {
    console.log('📊 加载使用统计...');
    
    const tbody = document.getElementById('usageTableBody');
    if (!tbody) {
        console.error('❌ 找不到使用统计表格容器');
        return;
    }
    
    // 显示加载状态
    tbody.innerHTML = `
        <tr>
            <td colspan="8" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">加载中...</span>
                </div>
                <p class="mt-3 text-muted">正在加载使用统计...</p>
            </td>
        </tr>
    `;
    
    try {
        const response = await fetch('/api/models/usage');
        if (response.ok) {
            const data = await response.json();
            console.log('✅ 使用统计加载成功:', data.total_requests, '总请求数');
            updateUsageTable(data);
            showMessage('成功', `已加载使用统计 (${data.total_requests} 总请求数)`, 'success');
        } else {
            const error = await response.text();
            console.error('❌ 使用统计加载失败:', error);
            showMessage('错误', '加载使用统计失败', 'danger');
        }
    } catch (error) {
        console.error('❌ 使用统计加载异常:', error);
        showMessage('错误', '加载使用统计异常', 'danger');
    }
}

// 更新使用统计表格
function updateUsageTable(data) {
    const tbody = document.getElementById('usageTableBody');
    if (!tbody) return;
    
    // 更新统计卡片
    updateElement('totalRequests', data.total_requests || 0);
    
    // 计算平均成功率
    let totalSuccessRate = 0;
    let activeModels = 0;
    
    data.models?.forEach(model => {
        if (model.total_requests > 0) {
            totalSuccessRate += model.success_rate || 0;
            activeModels++;
        }
    });
    
    const avgSuccessRate = activeModels > 0 ? (totalSuccessRate / activeModels).toFixed(1) : 0;
    updateElement('avgSuccessRate', avgSuccessRate + '%');
    
    // 计算平均响应时间
    let totalResponseTime = 0;
    let totalModelsWithResponse = 0;
    
    data.models?.forEach(model => {
        if (model.avg_response_time > 0) {
            totalResponseTime += model.avg_response_time;
            totalModelsWithResponse++;
        }
    });
    
    const avgResponseTime = totalModelsWithResponse > 0 
        ? Math.round(totalResponseTime / totalModelsWithResponse)
        : 0;
    updateElement('avgResponseTime', avgResponseTime + 'ms');
    
    // 更新活跃模型数
    updateElement('activeModelsCount', activeModels);
    
    // 更新表格
    if (!data.models || data.models.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center py-5">
                    <div class="text-muted">
                        <i class="bi bi-bar-chart" style="font-size: 2rem;"></i>
                        <p class="mt-3">暂无使用数据</p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }
    
    let html = '';
    data.models.forEach((model, index) => {
        const successRate = model.success_rate || 0;
        const responseTime = model.avg_response_time || 0;
        const lastUsed = model.last_used ? new Date(model.last_used).toLocaleString('zh-CN') : '从未使用';
        
        // 确定状态颜色
        let statusClass = 'text-warning';
        let statusText = '未知';
        
        if (model.status === 'active') {
            statusClass = 'text-success';
            statusText = '活跃';
        } else if (model.status === 'disabled') {
            statusClass = 'text-danger';
            statusText = '禁用';
        }
        
        // 确定成功率颜色
        let successRateClass = 'text-success';
        if (successRate < 80) successRateClass = 'text-warning';
        if (successRate < 60) successRateClass = 'text-danger';
        
        // 确定响应时间颜色
        let responseTimeClass = 'text-success';
        if (responseTime > 2000) responseTimeClass = 'text-warning';
        if (responseTime > 5000) responseTimeClass = 'text-danger';
        
        html += `
            <tr>
                <td>${index + 1}</td>
                <td>
                    <strong>${model.name || model.id}</strong>
                    <br>
                    <small class="text-muted">${model.provider || '未知提供商'}</small>
                </td>
                <td>
                    <span class="badge bg-primary">${model.total_requests || 0}</span>
                </td>
                <td>
                    <span class="${successRateClass} fw-bold">${successRate.toFixed(1)}%</span>
                </td>
                <td>
                    <span class="${responseTimeClass} fw-bold">${responseTime}ms</span>
                </td>
                <td>
                    <small class="text-muted">${lastUsed}</small>
                </td>
                <td>
                    <span class="${statusClass}">
                        <i class="bi bi-circle-fill"></i> ${statusText}
                    </span>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-info" onclick="testModel('${model.id}')">
                        <i class="bi bi-play-circle"></i> 测试
                    </button>
                </td>
            </tr>
        `;
    });
    
    tbody.innerHTML = html;
}

// 测试模型
function testModel(modelId) {
    console.log(`🧪 测试模型: ${modelId}`);
    
    fetch('/api/models/test', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ modelId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage('测试成功', `模型 ${modelId} 测试通过`, 'success');
        } else {
            showMessage('测试失败', `模型 ${modelId} 测试失败`, 'danger');
        }
    })
    .catch(error => {
        console.error('❌ 测试模型异常:', error);
        showMessage('错误', '测试模型异常', 'danger');
    });
}

// 导出使用数据
async function exportUsageData() {
    console.log('📤 导出使用数据...');
    
    try {
        const response = await fetch('/api/models/usage');
        if (response.ok) {
            const data = await response.json();
            
            // 创建CSV内容
            let csvContent = "模型ID,模型名称,提供商,状态,请求数,成功率(%),平均响应时间(ms),最后使用\n";
            
            data.models?.forEach(model => {
                const row = [
                    model.id,
                    `"${model.name || ''}"`,
                    `"${model.provider || ''}"`,
                    model.status || 'unknown',
                    model.total_requests || 0,
                    (model.success_rate || 0).toFixed(1),
                    model.avg_response_time || 0,
                    model.last_used || ''
                ];
                csvContent += row.join(',') + '\n';
            });
            
            // 创建下载链接
            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `model_usage_${new Date().toISOString().slice(0, 10)}.csv`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
            
            showMessage('导出成功', '使用数据已导出为CSV文件', 'success');
        } else {
            const error = await response.text();
            console.error('❌ 导出数据失败:', error);
            showMessage('错误', '导出数据失败', 'danger');
        }
    } catch (error) {
        console.error('❌ 导出数据异常:', error);
        showMessage('错误', '导出数据异常', 'danger');
    }
}

// 全局函数
window.loadModels = loadModels;
window.refreshData = refreshData;
window.loadUsageStats = loadUsageStats;
window.testModel = testModel;

console.log('🎉 OpenClaw 管理后台 - 简化版加载完成');