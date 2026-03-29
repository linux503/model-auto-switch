// 调试脚本 - 直接测试数据加载和更新

console.log('🔧 开始调试 OpenClaw 管理后台');

// 检查关键DOM元素
function checkElements() {
    console.log('检查DOM元素...');
    const elements = [
        'totalModels', 'activeModels', 'currentModel', 'successRate',
        'modelsTableBody', 'connectionStatus', 'realtimeStatus'
    ];
    
    elements.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            console.log(`✅ ${id}: 存在`, element);
        } else {
            console.error(`❌ ${id}: 不存在`);
        }
    });
}

// 直接加载数据并更新
async function loadAndUpdate() {
    console.log('直接加载数据...');
    
    try {
        // 1. 加载模型数据
        const response = await fetch('/api/models');
        if (!response.ok) {
            throw new Error(`API响应错误: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('📊 数据加载成功:', data);
        
        // 2. 直接更新DOM
        updateDashboardDirectly(data);
        
        // 3. 更新模型表格
        if (document.getElementById('modelsTableBody')) {
            updateModelsTableDirectly(data.models || []);
        }
        
        console.log('✅ 数据更新完成');
        
    } catch (error) {
        console.error('❌ 数据加载失败:', error);
        showErrorDirectly(error.message);
    }
}

// 直接更新仪表板
function updateDashboardDirectly(data) {
    console.log('更新仪表板...');
    
    const totalModels = data.count || 0;
    const activeModels = data.models?.filter(m => m.status === 'active').length || 0;
    
    // 更新统计卡片
    updateElement('totalModels', totalModels);
    updateElement('activeModels', activeModels);
    
    // 更新进度条
    const progressBar = document.getElementById('activeModelsProgress');
    if (progressBar && totalModels > 0) {
        const percentage = (activeModels / totalModels) * 100;
        progressBar.style.width = `${percentage}%`;
        progressBar.style.background = percentage >= 70 ? 
            'linear-gradient(135deg, #10b981, #059669)' : 
            'linear-gradient(135deg, #f59e0b, #d97706)';
    }
    
    // 更新当前模型
    let currentModel = '未设置';
    if (data.models && data.models.length > 0) {
        const sortedModels = [...data.models].sort((a, b) => {
            const timeA = a.last_used ? new Date(a.last_used).getTime() : 0;
            const timeB = b.last_used ? new Date(b.last_used).getTime() : 0;
            return timeB - timeA;
        });
        
        if (sortedModels[0] && sortedModels[0].last_used) {
            currentModel = sortedModels[0].name;
            if (currentModel.length > 15) {
                currentModel = currentModel.substring(0, 15) + '...';
            }
        }
    }
    updateElement('currentModel', currentModel);
    
    // 更新成功率
    let overallSuccessRate = 0;
    if (data.models && data.models.length > 0) {
        const modelsWithPerformance = data.models.filter(m => m.performance && m.performance.success_rate);
        if (modelsWithPerformance.length > 0) {
            const totalRate = modelsWithPerformance.reduce((sum, m) => sum + m.performance.success_rate, 0);
            overallSuccessRate = (totalRate / modelsWithPerformance.length) * 100;
        }
    }
    updateElement('successRate', overallSuccessRate.toFixed(1) + '%');
    
    console.log('📈 仪表板更新完成:', { totalModels, activeModels, currentModel, overallSuccessRate });
}

// 直接更新模型表格
function updateModelsTableDirectly(models) {
    console.log('更新模型表格...', models.length, '个模型');
    
    const tbody = document.getElementById('modelsTableBody');
    if (!tbody) {
        console.error('找不到模型表格容器');
        return;
    }
    
    if (!models || models.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center py-5 text-muted">
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
                        <button class="btn btn-outline-info" title="查看详情">
                            <i class="bi bi-info-circle"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    });
    
    tbody.innerHTML = html;
    console.log('✅ 模型表格更新完成');
}

// 更新元素
function updateElement(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    } else {
        console.error(`找不到元素: ${id}`);
    }
}

// 显示错误
function showErrorDirectly(message) {
    const container = document.getElementById('realtimeStatus');
    if (container) {
        container.innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle"></i>
                ${message}
            </div>
        `;
    }
}

// 初始化
console.log('🚀 调试脚本初始化');
checkElements();

// 延迟执行，确保页面加载完成
setTimeout(() => {
    console.log('⏰ 开始加载数据...');
    loadAndUpdate();
}, 1000);

// 添加手动刷新按钮
function addRefreshButton() {
    const header = document.querySelector('.main-header');
    if (header) {
        const button = document.createElement('button');
        button.className = 'btn btn-primary btn-sm';
        button.innerHTML = '<i class="bi bi-arrow-clockwise"></i> 手动刷新';
        button.style.marginLeft = '10px';
        button.onclick = loadAndUpdate;
        header.appendChild(button);
        console.log('✅ 添加手动刷新按钮');
    }
}

// 添加调试按钮
setTimeout(addRefreshButton, 1500);

console.log('🔧 调试脚本加载完成');