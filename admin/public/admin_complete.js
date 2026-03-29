'通过' : '失败';
            showToast('测试完成', `${model.name} 测试${status}`, data.success ? 'success' : 'warning');
            
            // 刷新模型列表
            setTimeout(loadModels, 1000);
        } else {
            showToast('错误', '测试模型失败', 'danger');
        }
    } catch (error) {
        console.error('测试模型失败:', error);
        showToast('错误', '测试模型失败', 'danger');
    }
}

// 切换到模型
async function switchModel(modelId) {
    console.log('切换模型:', modelId);
    
    const model = modelsData.find(m => m.id === modelId);
    if (!model) {
        showToast('错误', '未找到模型', 'danger');
        return;
    }
    
    if (!confirm(`确定要切换到模型 "${model.name}" 吗？`)) {
        return;
    }
    
    try {
        showToast('切换中', `正在切换到 ${model.name}...`, 'info');
        
        const response = await fetch('/api/models/switch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ modelId, reason: 'manual_switch' })
        });
        
        if (response.ok) {
            const data = await response.json();
            showToast('切换成功', data.message, 'success');
            
            // 刷新模型列表
            setTimeout(loadModels, 1000);
        } else {
            showToast('错误', '切换模型失败', 'danger');
        }
    } catch (error) {
        console.error('切换模型失败:', error);
        showToast('错误', '切换模型失败', 'danger');
    }
}

// 显示模型详情
function showModelDetail(modelId) {
    console.log('显示模型详情:', modelId);
    
    const model = modelsData.find(m => m.id === modelId);
    if (!model) {
        showToast('错误', '未找到模型信息', 'danger');
        return;
    }
    
    // 这里可以显示模态框
    showToast('模型详情', `查看 ${model.name} 的详细信息`, 'info');
}

// 运行自动切换
async function runAutoSwitch() {
    console.log('运行自动切换');
    
    try {
        showToast('执行中', '正在运行自动切换...', 'info');
        
        const response = await fetch('/api/auto-switch/run', {
            method: 'POST'
        });
        
        if (response.ok) {
            const data = await response.json();
            showToast('完成', data.message, 'success');
            
            // 刷新模型列表
            setTimeout(loadModels, 2000);
        } else {
            showToast('错误', '执行自动切换失败', 'danger');
        }
    } catch (error) {
        console.error('运行自动切换失败:', error);
        showToast('错误', '执行自动切换失败', 'danger');
    }
}

// 测试所有模型
async function testAllModels() {
    console.log('测试所有模型');
    
    if (!modelsData || modelsData.length === 0) {
        showToast('提示', '没有可测试的模型', 'info');
        return;
    }
    
    const activeModels = modelsData.filter(m => m.status === 'active');
    if (activeModels.length === 0) {
        showToast('提示', '没有活跃的模型', 'info');
        return;
    }
    
    if (!confirm(`确定要测试所有 ${activeModels.length} 个活跃模型吗？`)) {
        return;
    }
    
    showToast('开始测试', `开始测试 ${activeModels.length} 个模型`, 'info');
    
    let successCount = 0;
    let failCount = 0;
    
    for (const model of activeModels) {
        try {
            const response = await fetch('/api/models/test', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ modelId: model.id })
            });
            
            if (response.ok) {
                const result = await response.json();
                if (result.success) {
                    successCount++;
                } else {
                    failCount++;
                }
            } else {
                failCount++;
            }
            
            // 延迟避免请求过快
            await new Promise(resolve => setTimeout(resolve, 500));
        } catch (error) {
            console.error(`测试模型 ${model.name} 失败:`, error);
            failCount++;
        }
    }
    
    showToast('测试完成', `成功: ${successCount}, 失败: ${failCount}`, successCount > 0 ? 'success' : 'warning');
    loadModels();
}

// 创建备份
async function createBackup() {
    console.log('创建备份');
    
    try {
        showToast('创建中', '正在创建备份...', 'info');
        
        const response = await fetch('/api/backup', {
            method: 'POST'
        });
        
        if (response.ok) {
            const data = await response.json();
            showToast('备份成功', data.message, 'success');
        } else {
            showToast('错误', '创建备份失败', 'danger');
        }
    } catch (error) {
        console.error('创建备份失败:', error);
        showToast('错误', '创建备份失败', 'danger');
    }
}

// 更新实时状态
function updateRealtimeStatus(data) {
    console.log('更新实时状态:', data);
    
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
                        <div class="status-item">
                            <div class="d-flex align-items-center mb-2">
                                <i class="bi bi-check-circle text-success me-2"></i>
                                <small class="text-muted">活跃模型</small>
                            </div>
                            <div class="h4 fw-bold">${activeModels}<span class="h6 text-muted">/${totalModels}</span></div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="status-item mb-4">
                            <div class="d-flex align-items-center mb-2">
                                <i class="bi bi-lightning text-warning me-2"></i>
                                <small class="text-muted">自动切换</small>
                            </div>
                            <div class="h4">
                                <span class="badge bg-${autoSwitch === '启用' ? 'success' : 'warning'}">
                                    ${autoSwitch}
                                </span>
                            </div>
                        </div>
                        <div class="status-item">
                            <div class="d-flex align-items-center mb-2">
                                <i class="bi bi-clock text-info me-2"></i>
                                <small class="text-muted">最后更新</small>
                            </div>
                            <div class="h6 text-muted">${new Date(data.timestamp).toLocaleTimeString('zh-CN')}</div>
                        </div>
                    </div>
                </div>
            `;
        }
        
        container.innerHTML = html;
    } catch (error) {
        console.error('更新实时状态错误:', error);
        container.innerHTML = `
            <div class="alert alert-warning">
                <i class="bi bi-exclamation-triangle"></i>
                实时状态解析错误
            </div>
        `;
    }
}

// 显示通知
function showToast(title, message, type = 'info') {
    console.log('显示通知:', { title, message, type });
    
    const toastElement = document.getElementById('liveToast');
    const toastTitle = document.getElementById('toastTitle');
    const toastMessage = document.getElementById('toastMessage');
    const toastTime = document.getElementById('toastTime');
    
    if (!toastElement || !toastTitle || !toastMessage || !toastTime) {
        console.error('找不到通知元素');
        return;
    }
    
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
    try {
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: 3000
        });
        toast.show();
    } catch (error) {
        console.error('显示通知失败:', error);
    }
}

// 启动时钟
function startClock() {
    console.log('启动时钟');
    
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

// 刷新所有数据
function refreshAllData() {
    console.log('刷新所有数据');
    
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
            loadLogs();
            break;
        case 'settings':
            loadSettings();
            break;
    }
    showToast('刷新', '数据已刷新', 'info');
}

// 加载性能数据
async function loadPerformanceData() {
    console.log('加载性能数据');
    // 这里实现性能数据加载
    showToast('提示', '性能分析功能开发中', 'info');
}

// 加载日志
async function loadLogs() {
    console.log('加载日志');
    // 这里实现日志加载
    showToast('提示', '日志功能开发中', 'info');
}

// 加载设置
async function loadSettings() {
    console.log('加载设置');
    // 这里实现设置加载
    showToast('提示', '设置功能开发中', 'info');
}

// 全局函数（供HTML内联调用）
window.testModel = testModel;
window.switchModel = switchModel;
window.showModelDetail = showModelDetail;
window.loadModels = loadModels;
window.runAutoSwitch = runAutoSwitch;
window.testAllModels = testAllModels;
window.createBackup = createBackup;

console.log('OpenClaw 模型管理后台 - 初始化完成');