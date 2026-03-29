    let options = {
        method: method,
        headers: { 'Content-Type': 'application/json' }
    };
    
    if (method === 'POST' && requestBody) {
        try {
            options.body = requestBody;
        } catch (error) {
            showToast('错误', '请求体JSON格式错误', 'danger');
            return;
        }
    }
    
    try {
        showToast('测试中', `正在测试 ${method} ${endpoint}...`, 'info');
        
        const response = await fetch(endpoint, options);
        const data = await response.json();
        
        document.getElementById('apiResponse').textContent = JSON.stringify(data, null, 2);
        
        if (response.ok) {
            showToast('API测试', '请求成功', 'success');
        } else {
            showToast('API测试', `请求失败: ${data.error || response.status}`, 'warning');
        }
    } catch (error) {
        console.error('API测试失败:', error);
        document.getElementById('apiResponse').textContent = `错误: ${error.message}`;
        showToast('错误', 'API测试失败', 'danger');
    }
}

// 显示添加模型模态框
function showAddModelModal() {
    const modal = new bootstrap.Modal(document.getElementById('addModelModal'));
    modal.show();
}

// 提交添加模型
async function submitAddModel() {
    const form = document.getElementById('addModelForm');
    const formData = new FormData(form);
    
    const modelData = {
        name: form.querySelector('input[placeholder*="模型名称"]').value,
        provider: form.querySelector('input[placeholder*="Provider"]').value,
        priority: parseInt(form.querySelector('input[type="number"]').value),
        status: form.querySelector('select').value,
        notes: form.querySelector('textarea').value
    };
    
    // 这里需要实现添加模型的API调用
    showToast('添加模型', '添加模型功能开发中', 'info');
    
    // 关闭模态框
    const modal = bootstrap.Modal.getInstance(document.getElementById('addModelModal'));
    modal.hide();
    
    // 刷新模型列表
    setTimeout(() => loadModels(), 1000);
}

// 显示通知
function showToast(title, message, type = 'info') {
    const toastElement = document.getElementById('liveToast');
    const toastTitle = document.getElementById('toastTitle');
    const toastMessage = document.getElementById('toastMessage');
    const toastTime = document.getElementById('toastTime');
    
    // 设置样式
    const typeClasses = {
        'success': 'bg-success text-white',
        'warning': 'bg-warning text-dark',
        'danger': 'bg-danger text-white',
        'info': 'bg-info text-white',
        'primary': 'bg-primary text-white'
    };
    
    toastElement.className = `toast ${typeClasses[type] || 'bg-dark text-light'}`;
    
    // 设置内容
    toastTitle.textContent = title;
    toastMessage.textContent = message;
    toastTime.textContent = new Date().toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit'
    });
    
    // 显示通知
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 3000
    });
    toast.show();
    
    // 添加到最近操作
    addRecentAction(title, message, type);
}

// 启动时钟
function startClock() {
    function updateClock() {
        const now = new Date();
        document.getElementById('serverTime').textContent = 
            now.toLocaleTimeString('zh-CN', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
    }
    
    updateClock();
    setInterval(updateClock, 1000);
}

// 刷新所有数据
function refreshAllData() {
    switch(currentTab) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'models':
            loadModels();
            break;
        case 'performance':
            loadPerformanceData();
            break;
        case 'logs':
            loadLogs('all');
            break;
        case 'settings':
            loadSettings();
            break;
    }
    showToast('刷新', '数据已刷新', 'info');
}

// 加载性能数据
async function loadPerformanceData() {
    try {
        const response = await fetch('/api/performance');
        if (response.ok) {
            performanceData = await response.json();
            renderPerformanceReport(performanceData);
        }
    } catch (error) {
        console.error('加载性能数据失败:', error);
        document.getElementById('performanceContent').innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle"></i>
                加载性能数据失败: ${error.message}
            </div>
        `;
    }
}

// 加载日志
async function loadLogs(type = 'all') {
    try {
        const response = await fetch(`/api/logs?type=${type}&limit=100`);
        if (response.ok) {
            const data = await response.json();
            renderLogs(data.logs);
        }
    } catch (error) {
        console.error('加载日志失败:', error);
        document.getElementById('logContent').textContent = `加载日志失败: ${error.message}`;
    }
}

// 渲染性能报告
function renderPerformanceReport(data) {
    const container = document.getElementById('performanceContent');
    
    if (!data || data.error) {
        container.innerHTML = `
            <div class="alert alert-warning">
                <i class="bi bi-exclamation-triangle"></i>
                ${data?.error || '没有性能数据'}
            </div>
        `;
        return;
    }
    
    // 这里可以添加性能报告的具体渲染逻辑
    container.innerHTML = `
        <div class="alert alert-info">
            <i class="bi bi-info-circle"></i>
            性能报告功能开发中，数据已加载
        </div>
        <pre class="bg-dark p-3 rounded">${JSON.stringify(data, null, 2)}</pre>
    `;
}

// 渲染日志
function renderLogs(logs) {
    const container = document.getElementById('logContent');
    
    if (!logs || logs.length === 0) {
        container.textContent = '暂无日志数据';
        return;
    }
    
    let html = '';
    logs.forEach(log => {
        const levelClass = log.level === 'error' ? 'text-danger' : 
                          log.level === 'warning' ? 'text-warning' : 'text-info';
        
        html += `<span class="${levelClass}">[${log.timestamp}]</span> ${log.message}\n`;
    });
    
    container.textContent = html;
}

// 过滤日志
function filterLogs(searchText) {
    const container = document.getElementById('logContent');
    const text = container.textContent;
    const lines = text.split('\n');
    
    if (!searchText) {
        loadLogs('all');
        return;
    }
    
    const filtered = lines.filter(line => 
        line.toLowerCase().includes(searchText.toLowerCase())
    );
    
    container.textContent = filtered.join('\n') || '没有匹配的日志';
}

// 全局函数（供HTML内联调用）
window.testModel = testModel;
window.switchModel = switchModel;
window.showModelDetail = showModelDetail;
window.loadModels = loadModels;