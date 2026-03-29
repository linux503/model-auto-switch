#!/usr/bin/env python3
"""
OpenClaw 模型管理器 - 增强版
功能：
1. 模型状态检测与自动切换
2. 性能统计与智能选择
3. 通知集成与成本统计
4. 批量操作与高级管理
"""

import json
import subprocess
import time
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import statistics
import argparse

# 配置
WORKSPACE = Path("/Users/a404/.openclaw/workspace")
REGISTRY_FILE = WORKSPACE / "models_registry.json"
CONFIG_FILE = Path("/Users/a404/.openclaw/openclaw.json")
LOG_FILE = WORKSPACE / "logs" / "model_switch.log"

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def color_text(text: str, color: str) -> str:
    """给文本添加颜色"""
    return f"{color}{text}{Colors.END}"

def log_message(level: str, message: str):
    """记录日志到文件和控制台"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"
    
    # 写入日志文件
    LOG_FILE.parent.mkdir(exist_ok=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry + "\n")
    
    # 控制台输出
    if level == "ERROR":
        print(color_text(f"[ERROR] {message}", Colors.RED))
    elif level == "WARN":
        print(color_text(f"[WARN] {message}", Colors.YELLOW))
    elif level == "INFO":
        print(color_text(f"[INFO] {message}", Colors.CYAN))
    elif level == "SUCCESS":
        print(color_text(f"[SUCCESS] {message}", Colors.GREEN))
    else:
        print(f"[{level}] {message}")

def load_registry() -> Dict:
    """加载模型注册表"""
    try:
        if REGISTRY_FILE.exists():
            with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 确保数据结构完整
            if "models" not in data:
                data["models"] = []
            if "switch_log" not in data:
                data["switch_log"] = []
            if "performance_stats" not in data:
                data["performance_stats"] = {}
            if "settings" not in data:
                data["settings"] = get_default_settings()
                
            return data
        else:
            # 创建默认注册表
            return {
                "version": "2.0",
                "created_at": datetime.utcnow().isoformat() + "Z",
                "models": [],
                "switch_log": [],
                "performance_stats": {},
                "settings": get_default_settings()
            }
    except Exception as e:
        log_message("ERROR", f"加载注册表失败: {e}")
        return {
            "version": "2.0",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "models": [],
            "switch_log": [],
            "performance_stats": {},
            "settings": get_default_settings()
        }

def save_registry(data: Dict):
    """保存模型注册表"""
    try:
        with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        log_message("INFO", "注册表已保存")
    except Exception as e:
        log_message("ERROR", f"保存注册表失败: {e}")

def get_default_settings() -> Dict:
    """获取默认设置"""
    return {
        "auto_switch_enabled": True,
        "check_interval_minutes": 5,
        "max_retries": 3,
        "retry_delay_seconds": 2,
        "test_timeout_seconds": 15,
        "notify_on_switch": True,
        "notify_on_failure": True,
        "telegram_chat_id": "telegram:2039643883",
        "performance_weight_response_time": 0.4,
        "performance_weight_success_rate": 0.6,
        "min_success_rate_for_auto_switch": 0.7,
        "max_response_time_ms": 30000,
        "log_retention_days": 7,
        "max_log_size_mb": 10,
        "backup_enabled": True,
        "backup_interval_hours": 24
    }

def get_current_model() -> Optional[str]:
    """获取当前配置的主模型"""
    try:
        result = subprocess.run(
            ["openclaw", "config", "get", "--path", "agents.defaults.model.primary"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            model = result.stdout.strip()
            if model.startswith('"') and model.endswith('"'):
                model = model[1:-1]
            return model if model else None
    except Exception as e:
        log_message("ERROR", f"获取当前模型失败: {e}")
    return None

def test_model_with_stats(model_name: str, test_prompt: str = "Hello, please respond with 'OK'") -> Tuple[bool, float, Optional[str]]:
    """
    测试模型并收集统计信息
    返回: (是否成功, 响应时间ms, 错误信息)
    """
    log_message("INFO", f"测试模型: {model_name}")
    
    start_time = time.time()
    success = False
    error_msg = None
    response_time = None
    
    try:
        # 使用 session-status 测试模型
        env = os.environ.copy()
        env["OPENCLAW_MODEL_OVERRIDE"] = model_name
        
        result = subprocess.run(
            ["openclaw", "session-status"],
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )
        
        response_time = (time.time() - start_time) * 1000  # 转换为毫秒
        
        if result.returncode == 0:
            success = True
            log_message("SUCCESS", f"模型 {model_name} 测试通过，响应时间: {response_time:.0f}ms")
        else:
            error_msg = result.stderr[:200] if result.stderr else "Unknown error"
            log_message("WARN", f"模型 {model_name} 测试失败: {error_msg}")
            
    except subprocess.TimeoutExpired:
        response_time = (time.time() - start_time) * 1000
        error_msg = f"测试超时 ({response_time:.0f}ms)"
        log_message("WARN", f"模型 {model_name} 测试超时")
    except Exception as e:
        response_time = (time.time() - start_time) * 1000 if 'start_time' in locals() else 0
        error_msg = str(e)
        log_message("ERROR", f"模型 {model_name} 测试异常: {e}")
    
    return success, response_time, error_msg

def update_performance_stats(model_name: str, success: bool, response_time: float):
    """更新模型性能统计"""
    registry = load_registry()
    
    if "performance_stats" not in registry:
        registry["performance_stats"] = {}
    
    if model_name not in registry["performance_stats"]:
        registry["performance_stats"][model_name] = {
            "total_tests": 0,
            "successful_tests": 0,
            "failed_tests": 0,
            "response_times": [],
            "last_test_time": None,
            "avg_response_time": 0,
            "success_rate": 0
        }
    
    stats = registry["performance_stats"][model_name]
    stats["total_tests"] += 1
    
    if success:
        stats["successful_tests"] += 1
        if response_time:
            stats["response_times"].append(response_time)
            # 只保留最近100个响应时间
            if len(stats["response_times"]) > 100:
                stats["response_times"] = stats["response_times"][-100:]
            stats["avg_response_time"] = statistics.mean(stats["response_times"]) if stats["response_times"] else 0
    else:
        stats["failed_tests"] += 1
    
    stats["last_test_time"] = datetime.utcnow().isoformat() + "Z"
    stats["success_rate"] = stats["successful_tests"] / stats["total_tests"] if stats["total_tests"] > 0 else 0
    
    save_registry(registry)
    log_message("INFO", f"更新 {model_name} 性能统计: 成功率={stats['success_rate']:.1%}, 平均响应={stats['avg_response_time']:.0f}ms")

def calculate_model_score(model_name: str) -> float:
    """计算模型综合评分（用于智能选择）"""
    registry = load_registry()
    settings = registry.get("settings", get_default_settings())
    
    if model_name not in registry.get("performance_stats", {}):
        return 0.5  # 默认分数
    
    stats = registry["performance_stats"][model_name]
    
    if stats["total_tests"] < 3:
        return 0.5  # 测试数据不足
    
    # 响应时间分数（越短越好）
    max_response_time = settings.get("max_response_time_ms", 30000)
    response_time_score = 1.0 - min(stats["avg_response_time"] / max_response_time, 1.0)
    
    # 成功率分数
    success_rate_score = stats["success_rate"]
    
    # 综合评分
    weight_rt = settings.get("performance_weight_response_time", 0.4)
    weight_sr = settings.get("performance_weight_success_rate", 0.6)
    
    score = (response_time_score * weight_rt) + (success_rate_score * weight_sr)
    
    # 根据优先级调整（优先级越高，分数越高）
    for model in registry.get("models", []):
        if model["name"] == model_name:
            priority = model.get("priority", 10)
            priority_factor = 1.0 / (priority * 0.1)  # 优先级1得1.0，优先级10得0.1
            score *= (0.7 + 0.3 * priority_factor)  # 优先级影响30%
            break
    
    return min(max(score, 0.0), 1.0)

def switch_model(model_name: str, reason: str = "manual", notify: bool = True) -> bool:
    """切换到指定模型"""
    log_message("INFO", f"切换到模型: {model_name} (原因: {reason})")
    
    old_model = get_current_model()
    
    # 更新 OpenClaw 配置
    try:
        patch = {
            "agents": {
                "defaults": {
                    "model": {
                        "primary": model_name
                    }
                }
            }
        }
        
        # 保存 patch 到临时文件
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            json.dump(patch, tmp)
            tmp_path = tmp.name
        
        result = subprocess.run(
            ["openclaw", "config", "patch", "--file", tmp_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        Path(tmp_path).unlink()
        
        if result.returncode == 0:
            log_message("SUCCESS", f"成功切换到 {model_name}")
            
            # 更新注册表
            registry = load_registry()
            now = datetime.utcnow().isoformat() + "Z"
            
            # 更新模型最后使用时间
            for model in registry["models"]:
                if model["name"] == model_name:
                    model["last_used"] = now
                    break
            
            # 记录切换日志
            registry["switch_log"].append({
                "timestamp": now,
                "from": old_model,
                "to": model_name,
                "reason": reason,
                "success": True,
                "notified": False
            })
            
            # 只保留最近500条日志
            if len(registry["switch_log"]) > 500:
                registry["switch_log"] = registry["switch_log"][-500:]
            
            save_registry(registry)
            
            # 发送通知
            if notify and registry.get("settings", {}).get("notify_on_switch", True):
                send_notification(f"🔁 模型切换: {old_model or '未知'} → {model_name}\n原因: {reason}")
            
            return True
        else:
            error_msg = result.stderr[:200] if result.stderr else "Unknown error"
            log_message("ERROR", f"切换失败: {error_msg}")
            
            # 记录失败日志
            registry = load_registry()
            registry["switch_log"].append({
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "from": old_model,
                "to": model_name,
                "reason": reason,
                "success": False,
                "error": error_msg
            })
            save_registry(registry)
            
            return False
            
    except Exception as e:
        log_message("ERROR", f"切换异常: {e}")
        return False

def send_notification(message: str):
    """发送通知到 Telegram"""
    try:
        registry = load_registry()
        settings = registry.get("settings", get_default_settings())
        chat_id = settings.get("telegram_chat_id", "telegram:2039643883")
        
        # 添加时间戳
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_message = f"🦞 [{timestamp}] {message}"
        
        result = subprocess.run(
            ["openclaw", "message", "send",
             "--channel", "telegram",
             "--to", chat_id,
             "--message", full_message],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            log_message("INFO", "通知发送成功")
        else:
            log_message("WARN", f"通知发送失败: {result.stderr[:100]}")
            
    except Exception as e:
        log_message("ERROR", f"发送通知异常: {e}")

def auto_switch_with_intelligence():
    """智能自动切换"""
    registry = load_registry()
    settings = registry.get("settings", get_default_settings())
    
    if not settings.get("auto_switch_enabled", True):
        log_message("INFO", "自动切换已禁用")
        return
    
    current_model = get_current_model()
    log_message("INFO", f"当前模型: {current_model or '未设置'}")
    
    if not current_model:
        log_message("WARN", "当前模型未设置，尝试设置默认模型")
        # 尝试设置第一个可用模型
        active_models = [m for m in registry.get("models", []) if m.get("status") == "active"]
        if active_models:
            best_model = find_best_model(active_models)
            if best_model:
                switch_model(best_model["name"], "auto_set_default")
        return
    
    # 测试当前模型
    success, response_time, error_msg = test_model_with_stats(current_model)
    update_performance_stats(current_model, success, response_time)
    
    if success:
        log_message("SUCCESS", f"当前模型正常，响应时间: {response_time:.0f}ms")
        
        # 检查性能是否达标
        stats = registry.get("performance_stats", {}).get(current_model, {})
        success_rate = stats.get("success_rate", 0)
        avg_response = stats.get("avg_response_time", 0)
        
        min_success_rate = settings.get("min_success_rate_for_auto_switch", 0.7)
        max_response_time = settings.get("max_response_time_ms", 30000)
        
        if success_rate < min_success_rate or avg_response > max_response_time:
            log_message("WARN", f"模型性能不达标: 成功率={success_rate:.1%}, 响应时间={avg_response:.0f}ms")
            find_and_switch_better_model(current_model, "performance_issue")
        return
    
    # 当前模型失败，寻找替代模型
    log_message("WARN", f"当前模型不可用: {error_msg}")
    find_and_switch_better_model(current_model, "model_failure")

def find_best_model(active_models: List[Dict]) -> Optional[Dict]:
    """根据评分找到最佳模型"""
    if not active_models:
        return None
    
    best_model = None
    best_score = -1
    
    for model in active_models:
        score = calculate_model_score(model["name"])
        log_message("DEBUG", f"模型 {model['name']} 评分: {score:.3f}")
        
        if score > best_score:
            best_score = score
            best_model = model
    
    if best_model:
        log_message("INFO", f"最佳模型: {best_model['name']} (评分: {best_score:.3f})")
    
    return best_model

def find_and_switch_better_model(current_model: str, reason: str):
    """寻找并切换到更好的模型"""
    registry = load_registry()
    
    # 获取所有活跃模型（排除当前模型）
    active_models = [
        m for m in registry.get("models", []) 
        if m.get("status") == "active" and m["name"] != current_model
    ]
    
    if not active_models:
        log_message("ERROR", "没有可用的备用模型")
        if registry.get("settings", {}).get("notify_on_failure", True):
            send_notification(f"⚠️ 所有模型都不可用！当前模型: {current_model}")
        return
    
    log_message("INFO", f"开始测试 {len(active_models)} 个备用模型...")
    
    # 按优先级排序
    active_models.sort(key=lambda x: x.get("priority", 999))
    
    # 测试每个模型
    tested_models = []
    for model in active_models:
        model_name = model["name"]
        
        # 重试机制
        max_retries = registry.get("settings", {}).get("max_retries", 3)
        retry_delay = registry.get("settings", {}).get("retry_delay_seconds", 2)
        
        for attempt in range(max_retries):
            if attempt > 0:
                log_message("INFO", f"第 {attempt + 1} 次重试 {model_name}...")
                time.sleep(retry_delay)
            
            success, response_time, error_msg = test_model_with_stats(model_name)
            update_performance_stats(model_name, success, response_time)
            
            if success:
                tested_models.append({
                    "model": model,
                    "response_time": response_time,
                    "score": calculate_model_score(model_name)
                })
                break
            elif attempt == max_retries - 1:
                log_message("WARN", f"模型 {model_name} 测试失败: {error_msg}")
    
    if not tested_models:
        log_message("ERROR", "所有备用模型测试都失败")
        if registry.get("settings", {}).get("notify_on_failure", True):
            send_notification(f"❌ 所有备用模型都不可用！当前模型: {current_model}")
        return
    
    # 按评分排序
    tested_models.sort(key=lambda x: x["score"], reverse=True)
    
    best_candidate = tested_models[0]
    best_model = best_candidate["model"]
    best_score = best_candidate["score"]
    
    log_message("INFO", f"选择模型: {best_model['name']} (评分: {best_score:.3f}, 响应: {best_candidate['response_time']:.0f}ms)")
    
    # 切换到最佳模型
    if switch_model(best_model["name"], f"auto_switch_{reason}", notify=True):
        # 更新性能统计
        stats = registry.get("performance_stats", {}).get(best_model["name"], {})
        success_rate = stats.get("success_rate", 0)
        avg_response = stats.get("avg_response_time", 0)
        
        log_message("SUCCESS", f"自动切换完成: {current_model} → {best_model['name']}")
        log_message("INFO", f"新模型性能: 成功率={success_rate:.1%}, 平均响应={avg_response:.0f}ms")
    else:
        log_message("ERROR", "自动切换失败")

def list_models_detailed():
    """详细列出所有模型"""
    registry = load_registry()
    current_model = get_current_model()
    
    print("\n" + "="*120)
    print(f"{'模型管理面板':^120}")
    print("="*120)
    print(f"{'当前模型:':<20} {color_text(current_model or '未设置', Colors.CYAN + Colors.BOLD)}")
    print(f"{'活跃模型:':<20} {sum(1 for m in registry.get('models', []) if m.get('status') == 'active')}/{len(registry.get('models', []))}")
    print(f"{'自动切换:':<20} {'启用' if registry.get('settings', {}).get('auto_switch_enabled', True) else '禁用'}")
    print("="*120)
    
    # 表头
    header = f"{'ID':<4} | {'模型名称':<35} | {'状态':<6} | {'优先级':<3} | {'评分':<6} | {'成功率':<6} | {'响应时间':<10} | {'最后使用':<12}"
    print(color_text(header, Colors.BOLD))
    print("-" * 120)
    
    # 按优先级排序
    models = sorted(registry.get("models", []), key=lambda x: x.get("priority", 999))
    
    for model in models:
        model_name = model["name"]
        is_current = model_name == current_model
        
        # 获取性能统计
        stats = registry.get("performance_stats", {}).get(model_name, {})
        success_rate = stats.get("success_rate", 0)
        avg_response = stats.get("avg_response_time", 0)
        score = calculate_model_score(model_name)
        
        # 状态图标
        status_icon = "✓" if model.get("status") == "active" else "✗"
        status_color = Colors.GREEN if model.get("status") == "active" else Colors.RED
        
        # 当前模型标记
        current_icon = color_text("★", Colors.YELLOW + Colors.BOLD) if is_current else " "
        
        # 评分颜色
        if score >= 0.8:
            score_color = Colors.GREEN
        elif score >= 0.6:
            score_color = Colors.YELLOW
        else:
            score_color = Colors.RED
        
        # 成功率颜色
        if success_rate >= 0.9:
            success_color = Colors.GREEN
        elif success_rate >= 0.7:
            success_color = Colors.YELLOW
        else:
            success_color = Colors.RED
        
        # 响应时间颜色
        if avg_response < 1000:
            response_color = Colors.GREEN
        elif avg_response < 3000:
            response_color = Colors.YELLOW
        else:
            response_color = Colors.RED
        
        # 最后使用时间
        last_used = model.get("last_used", "")
        if last_used:
            last_used = last_used[:10]  # 只显示日期
        
        # 输出行
        line = (f"{current_icon} {model['id']:<4} | "
                f"{color_text(model_name[:34], Colors.CYAN if is_current else Colors.WHITE):<35} | "
                f"{color_text(status_icon + ' ' + model.get('status', 'unknown'), status_color):<6} | "
                f"{model.get('priority', 999):<3} | "
                f"{color_text(f'{score:.3f}', score_color):<6} | "
                f"{color_text(f'{success_rate:.1%}', success_color):<6} | "
                f"{color_text(f'{avg_response:.0f}ms', response_color):<10} | "
                f"{last_used:<12}")
        
        print(line)
    
    print("="*120)
    
    # 显示统计信息
    if registry.get("performance_stats"):
        total_tests = sum(stats.get("total_tests", 0) for stats in registry["performance_stats"].values())
        if total_tests > 0:
            print(f"\n📊 性能统计: 共进行 {total_tests} 次测试")
            
            # 显示最佳模型
            best_models = sorted(
                [(name, calculate_model_score(name)) for name in registry["performance_stats"].keys()],
                key=lambda x: x[1],
                reverse=True
            )[:3]
            
            if best_models:
                print("🏆 最佳模型:")
                for i, (model_name, score) in enumerate(best_models, 1):
                    stats = registry["performance_stats"][model_name]
                    print(f"  {i}. {model_name:<35} 评分: {score:.3f} 成功率: {stats.get('success_rate', 0):.1%} 响应: {stats.get('avg_response_time', 0):.0f}ms")

def show_dashboard():
    """显示仪表板"""
    registry = load_registry()
    current_model = get_current_model()
    
    print("\n" + "="*80)
    print(color_text(f"{'模型管理系统仪表板':^80}", Colors.BOLD + Colors.CYAN))
    print("="*80)
    
    # 当前状态
    print(color_text("\n📈 当前状态", Colors.BOLD))
    print(f"  • 当前模型: {color_text(current_model or '未设置', Colors.CYAN)}")
    
    active_count = sum(1 for m in registry.get("models", []) if m.get("status") == "active")
    print(f"  • 活跃模型: {color_text(str(active_count), Colors.GREEN)}/{len(registry.get('models', []))}")
    
    settings = registry.get("settings", get_default_settings())
    print(f"  • 自动切换: {color_text('启用' if settings.get('auto_switch_enabled', True) else '禁用', Colors.GREEN if settings.get('auto_switch_enabled', True) else Colors.RED)}")
    print(f"  • 检测间隔: {settings.get('check_interval_minutes', 5)} 分钟")
    
    # 最近切换
    switch_log = registry.get("switch_log", [])
    if switch_log:
        print(color_text("\n🔄 最近切换", Colors.BOLD))
        for log in switch_log[-3:][::-1]:  # 显示最近3条
            timestamp = log.get("timestamp", "")[:19].replace("T", " ")
            success_icon = "✓" if log.get("success") else "✗"
            color = Colors.GREEN if log.get("success") else Colors.RED
            print(f"  • {timestamp} {color(success_icon, color)} {log.get('from', '?')} → {log.get('to', '?')}")
    
    # 性能概览
    if registry.get("performance_stats"):
        print(color_text("\n⚡ 性能概览", Colors.BOLD))
        
        # 计算总体统计
        all_stats = list(registry["performance_stats"].values())
        if all_stats:
            total_tests = sum(s.get("total_tests", 0) for s in all_stats)
            avg_success_rate = statistics.mean([s.get("success_rate", 0) for s in all_stats if s.get("total_tests", 0) > 0]) if any(s.get("total_tests", 0) > 0 for s in all_stats) else 0
            avg_response = statistics.mean([s.get("avg_response_time", 0) for s in all_stats if s.get("avg_response_time", 0) > 0]) if any(s.get("avg_response_time", 0) > 0 for s in all_stats) else 0
            
            print(f"  • 总测试次数: {total_tests}")
            print(f"  • 平均成功率: {color_text(f'{avg_success_rate:.1%}', Colors.GREEN if avg_success_rate >= 0.9 else Colors.YELLOW if avg_success_rate >= 0.7 else Colors.RED)}")
            print(f"  • 平均响应时间: {color_text(f'{avg_response:.0f}ms', Colors.GREEN if avg_response < 1000 else Colors.YELLOW if avg_response < 3000 else Colors.RED)}")
    
    # 系统信息
    print(color_text("\n🔧 系统信息", Colors.BOLD))
    print(f"  • 注册表版本: {registry.get('version', '1.0')}")
    print(f"  • 创建时间: {registry.get('created_at', '')[:10]}")
    print(f"  • 日志文件: {LOG_FILE}")
    
    print("\n" + "="*80)
    print(color_text("💡 使用 'python3 model_manager_enhanced.py --help' 查看所有命令", Colors.YELLOW))
    print("="*80)

def backup_registry():
    """备份注册表"""
    try:
        if not REGISTRY_FILE.exists():
            return
        
        backup_dir = WORKSPACE / "backups" / "model_registry"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"models_registry_{timestamp}.json"
        
        import shutil
        shutil.copy2(REGISTRY_FILE, backup_file)
        
        # 清理旧备份（保留最近7天）
        for file in backup_dir.glob("models_registry_*.json"):
            file_age = datetime.now() - datetime.fromtimestamp(file.stat().st_mtime)
            if file_age.days > 7:
                file.unlink()
        
        log_message("INFO", f"注册表已备份到: {backup_file}")
    except Exception as e:
        log_message("ERROR", f"备份注册表失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="OpenClaw 模型管理器 - 增强版")
    parser.add_argument("command", nargs="?", help="命令: list, status, test, switch, auto, dashboard, backup, notify")
    parser.add_argument("args", nargs="*", help="命令参数")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--quiet", "-q", action="store_true", help="安静模式")
    
    args = parser.parse_args()
    
    # 设置日志级别
    global LOG_LEVEL
    if args.quiet:
        LOG_LEVEL = "ERROR"
    elif args.verbose:
        LOG_LEVEL = "DEBUG"
    else:
        LOG_LEVEL = "INFO"
    
    if not args.command:
        show_dashboard()
        return
    
    command = args.command.lower()
    
    if command == "list":
        list_models_detailed()
    
    elif command == "status":
        current = get_current_model()
        registry = load_registry()
        active_count = sum(1 for m in registry.get("models", []) if m.get("status") == "active")
        
        print(f"当前模型: {current or '未设置'}")
        print(f"活跃模型: {active_count}/{len(registry.get('models', []))}")
        print(f"自动切换: {'启用' if registry.get('settings', {}).get('auto_switch_enabled', True) else '禁用'}")
        
        # 显示最近一次切换
        logs = registry.get("switch_log", [])
        if logs:
            last = logs[-1]
            print(f"最近切换: {last.get('timestamp', '')[:19]} {last.get('from', '?')} → {last.get('to', '?')}")
    
    elif command == "test":
        if args.args:
            model_name = args.args[0]
        else:
            model_name = get_current_model()
        
        if not model_name:
            print("错误: 未指定模型且当前模型未设置")
            return
        
        success, response_time, error_msg = test_model_with_stats(model_name)
        update_performance_stats(model_name, success, response_time)
        
        if success:
            print(f"✅ 测试通过 - 响应时间: {response_time:.0f}ms")
        else:
            print(f"❌ 测试失败 - {error_msg}")
    
    elif command == "switch":
        if not args.args:
            print("错误: 请指定要切换的模型名称")
            return
        
        model_name = args.args[0]
        reason = args.args[1] if len(args.args) > 1 else "manual"
        
        if switch_model(model_name, reason):
            print(f"✅ 成功切换到 {model_name}")
        else:
            print(f"❌ 切换到 {model_name} 失败")
    
    elif command == "auto":
        print("运行智能自动切换...")
        auto_switch_with_intelligence()
    
    elif command == "dashboard":
        show_dashboard()
    
    elif command == "backup":
        print("备份注册表...")
        backup_registry()
    
    elif command == "notify":
        if not args.args:
            print("错误: 请指定通知内容")
            return
        
        message = " ".join(args.args)
        send_notification(message)
        print("通知已发送")
    
    elif command == "help":
        parser.print_help()
        print("\n示例:")
        print("  python3 model_manager_enhanced.py list          # 列出所有模型")
        print("  python3 model_manager_enhanced.py status        # 显示状态")
        print("  python3 model_manager_enhanced.py test          # 测试当前模型")
        print("  python3 model_manager_enhanced.py test <model>  # 测试指定模型")
        print("  python3 model_manager_enhanced.py switch <model> # 切换到指定模型")
        print("  python3 model_manager_enhanced.py auto          # 运行自动切换")
        print("  python3 model_manager_enhanced.py dashboard     # 显示仪表板")
        print("  python3 model_manager_enhanced.py backup        # 备份注册表")
        print("  python3 model_manager_enhanced.py notify <msg>  # 发送通知")
    
    else:
        print(f"错误: 未知命令 '{command}'")
        print("使用 'python3 model_manager_enhanced.py help' 查看帮助")

if __name__ == "__main__":
    # 全局日志级别
    LOG_LEVEL = "INFO"
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n操作被用户中断")
        sys.exit(0)
    except Exception as e:
        log_message("ERROR", f"程序异常: {e}")
        print(f"\n❌ 程序异常: {e}")
        sys.exit(1)