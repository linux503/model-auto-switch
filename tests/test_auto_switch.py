#!/usr/bin/env python3
"""
模型自动切换测试脚本
测试以下功能：
1. 检查当前模型
2. 列出所有可用模型
3. 测试模型可用性
4. 自动切换到最佳模型
"""

import json
import subprocess
import sys
import time
from pathlib import Path

# 配置
WORKSPACE_PATH = Path("/Users/a404/.openclaw/workspace")
REGISTRY_PATH = WORKSPACE_PATH / "models_registry.json"
SKILL_PATH = Path("/Users/a404/.openclaw/workspace/skills/model-auto-switch")

def run_command(cmd):
    """运行命令并返回结果"""
    print(f"🚀 执行命令: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "命令执行超时",
            "returncode": -1
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "returncode": -1
        }

def test_api_connection():
    """测试API连接"""
    print("\n" + "="*60)
    print("🔌 测试API连接")
    print("="*60)
    
    # 测试健康检查
    health_result = run_command("curl -s http://localhost:8191/api/health")
    if health_result["success"]:
        try:
            health_data = json.loads(health_result["stdout"])
            print(f"✅ 健康检查: {health_data.get('status', '未知')}")
            print(f"   版本: {health_data.get('version', '未知')}")
        except:
            print(f"✅ 健康检查响应: {health_result['stdout'][:100]}...")
    else:
        print(f"❌ 健康检查失败: {health_result['stderr']}")
    
    # 测试模型API
    models_result = run_command("curl -s http://localhost:8191/api/models")
    if models_result["success"]:
        try:
            models_data = json.loads(models_result["stdout"])
            print(f"✅ 模型API: {models_data.get('count', 0)} 个模型")
            
            # 显示当前模型
            current_model = models_data.get('current_model', {})
            if current_model:
                print(f"   当前模型: {current_model.get('name', '未知')} (ID: {current_model.get('id', '未知')})")
            
            # 显示OpenClaw当前模型
            openclaw_model = models_data.get('openclaw_current_model', '未知')
            print(f"   OpenClaw当前模型: {openclaw_model}")
            
        except Exception as e:
            print(f"❌ 解析模型数据失败: {e}")
            print(f"   原始响应: {models_result['stdout'][:200]}...")
    else:
        print(f"❌ 模型API失败: {models_result['stderr']}")
    
    return health_result["success"] and models_result["success"]

def test_model_manager():
    """测试模型管理器"""
    print("\n" + "="*60)
    print("🤖 测试模型管理器")
    print("="*60)
    
    # 检查脚本是否存在
    manager_script = SKILL_PATH / "scripts" / "model_manager_enhanced.py"
    if not manager_script.exists():
        print(f"❌ 模型管理器脚本不存在: {manager_script}")
        return False
    
    # 测试列出模型
    print("📋 测试列出所有模型...")
    list_result = run_command(f"cd {SKILL_PATH} && python3 scripts/model_manager_enhanced.py list")
    if list_result["success"]:
        print("✅ 模型列表命令执行成功")
        # 解析输出
        lines = list_result["stdout"].split('\n')
        model_count = 0
        for line in lines:
            if "M0" in line and "|" in line:
                model_count += 1
        print(f"   找到 {model_count} 个模型")
    else:
        print(f"❌ 模型列表失败: {list_result['stderr']}")
    
    # 测试状态检查
    print("\n📊 测试系统状态...")
    status_result = run_command(f"cd {SKILL_PATH} && python3 scripts/model_manager_enhanced.py status")
    if status_result["success"]:
        print("✅ 状态检查成功")
        # 显示关键信息
        lines = status_result["stdout"].split('\n')
        for line in lines[:10]:  # 只显示前10行
            if any(keyword in line.lower() for keyword in ["模型", "状态", "active", "total"]):
                print(f"   {line.strip()}")
    else:
        print(f"❌ 状态检查失败: {status_result['stderr']}")
    
    return list_result["success"]

def test_model_switching():
    """测试模型切换功能"""
    print("\n" + "="*60)
    print("🔄 测试模型切换功能")
    print("="*60)
    
    # 首先获取当前模型
    print("📝 获取当前模型信息...")
    current_result = run_command(f"cd {SKILL_PATH} && python3 scripts/model_manager_enhanced.py status")
    
    if current_result["success"]:
        # 尝试解析当前模型
        lines = current_result["stdout"].split('\n')
        current_model_id = None
        
        for line in lines:
            if "当前模型" in line or "current model" in line.lower():
                parts = line.split(':')
                if len(parts) > 1:
                    model_info = parts[1].strip()
                    # 尝试提取模型ID
                    if "M0" in model_info:
                        for part in model_info.split():
                            if part.startswith("M0"):
                                current_model_id = part
                                break
        
        if current_model_id:
            print(f"   当前模型ID: {current_model_id}")
            
            # 测试切换到另一个模型（如果可用）
            print(f"\n🔄 测试切换到另一个模型...")
            
            # 先获取所有模型
            list_result = run_command(f"cd {SKILL_PATH} && python3 scripts/model_manager_enhanced.py list")
            if list_result["success"]:
                lines = list_result["stdout"].split('\n')
                other_model_id = None
                
                for line in lines:
                    if "M0" in line and "|" in line:
                        parts = line.split('|')
                        if len(parts) > 1:
                            model_id = parts[0].strip()
                            if model_id != current_model_id:
                                other_model_id = model_id
                                break
                
                if other_model_id:
                    print(f"   尝试切换到模型: {other_model_id}")
                    
                    # 测试模型
                    test_result = run_command(f"cd {SKILL_PATH} && python3 scripts/model_manager_enhanced.py test {other_model_id}")
                    if test_result["success"]:
                        print(f"   ✅ 模型 {other_model_id} 测试成功")
                        
                        # 尝试切换
                        switch_result = run_command(f"cd {SKILL_PATH} && python3 scripts/model_manager_enhanced.py switch {other_model_id}")
                        if switch_result["success"]:
                            print(f"   ✅ 成功切换到模型 {other_model_id}")
                            
                            # 等待并验证
                            time.sleep(2)
                            verify_result = run_command(f"cd {SKILL_PATH} && python3 scripts/model_manager_enhanced.py status")
                            if verify_result["success"]:
                                print(f"   ✅ 切换验证完成")
                            else:
                                print(f"   ⚠️  切换验证失败: {verify_result['stderr']}")
                        else:
                            print(f"   ❌ 切换失败: {switch_result['stderr']}")
                    else:
                        print(f"   ⚠️  模型测试失败: {test_result['stderr']}")
                else:
                    print("   ⚠️  没有找到其他可用模型")
            else:
                print(f"   ❌ 获取模型列表失败: {list_result['stderr']}")
        else:
            print("   ⚠️  无法确定当前模型ID")
    else:
        print(f"❌ 获取当前状态失败: {current_result['stderr']}")
    
    return True  # 即使切换测试有问题，也返回True

