#!/usr/bin/env python3
"""
修复的 WebSocket 测试脚本
"""

import asyncio
import websockets
import json
import sys

async def test_websocket_connection():
    """测试 WebSocket 连接"""
    print("🔌 测试 WebSocket 连接...")
    
    try:
        # 连接到 WebSocket 服务器
        async with websockets.connect('ws://localhost:8191') as websocket:
            print("✅ WebSocket 连接成功")
            
            # 发送测试消息
            test_message = json.dumps({
                "type": "ping",
                "timestamp": "2026-03-29T15:00:00Z"
            })
            
            await websocket.send(test_message)
            print(f"📤 发送消息: {test_message}")
            
            # 等待响应
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                print(f"📥 收到响应: {response[:100]}...")
                
                # 尝试解析 JSON
                try:
                    data = json.loads(response)
                    print(f"✅ 响应解析成功，类型: {data.get('type', '未知')}")
                except json.JSONDecodeError:
                    print("⚠️  响应不是有效的 JSON")
                    
            except asyncio.TimeoutError:
                print("⚠️  等待响应超时")
            
            # 测试订阅系统状态
            print("\n📡 测试订阅系统状态...")
            subscribe_msg = json.dumps({
                "type": "subscribe",
                "channel": "system-status"
            })
            
            await websocket.send(subscribe_msg)
            print(f"📤 订阅消息: {subscribe_msg}")
            
            # 等待系统状态更新
            try:
                for i in range(3):  # 最多接收3条消息
                    update = await asyncio.wait_for(websocket.recv(), timeout=3)
                    print(f"📥 系统更新 {i+1}: {update[:100]}...")
            except asyncio.TimeoutError:
                print("⚠️  等待系统更新超时")
            
            return True
            
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"❌ WebSocket 连接关闭: {e}")
        return False
    except websockets.exceptions.InvalidURI as e:
        print(f"❌ 无效的 URI: {e}")
        return False
    except ConnectionRefusedError as e:
        print(f"❌ 连接被拒绝: {e}")
        return False
    except Exception as e:
        print(f"❌ WebSocket 连接异常: {type(e).__name__}: {e}")
        return False

async def test_websocket_events():
    """测试 WebSocket 事件"""
    print("\n🎯 测试 WebSocket 事件...")
    
    try:
        async with websockets.connect('ws://localhost:8191') as websocket:
            print("✅ 连接成功，等待事件...")
            
            # 发送请求获取系统状态
            request_msg = json.dumps({
                "type": "request-system-status"
            })
            
            await websocket.send(request_msg)
            print(f"📤 请求系统状态: {request_msg}")
            
            # 监听事件
            events_received = 0
            max_events = 5
            timeout = 10
            
            try:
                start_time = asyncio.get_event_loop().time()
                
                while events_received < max_events:
                    time_remaining = timeout - (asyncio.get_event_loop().time() - start_time)
                    if time_remaining <= 0:
                        break
                    
                    try:
                        event = await asyncio.wait_for(websocket.recv(), time_remaining)
                        events_received += 1
                        
                        # 尝试解析事件
                        try:
                            event_data = json.loads(event)
                            event_type = event_data.get('type', 'unknown')
                            print(f"📥 事件 {events_received}: {event_type}")
                            
                            # 显示特定事件的内容
                            if event_type in ['system-status', 'models-data']:
                                print(f"   数据: {str(event_data)[:80]}...")
                                
                        except json.JSONDecodeError:
                            print(f"📥 事件 {events_received}: 原始数据: {event[:80]}...")
                            
                    except asyncio.TimeoutError:
                        print(f"⚠️  等待事件超时 (已接收 {events_received} 个事件)")
                        break
                        
                print(f"✅ 总共接收 {events_received} 个事件")
                
            except Exception as e:
                print(f"❌ 事件监听异常: {type(e).__name__}: {e}")
            
            return events_received > 0
            
    except Exception as e:
        print(f"❌ 事件测试异常: {type(e).__name__}: {e}")
        return False

async def test_websocket_reconnection():
    """测试 WebSocket 重连"""
    print("\n🔄 测试 WebSocket 重连...")
    
    reconnect_attempts = 3
    successful_reconnects = 0
    
    for attempt in range(reconnect_attempts):
        print(f"尝试 {attempt + 1}/{reconnect_attempts}...")
        
        try:
            async with websockets.connect('ws://localhost:8191') as websocket:
                # 快速测试连接
                await websocket.send(json.dumps({"type": "ping"}))
                response = await asyncio.wait_for(websocket.recv(), timeout=2)
                
                successful_reconnects += 1
                print(f"✅ 重连 {attempt + 1} 成功")
                
                # 短暂断开
                await websocket.close()
                await asyncio.sleep(0.5)
                
        except Exception as e:
            print(f"❌ 重连 {attempt + 1} 失败: {type(e).__name__}")
            await asyncio.sleep(1)  # 等待后重试
    
    success_rate = successful_reconnects / reconnect_attempts
    print(f"📊 重连成功率: {success_rate:.0%} ({successful_reconnects}/{reconnect_attempts})")
    
    return success_rate >= 0.5

async def main():
    """主测试函数"""
    print("🚀 WebSocket 连接测试")
    print("=" * 50)
    
    # 运行测试
    tests = [
        ("基本连接测试", test_websocket_connection),
        ("事件监听测试", test_websocket_events),
        ("重连能力测试", test_websocket_reconnection),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}")
        print("-" * 30)
        
        try:
            success = await test_func()
            results.append((test_name, success))
            
            if success:
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败")
                
        except Exception as e:
            print(f"❌ {test_name} 异常: {type(e).__name__}: {e}")
            results.append((test_name, False))
    
    # 显示结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} - {test_name}")
    
    print("\n" + "=" * 50)
    print(f"📈 总体结果: {passed_tests}/{total_tests} 个测试通过")
    
    if passed_tests == total_tests:
        print("🎉 所有 WebSocket 测试通过！")
        return True
    else:
        print(f"⚠️  有 {total_tests - passed_tests} 个测试失败")
        return False

if __name__ == "__main__":
    try:
        # 检查 websockets 库
        try:
            import websockets
        except ImportError:
            print("❌ 未安装 websockets 库")
            print("安装命令: pip install websockets")
            sys.exit(1)
        
        # 运行测试
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试过程中发生异常: {e}")
        sys.exit(1)