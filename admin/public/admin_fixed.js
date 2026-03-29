'bi-x-circle' :
                        action.type === 'primary' ? 'bi-arrow-right-circle' : 'bi-info-circle';
        
        html += `
            <div class="mb-3 p-3 rounded bg-dark-bg-light">
                <div class="d-flex justify-content-between align-items-center">
                    <div class="d-flex align-items-center">
                        <i class="bi ${typeIcon} ${typeClass} me-2"></i>
                        <strong class="${typeClass}">${action.title}</strong>
                    </div>
                    <small class="text-muted">${time}</small>
                </div>
                <div class="small text-muted mt-1">${action.description}</div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// 显示通知
function showToast(title, message, type = 'info') {
    const toastElement = document.getElementById('liveToast');
    const toastTitle = document.getElementById('toastTitle');
    const toastMessage = document.getElementById('toastMessage');
    const toastTime = document.getElementById('toastTime');
    
    if (!toastElement || !toastTitle || !toastMessage || !toastTime) return;
    
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

// 刷新当前标签页
function refreshCurrentTab() {
    loadTabData(state.currentTab);
    showToast('刷新', '数据已刷新', 'info');
}

// 渲染性能报告
function renderPerformanceReport(data) {
    const container = document.getElementById('performanceContent');
    if (!container) return;
    
    if (!data || data.error) {
        container.innerHTML = `
            <div class="alert alert-warning">
                <i class="bi bi-exclamation-triangle"></i>
                ${data?.error || '没有性能数据'}
            </div>
        `;
        return;
    }
    
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
    if (!container) return;
    
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

// 全局函数（供HTML内联调用）
window.testSingleModel = testSingleModel;
window.switchToModel = switchToModel;
window.showModelDetails = showModelDetails;
window.loadModels = loadModels;
window.runAutoSwitch = runAutoSwitch;
window.testAllModels = testAllModels;
window.createBackup = createBackup;