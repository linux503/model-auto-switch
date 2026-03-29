#!/usr/bin/env python3
"""
OpenClaw 模型管理 API 客户端示例
展示如何通过 API 集成模型管理功能
"""

import requests
import json
import time
from typing import Dict, List, Optional
import sys

class ModelAPIClient:
    """模型管理 API 客户端"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8190"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'OpenClaw-Model-API-Client/2.0'
        })
    
    def _request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """发送 HTTP 请求"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=data)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.ConnectionError:
            print(f"❌ 无法连接到 API 服务器: {url}")
            print("   请确保 API 服务器正在运行:")
            print(f"   python3 scripts/model_api_server.py")
            return {"error": "Connection failed"}
        
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP 错误: {e}")
            try:
                error_data = response.json()
                return error_data
            except:
                return {"error": str(e)}
        
        except Exception as e:
            print(f"❌ 请求错误: {e}")
            return {"error": str(e)}
    
    def health_check(self) -> bool:
        """健康检查"""
        print("🔍 检查 API 健康状态...")
        result = self._request('GET', '/api/health')
        
        if 'status' in result and result['status'] == 'healthy':
            print("✅ API 服务器运行正常")
            return True
        else:
            print("❌ API 服务器异常")
            return False
    
    def get_status(self) -> Optional[Dict]:
        """获取系统状态"""
        print("📊 获取系统状态...")
        return self._request('GET', '/api/status')
    
    def list_models(self, status: str = None) -> List[Dict]:
        """列出所有模型"""
        print("📋 获取模型列表...")
        params = {}
        if status:
            params['status'] = status
        
        result = self._request('GET', '/api/models', params)
        return result.get('models', []) if 'models' in result else []
    
    def get_current_model(self) -> Optional[Dict]:
        """获取当前模型"""
        print("🎯 获取当前模型...")
        result = self._request('GET', '/api/models/current')
        return result if 'error' not in result else None
    
    def switch_model(self, model_name: str, reason: str = "api_request") -> bool:
        """切换模型"""
        print(f"🔄 切换到模型: {model_name}...")
        data = {
            "model": model_name,
            "reason": reason
        }
        
        result = self._request('POST', '/api/models/switch', data)
        
        if result.get('success'):
            print(f"✅ 成功切换到 {model_name}")
            return True
        else:
            print(f"❌ 切换失败: {result.get('message', 'Unknown error')}")
            return False
    
    def test_model(self, model_name: str) -> Dict:
        """测试模型"""
        print(f"🧪 测试模型: {model_name}...")
        data = {"model": model_name}
        
        result = self._request('POST', '/api/models/test', data)
        
        if 'success' in result:
            status = "通过" if result['success'] else "失败"
            print(f"✅ 测试{status} - 响应时间: {result.get('response_time_ms', 0)}ms")
        
        return result
    
    def get_performance_report(self) -> Dict:
        """获取性能报告"""
        print("📈 获取性能报告...")
        return self._request('GET', '/api/performance')
    
    def run_auto_switch(self) -> Dict:
        """运行自动切换"""
        print("⚡ 运行自动切换...")
        return self._request('POST', '/api/auto-switch/run')
    
    def get_cost_analysis(self) -> List[Dict]:
        """获取成本分析"""
        print("💰 获取成本分析...")
        result = self._request('GET', '/api/predictive/cost')
        return result.get('results', []) if 'results' in result else []
    
    def get_time_analysis(self) -> Dict:
        """获取时间敏感分析"""
        print("⏰ 获取时间敏感分析...")
        return self._request('GET', '/api/predictive/time')
    
    def send_notification(self, message: str, level: str = "info") -> bool:
        """发送通知"""
        print(f"📨 发送通知: {message}...")
        data = {
            "message": message,
            "level": level
        }
        
        result = self._request('POST', '/api/notify', data)
        return result.get('success', False)
    
    def create_backup(self) -> bool:
        """创建备份"""
        print("💾 创建备份...")
        result = self._request('POST', '/api/backup')
        return result.get('success', False)

