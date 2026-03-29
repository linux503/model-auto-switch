// OpenClaw 模型管理系统 - 增强版 JavaScript
// 功能：数据加载、交互操作、实时更新

class ModelManagerDashboard {
    constructor() {
        this.currentData = null;
        this.autoRefreshInterval = null;
        this.isLoading = false;
        this.currentView = 'table'; // 'table' 或 'card'
        this.init();
    }
    
    init() {
        console.log('🚀 模型管理系统增强版初始化...');
        
        // 加载数据
        this.loadData();
        
        // 设置自动刷新（每30秒）
        this.autoRefreshInterval = setInterval(() => {
            if (!document.hidden && !this.isLoading) {
                this.loadData();
            }
        }, 30000);
        
        // 绑定事件
        this.bindEvents();
        
        // 初始化标签页
        this.switchTab('dashboard');
    }
    
    bindEvents() {
        // 刷新按钮
        document.getElementById('refreshBtn')?.addEventListener('click', () => this.loadData());
        
        // 窗口可见性变化
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.loadData();
            }
        });
        
        // 键盘快捷键
        document.addEventListener('keydown', (e) => {
            // Ctrl+R 刷新
            if (e.ctrlKey && e.key === 'r') {
                e.preventDefault();
                this.loadData();
            }
            // F5 刷新
            if (e.key === 'F5') {
                e.preventDefault();
                this.loadData();
            }
        });
    }
    
    async loadData() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoading('加载模型数据...');
        
        try {
            // 这里应该调用后端 API 获取真实数据
            // 暂时使用模拟数据
            await this.loadMockData();
            
            // 更新 UI
            this.updateDashboard();
            this.updateModelsTable();
            this.updateLogs();
            this.updateSettings();
            this.updatePerformance();
            
            this.showToast('数据加载成功', 'success');
        } catch (error) {
            console.error('加载数据失败:', error);
            this.showToast(`加载失败: ${error.message}`, 'error');
        } finally {
            this.isLoading = false;
            this.hideLoading();
        }
    }
    
    async loadMockData() {
        // 模拟 API 请求延迟
        await new Promise(resolve => setTimeout(resolve, 800));
        
        // 模拟数据
        this.currentData = {
            current_model: 'aicodee/MiniMax-M2.5-highspeed',
            current_model_info: {
                name: 'aicodee/MiniMax-M2.5-highspeed',
                provider: 'aicodee',
                priority: 1,
                status: 'active',
                last_used: '2026-03-29T18:10:00Z',
                added_at: '2026-03-29'
            },
            last_check: '2026-03-29 18:12:30',
            active_count: 18,
            total_count: 19,
            auto_switch_enabled: true,
            check_interval: 5,
            notify_on_switch: true,
            notify_on_failure: true,
            models: [
                {
                    id: 'M001',
                    name: 'deepseek/deepseek-chat',
                    provider: 'deepseek',
                    status: 'active',
                    priority: 3,
                    last_used: '2026-03-29T09:49:00Z',
                    added_at: '2026-03-19',
                    notes: '默认备用模型'
                },
                {
                    id: 'M002',
                    name: 'deepseek/deepseek-reasoner',
                    provider: 'deepseek',
                    status: 'active',
                    priority: 4,
                    last_used: null,
                    added_at: '2026-03-19',
                    notes: '推理模型'
                },
                {
                    id: 'M018',
                    name: 'aicodee/MiniMax-M2.5-highspeed',
                    provider: 'aicodee',
                    status: 'active',
                    priority: 1,
                    last_used: '2026-03-29T18:10:00Z',
                    added_at: '2026-03-29',
                    notes: '主模型，高速版本'
                },
                {
                    id: 'M019',
                    name: 'aicodee/MiniMax-M2.7-highspeed',
                    provider: 'aicodee',
                    status: 'active',
                    priority: 2,
                    last_used: null,
                    added_at: '2026-03-29',
                    notes: '主要备用，更高速版本'
                }
            ],
            performance_stats: {
                'aicodee/MiniMax-M2.5-highspeed': {
                    total_tests: 15,
                    successful_tests: 14,
                    failed_tests: 1,
                    response_times: [1200, 1100, 1300, 1250, 1150],
                    last_test_time: '2026-03-29T18:12:00Z',
                    avg_response_time: 1200,
                    success_rate: 0.933
                },
                'deepseek/deepseek-chat': {
                    total_tests: 42,
                    successful_tests: 40,
                    failed_tests: 2,
                    response_times: [800, 850, 900, 820, 880],
                    last_test_time: '2026-03-29T17:30:00Z',
                    avg_response_time: 850,
                    success_rate: 0.952
                },
                'deepseek/deepseek-reasoner': {
                    total_tests: 8,
                    successful_tests: 7,
                    failed_tests: 1,
                    response_times: [1500, 1600, 1550],
                    last_test_time: '2026-03-29T16:45:00Z',
                    avg_response_time: 1550,
                    success_rate: 0.875
                },
                'aicodee/MiniMax-M2.7-highspeed': {
                    total_tests: 3,
                    successful_tests: 3,
                    failed_tests: 0,
                    response_times: [1100, 1050, 1150],
                    last_test_time: '2026-03-29T18:00:00Z',
                    avg_response_time: 1100,
                    success_rate: 1.0
                }
            },
            switch_log: [
                {
                    timestamp: '2026-03-29 18:12:30',
                    from: 'deepseek/deepseek-chat',
                    to: 'aicodee/MiniMax-M2.5-highspeed',
                    reason: '自动切换 - 性能优化',
                    success: true,
                    notified: true
                },
                {
                    timestamp: '2026-03-29 17:54:00',
                    from: 'openai_betterclaude/gpt-5.4',
                    to: 'deepseek/deepseek-chat',
                    reason: '手动切换',
                    success: true,
                    notified: true
                },
                {
                    timestamp: '2026-03-29 17:30:00',
                    from: 'deepseek/deepseek-chat',
                    to: 'openai_betterclaude/gpt-5.4',
                    reason: '测试新模型',
                    success: true,
                    notified: false
                },
                {
                    timestamp: '2026-03-29 16:45:00',
                    from: 'aicodee/MiniMax-M2.5-highspeed',
                    to: 'deepseek/deepseek-reasoner',
                    reason: '自动切换 - 模型故障',
                    success: false,
                    error: '连接超时',
                    notified: true
                }
            ],
            settings: {
                auto_switch_enabled: true,
                check_interval_minutes: 5,
                max_retries: 3,
                retry_delay_seconds: 2,
                test_timeout_seconds: 15,
                notify_on_switch: true,
                notify_on_failure: true,
                telegram_chat_id: 'telegram:2039643883',
                performance_weight_response_time: 0.4,
                performance_weight_success_rate: 0.6,
                min_success_rate_for_auto_switch: 0.7,
                max_response_time_ms: 30000,
                log_retention_days: 7,
                max_log_size_mb: 10,
                backup_enabled: true,
                backup_interval_hours: 24
            }
        };
    }
    
    updateDashboard() {
        if (!this.currentData) return;
        
        const data = this.currentData;
        
        // 更新状态栏
        document.getElementById('currentModel').textContent = data.current_model || '未设置';
        document.getElementById('activeCount').textContent = data.active_count;
        document.getElementById('totalCount').textContent = data.total_count;
        document.getElementById('autoSwitchStatus').textContent = data.auto_switch_enabled ? '启用' : '禁用';
        document.getElementById('lastCheck').textContent = data.last_check.split(' ')[1] || '--:--';
        
        // 更新当前模型卡片
        document.getElementById('currentModelName').textContent = data.current_model;
        document.getElementById('currentModelProvider').textContent = data.current_model_info?.provider || '--';
        
        // 更新性能统计
        const stats = data.performance_stats?.[data.current_model] || {};
        document.getElementById('currentSuccessRate').textContent = stats.success_rate ? `${(stats.success_rate * 100).toFixed(1)}%` : '--%';
        document.getElementById('currentResponseTime').textContent = stats.avg_response_time ? `${Math.round(stats.avg_response_time)}ms` : '--ms';
        document.getElementById('currentTests').textContent = stats.total_tests || '--';
        
        // 计算综合评分
        const score = this.calculateModelScore(data.current_model, stats);
        document.getElementById('currentScore').textContent = score.toFixed(3);
        
        // 更新自动切换设置
        document.getElementById('autoSwitchToggle').checked = data.auto_switch_enabled;
        document.getElementById('autoSwitchText').textContent = data.auto_switch_enabled ? '启用' : '禁用';
        document.getElementById('checkInterval').value = data.check_interval || 5;
        document.getElementById('notifyToggle').checked = data.notify_on_switch;
        document.getElementById('notifyText').textContent = data.notify_on_switch ? '启用' : '禁用';
        
        // 更新最佳模型推荐
        this.updateBestModels();
    }
    
    calculateModelScore(modelName, stats) {
        if (!stats || !stats.total_tests) return 0.5;
        
        const settings = this.currentData?.settings || {};
        const weightRT = settings.performance_weight_response_time || 0.4;
        const weightSR = settings.performance_weight_success_rate || 0.6;
        
        // 响应时间分数（越短越好）
        const maxRT = settings.max_response_time_ms || 30000;
        const rtScore = 1.0 - Math.min(stats.avg_response_time / maxRT, 1.0);
        
        // 成功率分数
        const srScore = stats.success_rate || 0;
        
        // 综合评分
        let score = (rtScore * weightRT) + (srScore * weightSR);
        
        // 根据优先级调整
        const model = this.currentData?.models?.find(m => m.name === modelName);
        if (model) {
            const priority = model.priority || 10;
            const priorityFactor = 1.0 / (priority * 0.1);
            score *= (0.7 + 0.3 * priorityFactor);
        }
        
        return Math.min(Math.max(score, 0), 1);
    }
    
    updateBestModels() {
        const container = document.getElementById('bestModelsList');
        if (!container || !this.currentData) return;
        
        const models = this.currentData.models || [];
        const stats = this.currentData.performance_stats || {};
        
        // 计算每个模型的评分
        const scoredModels = models
            .filter(model => model.status === 'active')
            .map(model => {
                const modelStats = stats[model.name] || {};
                const score = this.calculateModelScore(model.name, modelStats);
                return { ...model, score, stats: modelStats };
            })
            .sort((a, b) => b.score - a.score)
            .slice(0, 3); // 取前3名
        
        if (scoredModels.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-chart-bar"></i>
                    <div>暂无模型数据</div>
                </div>
            `;
            return;
        }
        
        let html = '';
        scoredModels.forEach((model, index) => {
            const isCurrent = model.name === this.currentData.current_model;
            const medal = ['🥇', '🥈', '🥉'][index] || '🏅';
            const scorePercent = Math.round(model.score * 1000) / 10;
            
            html += `
                <div class="model-card ${isCurrent ? 'current' : ''}" style="margin-bottom: 15px;">
                    <div class="model-card-header">
                        <div>
                            <div class="model-name">${medal} ${model.name}</div>
                            <div class="model-provider">${model.provider} • 优先级: ${model.priority}</div>
                        </div>
                        ${isCurrent ? '<span class="badge badge-new">当前</span>' : ''}
                    </div>
                    
                    <div class="model-stats-small">
                        <div class="model-stat">
                            <div class="model-stat-value">${scorePercent}%</div>
                            <div class="model-stat-label">综合评分</div>
                        </div>
                        <div class="model-stat">
                            <div class="model-stat-value">${model.stats.success_rate ? (model.stats.success_rate * 100).toFixed(1) + '%' : '--%'}</div>
                            <div class="model-stat-label">成功率</div>
                        </div>
                        <div class="model-stat">
                            <div class="model-stat-value">${model.stats.avg_response_time ? Math.round(model.stats.avg_response_time) + 'ms' : '--ms'}</div>
                            <div class="model-stat-label">响应时间</div>
                        </div>
                        <div class="model-stat">
                            <div class="model-stat-value">${model.stats.total_tests || '--'}</div>
                            <div class="model-stat-label">测试次数</div>
                        </div>
                    </div>
                    
                    <div class="score-bar">
                        <div class="score-fill ${model.score >= 0.8 ? 'score-high' : model.score >= 0.6 ? 'score-medium' : 'score-low'}" 
                             style="width: ${model.score * 100}%"></div>
                    </div>
                    
                    <div class="action-buttons" style="margin-top: 10px;">
                        ${!isCurrent ? `
                            <button class="btn btn-primary btn-sm" onclick="dashboard.switchModel('${model.name}')">
                                <i class="fas fa-exchange-alt"></i> 切换
                            </button>
                        ` : ''}
                        <button class="btn btn-secondary btn-sm" onclick="dashboard.testModel('${model.name}')">
                            <i class="fas fa-vial"></i> 测试
                        </button>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }
    
    updateModelsTable() {
        const tbody = document.getElementById('modelsTableBody');
        if (!tbody || !this.currentData) return;
        
        const models = this.currentData.models || [];
        const stats = this.currentData.performance_stats || {};
        const currentModel = this.currentData.current_model;
        
        let html = '';
        models.forEach(model => {
            const isCurrent = model.name === currentModel;
            const modelStats = stats[model.name] || {};
            const score = this.calculateModelScore(model.name, modelStats);
            const scorePercent = Math.round(score * 1000) / 10;
            
            // 确定评分颜色类
            let scoreClass = 'score-low';
            if (score >= 0.8) scoreClass = 'score-high';
            else if (score >= 0.6) scoreClass = 'score-medium';
            
            html += `
                <tr class="${isCurrent ? 'model-current' : ''}">
                    <td>${model.id}</td>
                    <td>
                        <strong>${model.name}</strong>
                        ${isCurrent ? ' <span class="badge badge-new">当前</span>' : ''}
                        <br>
                        <small style="color: #94a3b8;">${model.notes || ''}</small>
                    </td>
                    <td>${model.provider}</td>
                    <td>
                        <span class="status-badge ${model.status === 'active' ? 'status-active' : 'status-disabled'}">
                            ${model.status === 'active' ? '活跃' : '禁用'}
                        </span>
                    </td>
                    <td>
                        <span class="priority-badge priority-${Math.min(model.priority, 5)}">
                            ${model.priority}
                        </span>
                    </td>
                    <td>
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span>${scorePercent}%</span>
                            <div class="score-bar" style="flex: 1;">
                                <div class="score-fill ${scoreClass}" style="width: ${score * 100}%"></div>
                            </div>
                        </div>
                    </td>
                    <td>${modelStats.success_rate ? (modelStats.success_rate * 100).toFixed(1) + '%' : '--%'}</td>
                    <td>${modelStats.avg_response_time ? Math.round(modelStats.avg_response_time) + 'ms' : '--ms'}</td>
                    <td>${model.last_used ? model.last_used.substring(0, 10) : '从未使用'}</td>
                    <td>
                        <div class="action-buttons" style="justify-content: flex-start;">
                            ${!isCurrent ? `
                                <button class="btn btn-primary btn-sm" onclick="dashboard.switchModel('${model.name}')">
                                    <i class="fas fa-exchange-alt"></i>
                                </button>
                            ` : ''}
                            <button class="btn btn-secondary btn-sm" onclick="dashboard.testModel('${model.name}')">
                                <i class="fas fa-vial"></i>
                            </button>
                            ${model.status === 'active' ? `
                                <button class="btn btn-danger btn-sm" onclick="dashboard.toggleModelStatus('${model.id}', 'disabled')">
                                    <i class="fas fa-ban"></i>
                                </button>
                            ` : `
                                <button class="btn btn-success btn-sm" onclick="dashboard.toggleModelStatus('${model.id}', 'active')">
                                    <i class="fas fa-check"></i>
                                </button>
                            `}
                        </div>
                    </td>
                </tr>
            `;
        });
        
        tbody.innerHTML = html;
    }
    
    updateLogs() {
        const container = document.getElementById('logsContainer');
        if (!container || !this.currentData) return;
        
        const logs = this.currentData.switch_log || [];
        
        if (logs.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-history"></i>
                    <div>暂无切换日志</div>
                </div>
            `;
            return;
        }
        
        let html = '';
        logs.slice(-10).reverse().forEach(log => {
            const success = log.success !== false;
            const icon = success ? '✓' : '✗';
            const colorClass = success ? 'log-success' : 'log-error';
            
            html += `
                <div class="log-entry ${colorClass}">
                    <div class="log-time">
                        <span>${log.timestamp}</span>
                        <span style="color: ${success ? '#10b981' : '#ef4444'}">
                            ${icon} ${success ? '成功' : '失败'}
                        </span>
                    </div>
                    <div class="log-message">
                        <strong>${log.from || '?'}</strong> 
                        <i class="fas fa-arrow-right" style="margin: 0 10px; color: #94a3b8;"></i>
                        <strong>${log.to || '?'}</strong>
                        <span style="color: #94a3b8; margin-left: 10px;">(${log.reason})</span>
                        ${log.error ? `<br><small style="color: #ef4444;">错误: ${log.error}</small>` : ''}
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }
    
    updateSettings() {
        // 设置已经在 updateDashboard 中更新了
    }
    
    updatePerformance() {
        // 这里可以添加性能图表的更新逻辑
        // 暂时留空，后续可以集成图表库
    }
    
    // 交互方法
    switchTab(tabId) {
        // 隐藏所有标签页内容
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });
        
        // 移除所有标签的激活状态
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.remove('active');
        });
        
        // 显示选中的标签页
        const tabElement = document.getElementById(`tab-${tabId}`);
        if (tabElement) {
            tabElement.classList.add('active');
        }
        
        // 激活对应的标签
        const tabButton = Array.from(document.querySelectorAll('.tab')).find(tab => 
            tab.textContent.includes(this.getTabName(tabId))
        );
        if (tabButton) {
            tabButton.classList.add('active');
        }
        
        // 如果是模型标签页，确保表格是最新的
        if (tabId === 'models') {
            this.updateModelsTable();
        }
        
        // 如果是日志标签页，确保日志是最新的
        if (tabId === 'logs') {
            this.updateLogs();
        }
    }
    
    getTabName(tabId) {
        const tabNames = {
            'dashboard': '仪表板',
            'models': '模型列表',
            'logs': '切换日志',
            'settings': '系统设置',
            'performance': '性能分析'
        };
        return tabNames[tabId] || tabId;
    }
    
    async testCurrentModel() {
        await this.testModel(this.currentData?.current_model);
    }
    
    async testModel(modelName) {
        if (!modelName) {
            this.showToast('请先选择要测试的模型', 'warning');
            return;
        }
        
        this.showLoading(`测试模型: ${modelName}`);
        
        try {
            // 模拟 API 调用
            await new Promise(resolve => setTimeout(resolve, 1500));
            
            // 模拟测试结果（80%成功率）
            const success = Math.random() > 0.2;
            
            if (success) {
                this.showToast(`✅ ${modelName} 测试通过`, 'success');
            } else {
                this.showToast(`❌ ${modelName} 测试失败`, 'error');
            }
            
            // 重新加载数据以更新统计
            await this.loadData();
            
        } catch (error) {
            console.error('测试失败:', error);
            this.showToast(`测试失败: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    async switchModel(modelName) {
        if (!modelName) {
            this.showToast('请指定要切换的模型', 'warning');
            return;
        }
        
        if (modelName === this.currentData?.current_model) {
            this.showToast('已经是当前模型', 'info');
            return;
        }
        
        if (!confirm(`确定要切换到 ${modelName} 吗？`)) {
            return;
        }
        
        this.showLoading(`切换到 ${modelName}...`);
        
        try {
            // 模拟 API 调用
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // 模拟切换结果（90%成功率）
            const success = Math.random() > 0.1;
            
            if (success) {
                this.showToast(`✅ 已切换到 ${modelName}`, 'success');
                
                // 更新当前模型
                if (this.currentData) {
                    this.currentData.current_model = modelName;
                    this.currentData.current_model_info = this.currentData.models.find(m => m.name === modelName);
                    
                    // 添加切换日志
                    this.currentData.switch_log.push({
                        timestamp: new Date().toLocaleString('zh-CN'),
                        from: this.currentData.current_model,
                        to: modelName,
                        reason: '手动切换',
                        success: true,
                        notified: true
                    });
                }
                
                // 更新 UI
                this.updateDashboard();
                this.updateModelsTable();
                this.updateLogs();
                
            } else {
                this.showToast(`❌ 切换到 ${modelName} 失败`, 'error');
            }
            
        } catch (error) {
            console.error('切换失败:', error);
            this.showToast(`切换失败: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    async toggleModelStatus(modelId, newStatus) {
        const action = newStatus === 'active' ? '启用' : '禁用';
        const model = this.currentData?.models?.find(m => m.id === modelId);
        
        if (!model) {
            this.showToast('未找到指定模型', 'error');
            return;
        }
        
        if (!confirm(`确定要${action}模型 ${model.name} 吗？`)) {
            return;
        }
        
        this.showLoading(`${action}模型...`);
        
        try {
            // 模拟 API 调用
            await new Promise(resolve => setTimeout(resolve, 800));
            
            // 更新模型状态
            model.status = newStatus;
            
            this.showToast(`✅ 模型已${action}`, 'success');
            
            // 更新 UI
            this.updateDashboard();
            this.updateModelsTable();
            
        } catch (error) {
            console.error('操作失败:', error);
            this.showToast(`操作失败: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    async runAutoSwitch() {
        this.showLoading('运行自动检测...');
        
        try {
            // 模拟 API 调用
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // 模拟检测结果（30%概率切换）
            const switched = Math.random() > 0.7;
            
            if (switched) {
                this.showToast('检测到模型不可用，已自动切换', 'success');
            } else {
                this.showToast('当前模型正常，无需切换', 'info');
            }
            
            // 重新加载数据
            await this.loadData();
            
        } catch (error) {
            console.error('自动检测失败:', error);
            this.showToast(`自动检测失败: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    toggleAutoSwitch() {
        const toggle = document.getElementById('autoSwitchToggle');
        const text = document.getElementById('autoSwitchText');
        
        if (toggle && text) {
            const enabled = toggle.checked;
            text.textContent = enabled ? '启用' : '禁用';
            
            if (this.currentData) {
                this.currentData.auto_switch_enabled = enabled;
            }
            
            this.showToast(`自动切换已${enabled ? '启用' : '禁用'}`, 'info');
        }
    }
    
    toggleNotify() {
        const toggle = document.getElementById('notifyToggle');
        const text = document.getElementById('notifyText');
        
        if (toggle && text) {
            const enabled = toggle.checked;
            text.textContent = enabled ? '启用' : '禁用';
            
            if (this.currentData) {
                this.currentData.notify_on_switch = enabled;
            }
            
            this.showToast(`切换通知已${enabled ? '启用' : '禁用'}`, 'info');
        }
    }
    
    async saveSettings() {
        this.showLoading('保存设置...');
        
        try {
            // 模拟 API 调用
            await new Promise(resolve => setTimeout(resolve, 800));
            
            // 获取设置值
            const autoSwitchEnabled = document.getElementById('autoSwitchToggle').checked;
            const checkInterval = document.getElementById('checkInterval').value;
            const notifyEnabled = document.getElementById('notifyToggle').checked;
            
            // 更新数据
            if (this.currentData) {
                this.currentData.auto_switch_enabled = autoSwitchEnabled;
                this.currentData.check_interval = parseInt(checkInterval);
                this.currentData.notify_on_switch = notifyEnabled;
                
                if (this.currentData.settings) {
                    this.currentData.settings.auto_switch_enabled = autoSwitchEnabled;
                    this.currentData.settings.check_interval_minutes = parseInt(checkInterval);
                    this.currentData.settings.notify_on_switch = notifyEnabled;
                }
            }
            
            this.showToast('✅ 设置已保存', 'success');
            
        } catch (error) {
            console.error('保存设置失败:', error);
            this.showToast(`保存失败: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    exportModels() {
        if (!this.currentData) return;
        
        const models = this.currentData.models || [];
        
        // 创建 CSV 内容
        const headers = ['ID', '模型名称', 'Provider', '状态', '优先级', '最后使用', '添加时间', '备注'];
        const rows = models.map(model => [
            model.id,
            model.name,
            model.provider,
            model.status,
            model.priority,
            model.last_used ? model.last_used.substring(0, 10) : '',
            model.added_at,
            model.notes || ''
        ]);
        
        const csvContent = [
            headers.join(','),
            ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
        ].join('\n');
        
        // 创建下载链接
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const timestamp = new Date().toISOString().slice(0, 10);
        
        link.href = URL.createObjectURL(blob);
        link.download = `openclaw_models_${timestamp}.csv`;
        link.click();
        
        this.showToast('模型列表已导出为 CSV', 'success');
    }
    
    refreshData() {
        this.loadData();
    }
    
    refreshModels() {
        this.updateModelsTable();
        this.showToast('模型列表已刷新', 'success');
    }
    
    showAllModels() {
        this.switchTab('models');
    }
    
    async backupRegistry() {
        this.showLoading('备份数据...');
        
        try {
            // 模拟 API 调用
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            this.showToast('✅ 数据备份完成', 'success');
            
        } catch (error) {
            console.error('备份失败:', error);
            this.showToast(`备份失败: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    async clearOldLogs() {
        if (!confirm('确定要清理7天前的旧日志吗？')) {
            return;
        }
        
        this.showLoading('清理旧日志...');
        
        try {
            // 模拟 API 调用
            await new Promise(resolve => setTimeout(resolve, 800));
            
            this.showToast('✅ 旧日志已清理', 'success');
            
        } catch (error) {
            console.error('清理失败:', error);
            this.showToast(`清理失败: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    async resetPerformanceStats() {
        if (!confirm('确定要重置所有性能统计吗？此操作不可撤销。')) {
            return;
        }
        
        this.showLoading('重置性能统计...');
        
        try {
            // 模拟 API 调用
            await new Promise(resolve => setTimeout(resolve, 800));
            
            this.showToast('✅ 性能统计已重置', 'success');
            
        } catch (error) {
            console.error('重置失败:', error);
            this.showToast(`重置失败: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    toggleView() {
        this.currentView = this.currentView === 'table' ? 'card' : 'table';
        this.showToast(`已切换到${this.currentView === 'table' ? '表格' : '卡片'}视图`, 'info');
        // 这里可以添加切换视图的逻辑
    }
    
    // UI 工具方法
    showLoading(text = '加载中...') {
        const loading = document.getElementById('loading');
        const loadingText = document.getElementById('loadingText');
        
        if (loading && loadingText) {
            loadingText.textContent = text;
            loading.classList.add('show');
        }
    }
    
    hideLoading() {
        const loading = document.getElementById('loading');
        if (loading) {
            loading.classList.remove('show');
        }
    }
    
    showToast(message, type = 'info') {
        const toast = document.getElementById('toast');
        if (!toast) return;
        
        // 设置内容和类型
        toast.textContent = message;
        toast.className = 'toast';
        
        // 添加类型类
        if (type === 'success') {
            toast.classList.add('show');
            toast.innerHTML = `<i class="fas fa-check-circle toast-icon"></i> ${message}`;
        } else if (type === 'error') {
            toast.classList.add('show', 'error');
            toast.innerHTML = `<i class="fas fa-exclamation-circle toast-icon"></i> ${message}`;
        } else if (type === 'warning') {
            toast.classList.add('show', 'warning');
            toast.innerHTML = `<i class="fas fa-exclamation-triangle toast-icon"></i> ${message}`;
        } else {
            toast.classList.add('show', 'info');
            toast.innerHTML = `<i class="fas fa-info-circle toast-icon"></i> ${message}`;
        }
        
        // 3秒后自动隐藏
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
}

// 全局 dashboard 实例
let dashboard;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new ModelManagerDashboard();
    
    // 全局函数供 HTML 调用
    window.switchTab = (tabId) => dashboard.switchTab(tabId);
    window.testCurrentModel = () => dashboard.testCurrentModel();
    window.testModel = (modelName) => dashboard.testModel(modelName);
    window.switchModel = (modelName) => dashboard.switchModel(modelName);
    window.toggleModelStatus = (modelId, status) => dashboard.toggleModelStatus(modelId, status);
    window.runAutoSwitch = () => dashboard.runAutoSwitch();
    window.toggleAutoSwitch = () => dashboard.toggleAutoSwitch();
    window.toggleNotify = () => dashboard.toggleNotify();
    window.saveSettings = () => dashboard.saveSettings();
    window.exportModels = () => dashboard.exportModels();
    window.refreshData = () => dashboard.refreshData();
    window.refreshModels = () => dashboard.refreshModels();
    window.showAllModels = () => dashboard.showAllModels();
    window.backupRegistry = () => dashboard.backupRegistry();
    window.clearOldLogs = () => dashboard.clearOldLogs();
    window.resetPerformanceStats = () => dashboard.resetPerformanceStats();
    window.toggleView = () => dashboard.toggleView();
    
    // 添加键盘快捷键提示
    console.log('🎮 键盘快捷键:');
    console.log('  • Ctrl+R / F5 - 刷新数据');
    console.log('  • 点击模型名称可快速测试');
    console.log('  • 点击切换按钮可快速切换模型');
});

// 全局工具函数
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function formatTimeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return '刚刚';
    if (diffMins < 60) return `${diffMins}分钟前`;
    if (diffHours < 24) return `${diffHours}小时前`;
    if (diffDays < 7) return `${diffDays}天前`;
    
    return date.toLocaleDateString('zh-CN');
}

function getScoreColor(score) {
    if (score >= 0.8) return '#10b981';
    if (score >= 0.6) return '#f59e0b';
    return '#ef4444';
}

function getResponseTimeColor(responseTime) {
    if (responseTime < 1000) return '#10b981';
    if (responseTime < 3000) return '#f59e0b';
    return '#ef4444';
}

function getSuccessRateColor(rate) {
    if (rate >= 0.9) return '#10b981';
    if (rate >= 0.7) return '#f59e0b';
    return '#ef4444';
}