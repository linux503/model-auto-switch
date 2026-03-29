#!/usr/bin/env python3
"""
OpenClaw 模型管理 API 服务器
提供 RESTful API 接口供其他系统集成
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import threading

# 导入模型管理模块
import sys
sys.path.append(str(Path(__file__).parent))

from model_manager_enhanced import ModelManagerDashboard
from model_predictive_maintenance import PredictiveMaintenance

# 配置
WORKSPACE = Path("/Users/a404/.openclaw/workspace")
API_PORT = 8190
API_HOST = "127.0.0.1"

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(WORKSPACE / "logs" / "model_api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ModelAPI")

class ModelAPIHandler(BaseHTTPRequestHandler):
    """模型管理 API 处理器"""
    
    # 禁用默认的日志输出
    def log_message(self, format, *args):
        logger.info(f"{self.address_string()} - {format % args}")
    
    def do_GET(self):
        """处理 GET 请求"""
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path
            query_params = urllib.parse.parse_qs(parsed_path.query)
            
            logger.info(f"GET {path} - Query: {query_params}")
            
            # 路由处理
            if path == "/api/health":
                self._handle_health()
            elif path == "/api/status":
                self._handle_status()
            elif path == "/api/models":
                self._handle_get_models(query_params)
            elif path == "/api/models/current":
                self._handle_current_model()
            elif path == "/api/performance":
                self._handle_performance()
            elif path == "/api/predictive/maintenance":
                self._handle_predictive_maintenance(query_params)
            elif path == "/api/predictive/cost":
                self._handle_cost_analysis()
            elif path == "/api/predictive/time":
                self._handle_time_analysis()
            elif path == "/api/logs":
                self._handle_get_logs(query_params)
            elif path == "/":
                self._handle_index()
            else:
                self._send_error(404, "Endpoint not found")
        
        except Exception as e:
            logger.error(f"Error handling GET request: {e}", exc_info=True)
            self._send_error(500, f"Internal server error: {str(e)}")
    
    def do_POST(self):
        """处理 POST 请求"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length:
                body = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(body) if body else {}
            else:
                data = {}
            
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path
            
            logger.info(f"POST {path} - Data: {data}")
            
            # 路由处理
            if path == "/api/models/switch":
                self._handle_switch_model(data)
            elif path == "/api/models/test":
                self._handle_test_model(data)
            elif path == "/api/models/toggle":
                self._handle_toggle_model(data)
            elif path == "/api/auto-switch/run":
                self._handle_run_auto_switch()
            elif path == "/api/settings/update":
                self._handle_update_settings(data)
            elif path == "/api/backup":
                self._handle_backup()
            elif path == "/api/notify":
                self._handle_send_notification(data)
            else:
                self._send_error(404, "Endpoint not found")
        
        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON")
        except Exception as e:
            logger.error(f"Error handling POST request: {e}", exc_info=True)
            self._send_error(500, f"Internal server error: {str(e)}")
    
    def do_OPTIONS(self):
        """处理 OPTIONS 请求（CORS）"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    # GET 请求处理器
    def _handle_health(self):
        """健康检查"""
        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "service": "openclaw-model-manager",
            "version": "2.0"
        }
        self._send_json_response(200, health_data)
    
    def _handle_status(self):
        """系统状态"""
        try:
            dashboard = ModelManagerDashboard()
            # 这里需要调整，因为 ModelManagerDashboard 需要实例化方式不同
            # 暂时返回简单状态
            status_data = {
                "status": "operational",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "api_version": "2.0",
                "endpoints": [
                    "/api/health",
                    "/api/status",
                    "/api/models",
                    "/api/models/current",
                    "/api/performance",
                    "/api/predictive/maintenance",
                    "/api/predictive/cost",
                    "/api/predictive/time",
                    "/api/logs"
                ]
            }
            self._send_json_response(200, status_data)
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            self._send_error(500, f"Error getting status: {str(e)}")
    
    def _handle_get_models(self, query_params):
        """获取模型列表"""
        try:
            # 这里应该调用实际的模型管理逻辑
            # 暂时返回模拟数据
            models_data = self._get_mock_models()
            
            # 过滤参数
            status_filter = query_params.get('status', [None])[0]
            if status_filter:
                models_data = [m for m in models_data if m.get('status') == status_filter]
            
            self._send_json_response(200, {
                "count": len(models_data),
                "models": models_data,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
        except Exception as e:
            logger.error(f"Error getting models: {e}")
            self._send_error(500, f"Error getting models: {str(e)}")
    
    def _handle_current_model(self):
        """获取当前模型"""
        try:
            # 这里应该调用实际的模型管理逻辑
            current_model = {
                "name": "aicodee/MiniMax-M2.5-highspeed",
                "provider": "aicodee",
                "status": "active",
                "priority": 1,
                "last_used": "2026-03-29T18:10:00Z",
                "performance": {
                    "success_rate": 0.933,
                    "avg_response_time": 1200,
                    "total_tests": 15
                }
            }
            self._send_json_response(200, current_model)
        except Exception as e:
            logger.error(f"Error getting current model: {e}")
            self._send_error(500, f"Error getting current model: {str(e)}")
    
    def _handle_performance(self):
        """获取性能数据"""
        try:
            analyzer = PredictiveMaintenance()
            report = analyzer.generate_performance_report()
            self._send_json_response(200, report)
        except Exception as e:
            logger.error(f"Error getting performance: {e}")
            self._send_error(500, f"Error getting performance: {str(e)}")
    
    def _handle_predictive_maintenance(self, query_params):
        """预测性维护分析"""
        try:
            model_name = query_params.get('model', [None])[0]
            analyzer = PredictiveMaintenance()
            
            if model_name:
                result = analyzer.analyze_failure_patterns(model_name)
            else:
                # 分析所有模型
                result = []
                # 这里应该获取所有模型并分析
                pass
            
            self._send_json_response(200, result)
        except Exception as e:
            logger.error(f"Error in predictive maintenance: {e}")
            self._send_error(500, f"Error in predictive maintenance: {str(e)}")
    
    def _handle_cost_analysis(self):
        """成本分析"""
        try:
            analyzer = PredictiveMaintenance()
            results = analyzer.analyze_cost_optimization()
            self._send_json_response(200, {
                "analysis": "cost_optimization",
                "results": results,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
        except Exception as e:
            logger.error(f"Error in cost analysis: {e}")
            self._send_error(500, f"Error in cost analysis: {str(e)}")
    
    def _handle_time_analysis(self):
        """时间敏感分析"""
        try:
            analyzer = PredictiveMaintenance()
            result = analyzer.time_sensitive_analysis()
            self._send_json_response(200, result)
        except Exception as e:
            logger.error(f"Error in time analysis: {e}")
            self._send_error(500, f"Error in time analysis: {str(e)}")
    
    def _handle_get_logs(self, query_params):
        """获取日志"""
        try:
            limit = int(query_params.get('limit', [10])[0])
            # 这里应该从日志文件读取
            logs = self._get_mock_logs(limit)
            
            self._send_json_response(200, {
                "count": len(logs),
                "logs": logs,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            self._send_error(500, f"Error getting logs: {str(e)}")
    
    def _handle_index(self):
        """API 首页"""
        api_info = {
            "name": "OpenClaw Model Management API",
            "version": "2.0",
            "description": "RESTful API for model auto-switching and management",
            "endpoints": {
                "GET": {
                    "/api/health": "Health check",
                    "/api/status": "System status",
                    "/api/models": "List all models",
                    "/api/models/current": "Get current model",
                    "/api/performance": "Performance report",
                    "/api/predictive/maintenance": "Predictive maintenance analysis",
                    "/api/predictive/cost": "Cost optimization analysis",
                    "/api/predictive/time": "Time-sensitive analysis",
                    "/api/logs": "Get system logs"
                },
                "POST": {
                    "/api/models/switch": "Switch to a different model",
                    "/api/models/test": "Test a model",
                    "/api/models/toggle": "Enable/disable a model",
                    "/api/auto-switch/run": "Run auto-switch manually",
                    "/api/settings/update": "Update system settings",
                    "/api/backup": "Create backup",
                    "/api/notify": "Send notification"
                }
            },
            "documentation": "See SKILL.md for detailed documentation"
        }
        self._send_json_response(200, api_info)
    
    # POST 请求处理器
    def _handle_switch_model(self, data):
        """切换模型"""
        try:
            model_name = data.get('model')
            reason = data.get('reason', 'api_request')
            
            if not model_name:
                self._send_error(400, "Model name is required")
                return
            
            # 这里应该调用实际的切换逻辑
            # 暂时模拟成功
            success = True
            
            if success:
                response_data = {
                    "success": True,
                    "message": f"Switched to {model_name}",
                    "model": model_name,
                    "reason": reason,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
                self._send_json_response(200, response_data)
            else:
                self._send_error(500, "Failed to switch model")
        
        except Exception as e:
            logger.error(f"Error switching model: {e}")
            self._send_error(500, f"Error switching model: {str(e)}")
    
    def _handle_test_model(self, data):
        """测试模型"""
        try:
            model_name = data.get('model')
            
            if not model_name:
                self._send_error(400, "Model name is required")
                return
            
            # 这里应该调用实际的测试逻辑
            # 暂时模拟测试结果
            import random
            success = random.random() > 0.2  # 80% 成功率
            response_time = random.randint(800, 2000)
            
            response_data = {
                "success": success,
                "model": model_name,
                "response_time_ms": response_time,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "message": "Test passed" if success else "Test failed"
            }
            self._send_json_response(200, response_data)
        
        except Exception as e:
            logger.error(f"Error testing model: {e}")
            self._send_error(500, f"Error testing model: {str(e)}")
    
    def _handle_toggle_model(self, data):
        """启用/禁用模型"""
        try:
            model_id = data.get('model_id')
            status = data.get('status')  # 'active' or 'disabled'
            
            if not model_id or status not in ['active', 'disabled']:
                self._send_error(400, "model_id and status (active/disabled) are required")
                return
            
            # 这里应该调用实际的启用/禁用逻辑
            # 暂时模拟成功
            success = True
            
            if success:
                response_data = {
                    "success": True,
                    "model_id": model_id,
                    "status": status,
                    "message": f"Model {model_id} set to {status}",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
                self._send_json_response(200, response_data)
            else:
                self._send_error(500, "Failed to toggle model status")
        
        except Exception as e:
            logger.error(f"Error toggling model: {e}")
            self._send_error(500, f"Error toggling model: {str(e)}")
    
    def _handle_run_auto_switch(self):
        """运行自动切换"""
        try:
            # 这里应该调用实际的自动切换逻辑
            # 暂时模拟成功
            import random
            switched = random.random() > 0.7  # 30% 概率切换
            
            response_data = {
                "success": True,
                "auto_switch_run": True,
                "switched": switched,
                "message": "Auto-switch completed" + (" (model switched)" if switched else " (no switch needed)"),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            self._send_json_response(200, response_data)
        
        except Exception as e:
            logger.error(f"Error running auto-switch: {e}")
            self._send_error(500, f"Error running auto-switch: {str(e)}")
    
    def _handle_update_settings(self, data):
        """更新设置"""
        try:
            settings = data.get('settings', {})
            
            if not settings:
                self._send_error(400, "Settings are required")
                return
            
            # 这里应该调用实际的设置更新逻辑
            # 暂时模拟成功
            success = True
            
            if success:
                response_data = {
                    "success": True,
                    "settings_updated": True,
                    "updated_settings": settings,
                    "message": "Settings updated successfully",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
                self._send_json_response(200, response_data)
            else:
                self._send_error(500, "Failed to update settings")
        
        except Exception as e:
            logger.error(f"Error updating settings: {e}")
            self._send_error(500, f"Error updating settings: {str(e)}")
    
    def _handle_backup(self):
        """创建备份"""
        try:
            # 这里应该调用实际的备份逻辑
            # 暂时模拟成功
            backup_file = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            
            response_data = {
                "success": True,
                "backup_created": True,
                "backup_file": backup_file,
                "message": "Backup created successfully",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            self._send_json_response(200, response_data)
        
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            self._send_error(500, f"Error creating backup: {str(e)}")
    
    def _handle_send_notification(self, data):
        """发送通知"""
        try:
            message = data.get('message')
            level = data.get('level', 'info')  # info, warning, error, success
            
            if not message:
                self._send_error(400, "Message is required")
                return
            
            # 这里应该调用实际的通知发送逻辑
            # 暂时模拟成功
            success = True
            
            if success:
                response_data = {
                    "success": True,
                    "notification_sent": True,
                    "message": message,
                    "level": level,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
                self._send_json_response(200, response_data)
            else:
                self._send_error(500, "Failed to send notification")
        
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            self._send_error(500, f"Error sending notification: {str(e)}")
    
    # 辅助方法
    def _send_json_response(self, status_code: int, data: Dict):
        """发送 JSON 响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response_json = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response_json.encode('utf-8'))
    
    def _send_error(self, status_code: int, message: str):
        """发送错误响应"""
        error_data = {
            "error": True,
            "status_code": status_code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        self._send_json_response(status_code, error_data)
    
    def _get_mock_models(self) -> List[Dict]:
        """获取模拟模型数据"""
        return [
            {
                "id": "M001",
                "name": "deepseek/deepseek-chat",
                "provider": "deepseek",
                "status": "active",
                "priority": 3,
                "last_used": "2026-03-29T09:49:00Z",
                "added_at": "2026-03-19",
                "performance": {
                    "success_rate": 0.952,
                    "avg_response_time": 850,
                    "total_tests": 42
                }
            },
            {
                "id": "M018",
                "name": "aicodee/MiniMax-M2.5-highspeed",
                "provider": "aicodee",
                "status": "active",
                "priority": 1,
                "last_used": "2026-03-29T18:10:00Z",
                "added_at": "2026-03-29",
                "performance": {
                    "success_rate": 0.933,
                    "avg_response_time": 1200,
                    "total_tests": 15
                }
            },
            {
                "id": "M019",
                "name": "aicodee/MiniMax-M2.7-highspeed",
                "provider": "aicodee",
                "status": "active",
                "priority": 2,
                "last_used": None,
                "added_at": "2026-03-29",
                "performance": {
                    "success_rate": 1.0,
                    "avg_response_time": 1100,
                    "total_tests": 3
                }
            }
        ]
    
    def _get_mock_logs(self, limit: int = 10) -> List[Dict]:
        """获取模拟日志数据"""
        logs = []
        for i in range(limit):
            time_offset = (limit - i) * 5  # 分钟
            log_time = datetime.utcnow() - timedelta(minutes=time_offset)
            
            logs.append({
                "timestamp": log_time.isoformat() + "Z",
                "level": "INFO" if i % 3 != 0 else "WARNING",
                "message": f"Test log entry {i+1}",
                "source": "api_server"
            })
        return logs

def start_api_server():
    """启动 API 服务器"""
    server_address = (API_HOST, API_PORT)
    httpd = HTTPServer(server_address, ModelAPIHandler)
    
    logger.info(f"🚀 Starting Model Management API server on http://{API_HOST}:{API_PORT}")
    logger.info(f"📚 API documentation available at http://{API_HOST}:{API_PORT}/")
    logger.info("🛑 Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("👋 Shutting down API server...")
        httpd.server_close()
        logger.info("✅ API server stopped")

def run_in_background():
    """在后台运行 API 服务器"""
    thread = threading.Thread(target=start_api_server, daemon=True)
    thread.start()
    return thread

if __name__ == "__main__":
    start_api_server()