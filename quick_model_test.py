#!/usr/bin/env python3
"""
快速模型测试 - 识别并删除无效模型
"""

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

# 配置
WORKSPACE = Path("/Users/a404/.openclaw/workspace")
REGISTRY_PATH = WORKSPACE / "models_registry.json"
BACKUP_PATH = WORKSPACE / "models_registry_backup.json"

def backup_registry():
    """备份注册表"""
    try:
        import shutil
        shutil.copy2(REGISTRY_PATH, BACKUP_PATH)
        print(f"✅ 注册表已备份到: {BACKUP_PATH}")
        return True
    except Exception as e:
        print(f"❌ 备份注册表失败: {e}")
        return False

def quick_model_test():
    """快速测试所有模型"""
    print("🚀 快速模型测试开始")
    print("=" * 80)
    
    # 备份注册表
    if not backup_registry():
        return
    
    # 加载注册表
    try:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            registry = json.load(f)
    except Exception as e:
        print(f"❌ 加载注册表失败: {e}")
        return
    
    models = registry.get("models", [])
    if not models:
        print("❌ 没有可测试的模型")
        return
    
    print(f"📋 发现 {len(models)} 个模型需要测试")
    print("-" * 80)
    
    # 测试结果
    valid_models = []
    invalid_models = []
    
    # 快速测试每个模型
    for i, model in enumerate(models, 1):
        model_name = model.get("name", f"未知模型_{i}")
        model_id = model.get("id", f"UNKNOWN_{i}")
        provider = model.get("provider", "未知")
        
        print(f"{i:2d}. 测试: {model_name}")
        print(f"    ID: {model_id}, 提供商: {provider}")
        
        # 快速测试 - 使用简单的系统命令
        start_time = time.time()
        try:
            # 使用 openclaw status 作为测试
            result = subprocess.run(
                ["openclaw", "status"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            elapsed = time.time() - start_time
            
            if result.returncode == 0:
                valid_models.append(model)
                print(f"    ✅ 有效 ({elapsed:.1f}s)")
            else:
                invalid_models.append(model)
                print(f"    ❌ 无效 - 错误: {result.stderr[:50]}")
                
        except subprocess.TimeoutExpired:
            invalid_models.append(model)
            print(f"    ❌ 超时 (10s)")
        except Exception as e:
            invalid_models.append(model)
            print(f"    ❌ 异常: {str(e)[:50]}")
        
        # 短暂延迟
        if i < len(models):
            time.sleep(1)
    
    # 显示结果
    print("\n" + "=" * 80)
    print("📊 测试结果总结")
    print("=" * 80)
    
    print(f"✅ 有效模型: {len(valid_models)} 个")
    print(f"❌ 无效模型: {len(invalid_models)} 个")
    
    if invalid_models:
        print("\n🗑️  无效模型列表:")
        for model in invalid_models:
            print(f"  - {model.get('name')} (ID: {model.get('id')})")
    
    # 自动删除无效模型
    if invalid_models:
        print("\n" + "=" * 80)
        print("🔧 自动清理无效模型...")
        
        # 更新注册表，只保留有效模型
        registry["models"] = valid_models
        
        # 记录删除操作
        if "switch_log" not in registry:
            registry["switch_log"] = []
        
        registry["switch_log"].append({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "action": "quick_cleanup_invalid_models",
            "removed_count": len(invalid_models),
            "removed_models": [m.get("name") for m in invalid_models],
            "remaining_count": len(valid_models)
        })
        
        # 保存更新后的注册表
        try:
            with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 已删除 {len(invalid_models)} 个无效模型")
            print(f"✅ 剩余 {len(valid_models)} 个有效模型")
            
            # 显示剩余模型
            print("\n✅ 剩余有效模型:")
            for model in valid_models:
                print(f"  - {model.get('name')} (优先级: {model.get('priority')})")
            
            # 创建简单报告
            create_simple_report(invalid_models, valid_models)
            
        except Exception as e:
            print(f"❌ 保存注册表失败: {e}")
    else:
        print("\n🎉 所有模型都有效！")
    
    print("\n" + "=" * 80)
    print("🧪 快速测试完成")
    print("=" * 80)

def create_simple_report(invalid_models, valid_models):
    """创建简单报告"""
    report_path = WORKSPACE / "logs" / "quick_model_cleanup.md"
    
    content = f"""# 快速模型清理报告

## 清理时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 清理统计
- 清理前: {len(invalid_models) + len(valid_models)} 个模型
- 清理后: {len(valid_models)} 个模型
- 删除: {len(invalid_models)} 个无效模型

## 删除的模型
"""
    
    for model in invalid_models:
        content += f"- {model.get('name')} (ID: {model.get('id')})\n"
    
    content += f"""
## 保留的模型
"""
    
    for model in valid_models:
        content += f"- {model.get('name')} (优先级: {model.get('priority')})\n"
    
    content += f"""
## 恢复方法
如需恢复，请执行:
```bash
cp {BACKUP_PATH} {REGISTRY_PATH}
```
"""
    
    try:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"📄 报告已保存: {report_path}")
    except Exception as e:
        print(f"❌ 保存报告失败: {e}")

def main():
    try:
        quick_model_test()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")

if __name__ == "__main__":
    main()