def demo_all_features():
    """演示所有 API 功能"""
    print("=" * 60)
    print("OpenClaw 模型管理 API 客户端演示")
    print("=" * 60)
    
    client = ModelAPIClient()
    
    # 1. 健康检查
    if not client.health_check():
        print("\n⚠️  API 服务器未运行，无法继续演示")
        print("   请先启动 API 服务器:")
        print("   cd /Users/a404/.openclaw/workspace/skills/model-auto-switch")
        print("   python3 scripts/model_api_server.py")
        return
    
    print()
    
    # 2. 系统状态
    status = client.get_status()
    if status and 'error' not in status:
        print("📊 系统状态:")
        print(f"   服务: {status.get('service', 'N/A')}")
        print(f"   版本: {status.get('api_version', 'N/A')}")
        print(f"   状态: {status.get('status', 'N/A')}")
    
    print()
    
    # 3. 当前模型
    current_model = client.get_current_model()
    if current_model:
        print("🎯 当前模型:")
        print(f"   名称: {current_model.get('name', 'N/A')}")
        print(f"   Provider: {current_model.get('provider', 'N/A')}")
        print(f"   优先级: {current_model.get('priority', 'N/A')}")
        
        perf = current_model.get('performance', {})
        if perf:
            print(f"   成功率: {perf.get('success_rate', 0):.1%}")
            print(f"   响应时间: {perf.get('avg_response_time', 0)}ms")
    
    print()
    
    # 4. 模型列表
    models = client.list_models(status='active')
    if models:
        print(f"📋 活跃模型 ({len(models)} 个):")
        for model in models[:3]:  # 只显示前3个
            print(f"   • {model.get('name', 'N/A')} (优先级: {model.get('priority', 'N/A')})")
        
        if len(models) > 3:
            print(f"   ... 还有 {len(models) - 3} 个模型")
    
    print()
    
    # 5. 性能报告
    print("📈 获取性能报告...")
    report = client.get_performance_report()
    if report and 'error' not in report:
        summary = report.get('summary', {})
        if summary:
            print(f"   总测试: {summary.get('total_tests', 0)}")
            print(f"   整体成功率: {summary.get('overall_success_rate', 0):.1%}")
        
        top_performers = report.get('top_performers', [])
        if top_performers:
            print(f"   最佳模型: {top_performers[0].get('model', 'N/A')}")
    
    print()
    
    # 6. 成本分析
    print("💰 成本分析...")
    cost_results = client.get_cost_analysis()
    if cost_results:
        best_value = cost_results[0] if cost_results else {}
        print(f"   最具性价比: {best_value.get('model', 'N/A')}")
        print(f"   性价比评分: {best_value.get('value_score', 0):.3f}")
    
    print()
    
    # 7. 时间敏感分析
    print("⏰ 时间敏感分析...")
    time_analysis = client.get_time_analysis()
    if time_analysis and 'error' not in time_analysis:
        print(f"   当前时间: {time_analysis.get('current_time', 'N/A')}")
        print(f"   推荐模型: {', '.join(time_analysis.get('recommended_models', []))}")
        print(f"   理由: {time_analysis.get('reason', 'N/A')}")
    
    print()
    
    # 8. 测试模型（示例）
    if models:
        sample_model = models[0].get('name')
        print(f"🧪 测试示例模型: {sample_model}")
        test_result = client.test_model(sample_model)
        if 'success' in test_result:
            status = "通过" if test_result['success'] else "失败"
            print(f"   测试{status} - 响应时间: {test_result.get('response_time_ms', 0)}ms")
    
    print()
    
    # 9. 运行自动切换
    print("⚡ 运行自动切换演示...")
    auto_result = client.run_auto_switch()
    if auto_result and 'error' not in auto_result:
        switched = auto_result.get('switched', False)
        print(f"   自动切换{'已执行' if switched else '未执行'}切换")
        print(f"   消息: {auto_result.get('message', 'N/A')}")
    
    print()
    
    # 10. 发送通知
    print("📨 发送测试通知...")
    notification_sent = client.send_notification(
        "API 客户端演示完成",
        "info"
    )
    print(f"   通知发送{'成功' if notification_sent else '失败'}")
    
    print()
    print("=" * 60)
    print("✅ API 客户端演示完成")
    print("=" * 60)

