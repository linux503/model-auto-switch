#!/usr/bin/env python3
"""
OpenClaw 模型管理器
功能：
1. 模型状态检测
2. 自动切换策略
3. 模型管理记录
"""

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
import sys

WORKSPACE = Path("/Users/a404/.openclaw/workspace")
REGISTRY_FILE = WORKSPACE / "models_registry.json"
CONFIG_FILE = Path("/Users/a404/.openclaw/openclaw.json")

def load_registry():
    """加载模型注册表"""
    if REGISTRY_FILE.exists():
        with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"models": [], "switch_log": [], "settings": {}}

def save_registry(data):
    """保存模型注册表"""
    with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_current_model():
    """获取当前配置的主模型"""
    try:
        result = subprocess.run(
            ["openclaw", "config", "get", "--path", "agents.defaults.model.primary"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            # 提取模型名称，去除引号
            model = result.stdout.strip()
            if model.startswith('"') and model.endswith('"'):
                model = model[1:-1]
            return model
    except Exception as e:
        print(f"获取当前模型失败: {e}")
    return None

def test_model(model_name):
    """测试模型是否可用"""
    print(f"测试模型: {model_name}")
    try:
        # 使用一个简单的查询来测试模型
        result = subprocess.run(
            ["openclaw", "session-status"],
            capture_output=True,
            text=True,
            timeout=15,
            env={**os.environ, "OPENCLAW_MODEL_OVERRIDE": model_name}
        )
        
        if result.returncode == 0:
            print(f"✓ 模型 {model_name} 测试通过")
            return True
        else:
            print(f"✗ 模型 {model_name} 测试失败: {result.stderr[:100]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"✗ 模型 {model_name} 测试超时")
        return False
    except Exception as e:
        print(f"✗ 模型 {model_name} 测试异常: {e}")
        return False

def switch_model(model_name, reason="manual"):
    """切换到指定模型"""
    print(f"切换到模型: {model_name}")
    
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
            print(f"✓ 成功切换到 {model_name}")
            
            # 更新注册表
            registry = load_registry()
            now = datetime.utcnow().isoformat() + "Z"
            
            # 更新模型最后使用时间
            for model in registry["models"]:
                if model["name"] == model_name:
                    model["last_used"] = now
                    break
            
            # 记录切换日志
            old_model = get_current_model()  # 切换前的模型
            registry["switch_log"].append({
                "timestamp": now,
                "from": old_model,
                "to": model_name,
                "reason": reason,
                "success": True
            })
            
            # 只保留最近100条日志
            if len(registry["switch_log"]) > 100:
                registry["switch_log"] = registry["switch_log"][-100:]
            
            save_registry(registry)
            return True
        else:
            print(f"✗ 切换失败: {result.stderr[:200]}")
            return False
            
    except Exception as e:
        print(f"✗ 切换异常: {e}")
        return False

def auto_switch_if_needed():
    """自动检测并切换模型（如果需要）"""
    registry = load_registry()
    if not registry.get("settings", {}).get("auto_switch_enabled", True):
        print("自动切换已禁用")
        return
    
    current_model = get_current_model()
    print(f"当前模型: {current_model}")
    
    # 测试当前模型
    if test_model(current_model):
        print("✓ 当前模型正常，无需切换")
        return
    
    print("⚠️ 当前模型不可用，开始尝试备用模型...")
    
    # 按优先级排序获取可用模型
    active_models = [m for m in registry["models"] if m["status"] == "active"]
    active_models.sort(key=lambda x: x.get("priority", 999))
    
    for model in active_models:
        model_name = model["name"]
        if model_name == current_model:
            continue  # 跳过当前模型
        
        print(f"尝试模型: {model_name} (优先级: {model.get('priority', 'N/A')})")
        
        if test_model(model_name):
            print(f"✓ 模型 {model_name} 可用，开始切换...")
            if switch_model(model_name, reason="auto_switch_fallback"):
                # 发送通知（可选）
                send_notification(f"模型自动切换: {current_model} → {model_name}")
                return
            else:
                print(f"✗ 切换到 {model_name} 失败，继续尝试下一个")
        else:
            print(f"✗ 模型 {model_name} 不可用")
    
    print("✗ 所有备用模型都不可用")

def send_notification(message):
    """发送通知（Telegram）"""
    try:
        # 这里可以集成 Telegram 通知
        # 暂时先打印
        print(f"通知: {message}")
        
        # 示例：发送到 Telegram（需要配置）
        # subprocess.run([
        #     "openclaw", "message", "send",
        #     "--channel", "telegram",
        #     "--to", "telegram:2039643883",
        #     "--message", message
        # ])
    except Exception as e:
        print(f"发送通知失败: {e}")

def list_models():
    """列出所有模型"""
    registry = load_registry()
    current_model = get_current_model()
    
    print("\n" + "="*80)
    print("模型列表 (ID | 名称 | 状态 | 优先级 | 最后使用 | 添加时间)")
    print("="*80)
    
    for model in registry["models"]:
        status_icon = "✓" if model["status"] == "active" else "✗"
        current_icon = "★" if model["name"] == current_model else " "
        
        last_used = model.get("last_used", "从未使用")
        if last_used:
            # 简化时间显示
            last_used = last_used[:10] if len(last_used) > 10 else last_used
        
        added_at = model.get("added_at", "未知")[:10]
        
        print(f"{current_icon} {model['id']:4} | {model['name']:35} | {status_icon} {model['status']:6} | "
              f"{model.get('priority', 999):3} | {last_used:12} | {added_at}")

def show_switch_log(limit=10):
    """显示切换日志"""
    registry = load_registry()
    logs = registry.get("switch_log", [])
    
    print("\n" + "="*80)
    print(f"切换日志 (最近 {min(limit, len(logs))} 条)")
    print("="*80)
    
    for log in logs[-limit:]:
        timestamp = log.get("timestamp", "")[:19].replace("T", " ")
        success_icon = "✓" if log.get("success") else "✗"
        print(f"{timestamp} | {success_icon} {log.get('from', '?')} → {log.get('to', '?')} | {log.get('reason', '')}")

def update_model_status(model_id, status):
    """更新模型状态"""
    registry = load_registry()
    
    for model in registry["models"]:
        if model["id"] == model_id:
            old_status = model["status"]
            model["status"] = status
            save_registry(registry)
            print(f"✓ 模型 {model['name']} 状态更新: {old_status} → {status}")
            return True
    
    print(f"✗ 未找到模型 ID: {model_id}")
    return False

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python model_manager.py <命令> [参数]")
        print("命令:")
        print("  list                   列出所有模型")
        print("  test [model]           测试模型（不指定则测试当前模型）")
        print("  switch <model>         切换到指定模型")
        print("  auto                   自动检测并切换（如果需要）")
        print("  log [limit]            显示切换日志")
        print("  enable <model_id>      启用模型")
        print("  disable <model_id>     禁用模型")
        print("  status                 显示当前状态")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        list_models()
    
    elif command == "test":
        if len(sys.argv) > 2:
            model_name = sys.argv[2]
            test_model(model_name)
        else:
            current = get_current_model()
            if current:
                test_model(current)
            else:
                print("✗ 无法获取当前模型")
    
    elif command == "switch":
        if len(sys.argv) > 2:
            model_name = sys.argv[2]
            switch_model(model_name, reason="manual")
        else:
            print("✗ 请指定要切换的模型名称")
    
    elif command == "auto":
        auto_switch_if_needed()
    
    elif command == "log":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        show_switch_log(limit)
    
    elif command == "enable":
        if len(sys.argv) > 2:
            update_model_status(sys.argv[2], "active")
        else:
            print("✗ 请指定模型ID")
    
    elif command == "disable":
        if len(sys.argv) > 2:
            update_model_status(sys.argv[2], "disabled")
        else:
            print("✗ 请指定模型ID")
    
    elif command == "status":
        current = get_current_model()
        registry = load_registry()
        active_count = sum(1 for m in registry["models"] if m["status"] == "active")
        
        print(f"当前模型: {current}")
        print(f"活跃模型: {active_count}/{len(registry['models'])}")
        print(f"自动切换: {'启用' if registry.get('settings', {}).get('auto_switch_enabled', True) else '禁用'}")
        
        # 显示最近一次切换
        logs = registry.get("switch_log", [])
        if logs:
            last = logs[-1]
            print(f"最近切换: {last.get('timestamp', '')[:19]} {last.get('from', '?')} → {last.get('to', '?')}")
    
    else:
        print(f"✗ 未知命令: {command}")

if __name__ == "__main__":
    main()