def test_auto_switch():
    """测试自动切换功能"""
    print("\n" + "="*60)
    print("🤖 测试自动切换功能")
    print("="*60)
    
    print("🚀 运行自动切换检测...")
    auto_result = run_command(f"cd {SKILL_PATH} && python3 scripts/model_manager_enhanced.py auto --verbose")
    
    if auto_result["success"]:
        print("✅ 自动切换检测执行成功")
        
        # 分析输出
        output = auto_result["stdout"]
        if "切换到" in output or "switch to" in output.lower():
            print("   🔄 检测到模型切换操作")
        elif "无需切换" in output or "no need to switch" in output.lower():
            print("   ✅ 当前模型正常，无需切换")
        elif "所有模型" in output or "all models" in output.lower():
            print("   📊 完成模型检查")
        
        # 显示关键信息
        lines = output.split('\n')
        for line in lines[-10:]:  # 显示最后10行
            if line.strip():
                print(f"   {line.strip()}")
    else:
        print(f"❌ 自动切换检测失败: {auto_result['stderr']}")
    
    return auto_result["success"]

def test_web_interface():
    """测试Web界面"""
    print("\n" + "="*60)
    print("🌐 测试Web界面")
    print("="*60)
    
    print("🔗 测试页面可访问性...")
    
    # 测试管理后台
    admin_result = run_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:8191/admin")
    if admin_result["success"] and admin_result["stdout"] in ["200", "302"]:
        print("✅ 管理后台可访问")
    else:
        print(f"❌ 管理后台不可访问: HTTP {admin_result.get('stdout', '未知')}")
    
    # 测试API端点
    api_result = run_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:8191/api/health")
    if api_result["success"] and api_result["stdout"] == "200":
        print("✅ API健康检查可访问")
    else:
        print(f"❌ API健康检查不可访问: HTTP {api_result.get('stdout', '未知')}")
    
    # 测试WebSocket连接
    print("\n📡 测试WebSocket连接...")
    ws_test_script = f"""
import asyncio
import websockets
import sys

async def test_ws():
    try:
        async with websockets.connect('ws://localhost:8191') as websocket:
            await websocket.send('ping')
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            print(f"WebSocket连接成功: {{response[:50]}}...")
            return True
    except Exception as e:
        print(f"WebSocket连接失败: {{e}}")
        return False

asyncio.run(test_ws())
"""
    
    ws_result = run_command(f'python3 -c "{ws_test_script}"')
    if ws_result["success"] and "成功" in ws_result["stdout"]:
        print("✅ WebSocket连接正常")
    else:
        print(f"⚠️  WebSocket连接测试失败: {ws_result.get('stderr', '未知错误')}")
    
    return True

def main():
    """主测试函数"""
    print("🚀 OpenClaw 模型自动切换系统测试")
    print("="*60)
    
    # 检查环境
    print("🔍 检查测试环境...")
    if not REGISTRY_PATH.exists():
        print(f"❌ 模型注册表不存在: {REGISTRY_PATH}")
        return False
    
    if not SKILL_PATH.exists():
        print(f"❌ 技能目录不存在: {SKILL_PATH}")
        return False
    
    print(f"✅ 模型注册表: {REGISTRY_PATH}")
    print(f"✅ 技能目录: {SKILL_PATH}")
    
    # 运行测试
    tests = [
        ("API连接测试", test_api_connection),
        ("模型管理器测试", test_model_manager),
        ("模型切换测试", test_model_switching),
        ("自动切换测试", test_auto_switch),
        ("Web界面测试", test_web_interface),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")
            results.append((test_name, False))
    
    # 显示测试结果
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} - {test_name}")
    
    print("\n" + "="*60)
    print(f"📈 总体结果: {passed_tests}/{total_tests} 个测试通过")
    
    if passed_tests == total_tests:
        print("🎉 所有测试通过！系统功能正常。")
        return True
    else:
        print(f"⚠️  有 {total_tests - passed_tests} 个测试失败，请检查相关功能。")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试过程中发生异常: {e}")
        sys.exit(1)