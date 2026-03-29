#!/usr/bin/env python3
"""
修复的模型管理器 - 智能切换测试版本
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
import subprocess
import time

# 配置
WORKSPACE = Path("/Users/a404/.openclaw/workspace")
REGISTRY_PATH = WORKSPACE / "models_registry.json"
LOG_FILE = WORKSPACE / "logs" / "model_switch.log"

def log_message(level: str, message: str):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"
    
    print(log_entry)
    
    # 写入日志文件
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")

def load_registry():
    """加载模型注册表"""
    if not REGISTRY_PATH.exists():
        log_message("ERROR", f"注册表文件不存在: {REGISTRY_PATH}")
        return None
    
    try:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log_message("ERROR", f"加载注册表失败: {e}")
        return None

def save_registry(registry):
    """保存模型注册表"""
    try:
        with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        log_message("INFO", "注册表已保存")
        return True
    except Exception as e:
        log_message("ERROR", f"保存注册表失败: {e}")
        return False

def get_current_model():
    """获取当前模型"""
    try:
        result = subprocess.run(
            ["openclaw", "config", "get", "agents.defaults.model.primary"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            model = result.stdout.strip()
            if model and model != "Config path not found":
                return model
        
        # 如果获取失败，尝试从注册表获取
        registry = load_registry()
        if registry and registry.get("models"):
            # 找到最后使用的模型
            used_models = [m for m in registry["models"] if m.get("last_used")]
            if used_models:
                used_models.sort(key=lambda x: x.get("last_used") or "", reverse=True)
                return used_models[0].get("name")
            
            # 如果没有使用记录，按优先级排序
            sorted_models = sorted(registry["models"], key=lambda x: x.get("priority", 999))
            return sorted_models[0].get("name")
        
        return None
    except Exception as e:
        log_message("ERROR", f"获取当前模型失败: {e}")
        return None

def switch_model(model_name: str, reason: str = "manual") -> bool:
    """切换到指定模型"""
    log_message("INFO", f"切换到模型: {model_name} (原因: {reason})")
    
    old_model = get_current_model()
    
    # 更新 OpenClaw 配置
    try:
        # 使用 set 命令更新配置
        result = subprocess.run(
            ["openclaw", "config", "set", "agents.defaults.model.primary", model_name],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            log_message("SUCCESS", f"成功切换到 {model_name}")
            
            # 更新注册表
            registry = load_registry()
            if registry:
                now = datetime.utcnow().isoformat() + "Z"
                
                # 更新模型最后使用时间
                for model in registry.get("models", []):
                    if model.get("name") == model_name:
                        model["last_used"] = now
                        break
                
                # 记录切换日志
                if "switch_log" not in registry:
                    registry["switch_log"] = []
                
                registry["switch_log"].append({
                    "timestamp": now,
                    "from": old_model,
                    "to": model_name,
                    "reason": reason,
                    "success": True
                })
                
                # 保存注册表
                save_registry(registry)
            
            return True
        else:
            log_message("ERROR", f"切换失败: {result.stderr}")
            return False
            
    except Exception as e:
        log_message("ERROR", f"切换异常: {e}")
        return False

def test_model(model_name: str) -> bool:
    """测试模型可用性"""
    log_message("INFO", f"测试模型: {model_name}")
    
    try:
        # 使用一个简单的测试命令
        result = subprocess.run(
            ["openclaw", "status"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            log_message("SUCCESS", f"模型 {model_name} 测试通过")
            return True
        else:
            log_message("WARNING", f"模型 {model_name} 测试失败")
            return False
            
    except Exception as e:
        log_message("ERROR", f"测试异常: {e}")
        return False

def auto_switch():
    """自动切换 - 智能选择最佳模型"""
    log_message("INFO", "运行智能自动切换...")
    
    # 获取当前模型
    current_model = get_current_model()
    if current_model:
        log_message("INFO", f"当前模型: {current_model}")
    else:
        log_message("WARN", "当前模型未设置，尝试设置默认模型")
    
    # 加载注册表
    registry = load_registry()
    if not registry or not registry.get("models"):
        log_message("ERROR", "没有可用的模型")
        return False
    
    models = registry["models"]
    
    # 简单评分算法：基于优先级和状态
    scored_models = []
    for model in models:
        if model.get("status") != "active":
            continue
        
        # 基础评分
        score = 0.5
        
        # 优先级调整（优先级越低越好）
        priority = model.get("priority", 999)
        if priority < 5:
            score += 0.2
        elif priority < 10:
            score += 0.1
        
        # 如果有使用记录，稍微加分
        if model.get("last_used"):
            score += 0.05
        
        scored_models.append({
            "model": model,
            "score": score
        })
    
    if not scored_models:
        log_message("ERROR", "没有活跃的模型")
        return False
    
    # 选择评分最高的模型
    scored_models.sort(key=lambda x: x["score"], reverse=True)
    best_model = scored_models[0]["model"]
    best_score = scored_models[0]["score"]
    
    log_message("INFO", f"最佳模型: {best_model['name']} (评分: {best_score:.3f})")
    
    # 如果当前模型不是最佳模型，进行切换
    if current_model != best_model["name"]:
        log_message("INFO", f"切换到模型: {best_model['name']} (原因: auto_optimization)")
        
        # 先测试模型
        if test_model(best_model["name"]):
            # 切换模型
            if switch_model(best_model["name"], "auto_optimization"):
                log_message("SUCCESS", "自动切换完成")
                return True
            else:
                log_message("ERROR", "自动切换失败")
                return False
        else:
            log_message("WARN", f"模型 {best_model['name']} 测试失败，尝试下一个")
            
            # 尝试下一个模型
            if len(scored_models) > 1:
                next_best = scored_models[1]["model"]
                log_message("INFO", f"尝试下一个最佳模型: {next_best['name']}")
                
                if test_model(next_best["name"]):
                    if switch_model(next_best["name"], "auto_fallback"):
                        log_message("SUCCESS", "回退切换完成")
                        return True
    else:
        log_message("INFO", "当前已是最佳模型，无需切换")
        return True
    
    return False

def list_models():
    """列出所有模型"""
    registry = load_registry()
    if not registry or not registry.get("models"):
        print("没有可用的模型")
        return
    
    models = registry["models"]
    current_model = get_current_model()
    
    print(f"{'ID':<6} {'名称':<40} {'提供商':<20} {'状态':<10} {'优先级':<8} {'最后使用':<20}")
    print("=" * 120)
    
    for model in models:
        model_id = model.get("id", "N/A")
        name = model.get("name", "N/A")
        provider = model.get("provider", "N/A")
        status = model.get("status", "unknown")
        priority = model.get("priority", 999)
        last_used = model.get("last_used", "从未")
        
        if last_used and last_used != "从未":
            try:
                dt = datetime.fromisoformat(last_used.replace("Z", "+00:00"))
                last_used = dt.strftime("%Y-%m-%d %H:%M")
            except:
                pass
        
        current_indicator = "★" if name == current_model else " "
        
        print(f"{current_indicator} {model_id:<5} {name:<40} {provider:<20} {status:<10} {priority:<8} {last_used:<20}")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 model_manager_fixed.py [命令]")
        print("命令:")
        print("  list        - 列出所有模型")
        print("  status      - 显示系统状态")
        print("  test <id>   - 测试指定模型")
        print("  switch <id> - 切换到指定模型")
        print("  auto        - 运行自动切换")
        print("  help        - 显示帮助")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        list_models()
    
    elif command == "status":
        current_model = get_current_model()
        registry = load_registry()
        
        if registry:
            total_models = len(registry.get("models", []))
            active_models = len([m for m in registry.get("models", []) if m.get("status") == "active"])
            
            print("=== 系统状态 ===")
            print(f"当前模型: {current_model or '未设置'}")
            print(f"总模型数: {total_models}")
            print(f"活跃模型: {active_models}")
            
            if registry.get("switch_log"):
                print(f"切换次数: {len(registry['switch_log'])}")
                last_switch = registry["switch_log"][-1]
                print(f"最后切换: {last_switch.get('to')} (原因: {last_switch.get('reason')})")
        else:
            print("无法加载系统状态")
    
    elif command == "test":
        if len(sys.argv) < 3:
            print("需要指定模型ID或名称")
            return
        
        model_id = sys.argv[2]
        registry = load_registry()
        
        if registry:
            # 查找模型
            target_model = None
            for model in registry.get("models", []):
                if model.get("id") == model_id or model.get("name") == model_id:
                    target_model = model
                    break
            
            if target_model:
                test_model(target_model["name"])
            else:
                log_message("ERROR", f"找不到模型: {model_id}")
        else:
            log_message("ERROR", "无法加载注册表")
    
    elif command == "switch":
        if len(sys.argv) < 3:
            print("需要指定模型ID或名称")
            return
        
        model_id = sys.argv[2]
        reason = sys.argv[3] if len(sys.argv) > 3 else "manual"
        
        registry = load_registry()
        
        if registry:
            # 查找模型
            target_model = None
            for model in registry.get("models", []):
                if model.get("id") == model_id or model.get("name") == model_id:
                    target_model = model
                    break
            
            if target_model:
                switch_model(target_model["name"], reason)
            else:
                log_message("ERROR", f"找不到模型: {model_id}")
        else:
            log_message("ERROR", "无法加载注册表")
    
    elif command == "auto":
        auto_switch()
    
    elif command == "help":
        print("模型管理器 - 修复版")
        print("专门用于测试智能切换功能")
    
    else:
        print(f"未知命令: {command}")
        print("使用 'help' 查看可用命令")

if __name__ == "__main__":
    main()