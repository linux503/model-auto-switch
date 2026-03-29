// 简单的 WebSocket 测试脚本
console.log('🔌 测试 WebSocket 连接...');

// 创建 WebSocket 连接
const socket = new WebSocket('ws://localhost:8191');

// 连接成功
socket.onopen = function(event) {
    console.log('✅ WebSocket 连接成功');
    
    // 发送测试消息
    const testMessage = JSON.stringify({
        type: 'ping',
        timestamp: new Date().toISOString()
    });
    
    socket.send(testMessage);
    console.log('📤 发送消息:', testMessage);
};

// 接收消息
socket.onmessage = function(event) {
    console.log('📥 收到消息:', event.data);
    
    try {
        const data = JSON.parse(event.data);
        console.log('✅ 消息解析成功，类型:', data.type || '未知');
        
        // 根据消息类型处理
        switch(data.type) {
            case 'welcome':
                console.log('👋 欢迎消息:', data.message);
                break;
            case 'system-status':
                console.log('📊 系统状态更新');
                break;
            case 'models-data':
                console.log('🤖 模型数据更新');
                break;
            default:
                console.log('📨 其他消息类型:', data.type);
        }
    } catch (error) {
        console.log('⚠️  消息不是有效的 JSON:', event.data.substring(0, 100));
    }
};

// 连接错误
socket.onerror = function(error) {
    console.error('❌ WebSocket 错误:', error);
};

// 连接关闭
socket.onclose = function(event) {
    console.log('🔌 WebSocket 连接关闭，代码:', event.code, '原因:', event.reason);
};

// 测试函数：请求系统状态
function requestSystemStatus() {
    if (socket.readyState === WebSocket.OPEN) {
        const request = JSON.stringify({
            type: 'request-system-status'
        });
        socket.send(request);
        console.log('📤 请求系统状态:', request);
    } else {
        console.log('⚠️  WebSocket 未连接，无法发送请求');
    }
}

// 测试函数：请求模型数据
function requestModelsData() {
    if (socket.readyState === WebSocket.OPEN) {
        const request = JSON.stringify({
            type: 'request-models'
        });
        socket.send(request);
        console.log('📤 请求模型数据:', request);
    } else {
        console.log('⚠️  WebSocket 未连接，无法发送请求');
    }
}

// 自动测试流程
setTimeout(() => {
    console.log('\n🎯 开始自动测试...');
    
    // 请求系统状态
    requestSystemStatus();
    
    // 稍后请求模型数据
    setTimeout(() => {
        requestModelsData();
        
        // 测试完成，关闭连接
        setTimeout(() => {
            console.log('\n✅ 测试完成，关闭连接');
            socket.close();
        }, 2000);
    }, 1000);
}, 1000);

console.log('🚀 WebSocket 测试脚本已启动');