def integration_example():
    """集成示例：监控并自动优化模型"""
    print("=" * 60)
    print("集成示例：智能模型监控与优化")
    print("=" * 60)
    
    client = ModelAPIClient()
    
    if not client.health_check():
        return
    
    print("\n🔍 开始监控循环 (每30秒检查一次)...")
    print("   按 Ctrl+C 停止")
    print()
    
    try:
        check_count = 0
        while True:
            check_count += 1
            print(f"\n📊 检查 #{check_count} - {time.strftime('%H:%M:%S')}")
            
            # 1. 检查当前模型性能
            current_model = client.get_current_model()
            if current_model:
                perf = current_model.get('performance', {})
                success_rate = perf.get('success_rate', 0)
                response_time = perf.get('avg_response_time', 0)
                
                print(f"   当前模型: {current_model.get('name', 'N/A')}")
                print(f"     成功率: {success_rate:.1%}")
                print(f"     响应时间: {response_time}ms")
                
                # 如果性能不达标，考虑切换
                if success_rate < 0.7 or response_time > 3000:
                    print("   ⚠️  性能不达标，寻找替代模型...")
                    
                    # 获取所有活跃模型
                    models = client.list_models(status='active')
                    if models:
                        # 排除当前模型
                        alternatives = [m for m in models if m.get('name') != current_model.get('name')]
                        
                        if alternatives:
                            # 选择优先级最高的替代模型
                            alternatives.sort(key=lambda x: x.get('priority', 999))
                            best_alternative = alternatives[0]
                            
                            print(f"   🔄 建议切换到: {best_alternative.get('name')}")
                            
                            # 在实际应用中，这里可以添加切换逻辑
                            # client.switch_model(best_alternative.get('name'), "performance_issue")
            
            # 2. 获取时间敏感建议
            time_analysis = client.get_time_analysis()
            if time_analysis:
                print(f"   ⏰ 时间建议: {time_analysis.get('reason', 'N/A')}")
            
            # 3. 检查成本优化
            if check_count % 6 == 0:  # 每3分钟检查一次成本
                cost_results = client.get_cost_analysis()
                if cost_results:
                    best_value = cost_results[0]
                    print(f"   💰 最具性价比: {best_value.get('model')} (评分: {best_value.get('value_score', 0):.3f})")
            
            # 等待下一次检查
            time.sleep(30)
    
    except KeyboardInterrupt:
        print("\n\n👋 监控已停止")
        print("=" * 60)

def api_reference():
    """API 参考示例"""
    print("=" * 60)
    print("API 参考示例")
    print("=" * 60)
    
    client = ModelAPIClient()
    
    print("\n📚 可用 API 端点:")
    
    endpoints = [
        ("GET    /api/health", "健康检查"),
        ("GET    /api/status", "系统状态"),
        ("GET    /api/models", "获取模型列表"),
        ("GET    /api/models/current", "获取当前模型"),
        ("GET    /api/performance", "性能报告"),
        ("GET    /api/predictive/cost", "成本分析"),
        ("GET    /api/predictive/time", "时间敏感分析"),
        ("POST   /api/models/switch", "切换模型"),
        ("POST   /api/models/test", "测试模型"),
        ("POST   /api/auto-switch/run", "运行自动切换"),
        ("POST   /api/notify", "发送通知"),
        ("POST   /api/backup", "创建备份"),
    ]
    
    for endpoint, description in endpoints:
        print(f"   {endpoint:<30} {description}")
    
    print("\n💡 使用示例:")
    
    examples = [
        ("列出所有活跃模型", "client.list_models(status='active')"),
        ("切换到指定模型", "client.switch_model('aicodee/MiniMax-M2.5-highspeed', 'manual_switch')"),
        ("测试当前模型", "current = client.get_current_model(); client.test_model(current['name'])"),
        ("获取性能报告", "report = client.get_performance_report()"),
        ("发送警报通知", "client.send_notification('模型性能下降', 'warning')"),
    ]
    
    for desc, code in examples:
        print(f"   • {desc}:")
        print(f"       {code}")
    
    print("\n🔗 集成建议:")
    print("   1. 在定时任务中调用 API 进行定期检查")
    print("   2. 在 Web 应用中使用 API 获取实时状态")
    print("   3. 与其他系统集成实现自动化运维")
    print("   4. 使用通知 API 发送警报到不同平台")
    
    print("\n=" * 60)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 api_client.py <命令>")
        print("命令:")
        print("  demo        演示所有 API 功能")
        print("  monitor     运行监控示例")
        print("  reference   显示 API 参考")
        print("  health      健康检查")
        print()
        print("示例:")
        print("  python3 api_client.py demo")
        print("  python3 api_client.py monitor")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "demo":
        demo_all_features()
    elif command == "monitor":
        integration_example()
    elif command == "reference":
        api_reference()
    elif command == "health":
        client = ModelAPIClient()
        client.health_check()
    else:
        print(f"错误: 未知命令 '{command}'")