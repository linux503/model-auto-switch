                <h6>性能数据</h6>
                <table class="table table-sm table-borderless">
                    <tr>
                        <td width="40%"><strong>成功率:</strong></td>
                        <td>
                            <div class="progress" style="height: 20px;">
                                <div class="progress-bar bg-success" 
                                     style="width: ${(model.performance.success_rate || 0) * 100}%">
                                    ${((model.performance.success_rate || 0) * 100).toFixed(1)}%
                                </div>
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td><strong>响应时间:</strong></td>
                        <td>${model.performance.avg_response_time || 0}ms</td>
                    </tr>
                    <tr>
                        <td><strong>测试次数:</strong></td>
                        <td>${model.performance.total_tests || 0}</td>
                    </tr>
                </table>
            </div>
        `;
    }
    
    content.innerHTML = html;
    modal.show();
}

// 测试单个模型
async function testModel(modelId) {
    try {
        const response = await fetch('/api/models/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ modelId })
        });
        
        if (response.ok) {
            const data = await response.json();
            showToast('模型测试', data.message, data.success ? 'success' : 'warning');
        } else {
            showToast('错误', '测试模型失败', 'danger');
        }
    } catch (error) {
        console.error('测试模型失败:', error);
        showToast('错误', '测试模型失败', 'danger');
    }
}

// 切换模型
async function switchModel(modelId) {
    try {
        const response = await fetch('/api/models/switch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ modelId, reason: 'manual_switch' })
        });
        
        if (response.ok) {
            const data = await response.json();
            showToast('切换成功', data.message, 'success');
        } else {
            showToast('错误', '切换模型失败', 'danger');
        }
    } catch (error) {
        console.error('切换模型失败:', error);
        showToast('错误', '切换模型失败', 'danger');
    }
}

// 禁用模型
async function disableModel(modelName) {
    if (!confirm(`确定要禁用模型 "${modelName}" 吗？`)) {
        return;
    }
    
    // 这里需要实现禁用模型的逻辑
    showToast('禁用模型', `已禁用模型 ${modelName}`, 'warning');
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
        'info': 'bg-info text-white'
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

// 全局函数（供HTML内联调用）
window.testModel = testModel;
window.switchModel = switchModel;
window.showModelDetail = showModelDetail;
window.disableModel = disableModel;