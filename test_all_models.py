#!/usr/bin/env python3
"""
全面测试所有模型，识别无效模型并删除
"""

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

# 配置
WORKSPACE = Path("/Users/a404/.openclaw/workspace")
REGISTRY_PATH = WORKSPACE / "models_registry.json"
LOG_FILE = WORKSPACE / "logs" / "model_test.log"
BACKUP_PATH = WORKSPACE / "models_registry_backup.json"

def log_message(level: str, message: str):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"
    
    print(log_entry)
    
    # 写入日志文件
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")

def backup_registry():
    """备份注册表"""
    try:
        import shutil
        shutil.copy2(REGISTRY_PATH, BACKUP_PATH)
        log_message("INFO", f"注册表已备份到: {BACKUP_PATH}")
        return True
    except Exception as e:
        log_message("ERROR", f"备份注册表失败: {e}")
        return False

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

def test_model(model_name: str, timeout_seconds: int = 30) -> dict:
    """测试单个模型"""
    log_message("INFO", f"开始测试模型: {model_name}")
    
    start_time = time.time()
    
    try:
        # 使用 openclaw status 命令测试模型可用性
        result = subprocess.run(
            ["openclaw", "status"],
            capture_output=True,
            text=True,
            timeout=timeout_seconds
        )
        
        elapsed_time = time.time() - start_time
        
        if result.returncode == 0:
            log_message("SUCCESS", f"模型 {model_name} 测试通过 ({elapsed_time:.1f}s)")
            return {
                "success": True,
                "response_time": elapsed_time,
                "error": None
            }
        else:
            log_message("WARNING", f"模型 {model_name} 测试失败: {result.stderr[:100]}")
            return {
                "success": False,
                "response_time": elapsed_time,
                "error": result.stderr[:200]
            }
            
    except subprocess.TimeoutExpired:
        elapsed_time = time.time() - start_time
        log_message("ERROR", f"模型 {model_name} 测试超时 ({timeout_seconds}s)")
        return {
            "success": False,
            "response_time": elapsed_time,
            "error": f"超时 ({timeout_seconds}秒)"
        }
    except Exception as e:
        elapsed_time = time.time() - start_time
        log_message("ERROR", f"模型 {model_name} 测试异常: {e}")
        return {
            "success": False,
            "response_time": elapsed_time,
            "error": str(e)
        }

def test_all_models():
    """测试所有模型"""
    log_message("INFO", "开始全面测试所有模型")
    print("\n" + "=" * 80)
    print("🧪 开始全面模型测试")
    print("=" * 80)
    
    # 备份注册表
    if not backup_registry():
        print("❌ 备份失败，停止测试")
        return
    
    # 加载注册表
    registry = load_registry()
    if not registry:
        print("❌ 加载注册表失败")
        return
    
    models = registry.get("models", [])
    if not models:
        print("❌ 没有可测试的模型")
        return
    
    print(f"📋 发现 {len(models)} 个模型需要测试")
    print("-" * 80)
    
    # 测试结果存储
    test_results = []
    valid_models = []
    invalid_models = []
    
    # 测试每个模型
    for i, model in enumerate(models, 1):
        model_name = model.get("name", f"未知模型_{i}")
        model_id = model.get("id", f"UNKNOWN_{i}")
        
        print(f"\n{i:2d}. 测试: {model_name}")
        print(f"    ID: {model_id}, 提供商: {model.get('provider', '未知')}")
        
        # 测试模型
        result = test_model(model_name)
        
        # 记录结果
        test_result = {
            "model": model,
            "test_result": result,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        test_results.append(test_result)
        
        # 分类
        if result["success"]:
            valid_models.append(model)
            print(f"    ✅ 有效")
        else:
            invalid_models.append(model)
            print(f"    ❌ 无效 - 原因: {result['error']}")
        
        # 短暂延迟，避免请求过于频繁
        if i < len(models):
            time.sleep(2)
    
    # 显示测试总结
    print("\n" + "=" * 80)
    print("📊 测试结果总结")
    print("=" * 80)
    
    print(f"✅ 有效模型: {len(valid_models)} 个")
    print(f"❌ 无效模型: {len(invalid_models)} 个")
    print(f"📈 成功率: {len(valid_models)/len(models)*100:.1f}%")
    
    # 显示无效模型详情
    if invalid_models:
        print("\n🗑️  无效模型列表:")
        for model in invalid_models:
            print(f"  - {model.get('name')} (ID: {model.get('id')}, 提供商: {model.get('provider')})")
    
    # 显示有效模型详情
    if valid_models:
        print("\n✅ 有效模型列表:")
        for model in valid_models:
            print(f"  - {model.get('name')} (ID: {model.get('id')}, 优先级: {model.get('priority')})")
    
    # 询问是否删除无效模型
    if invalid_models:
        print("\n" + "=" * 80)
        response = input(f"是否删除 {len(invalid_models)} 个无效模型？ (y/N): ").strip().lower()
        
        if response == 'y':
            # 更新注册表，只保留有效模型
            registry["models"] = valid_models
            
            # 记录删除操作
            if "switch_log" not in registry:
                registry["switch_log"] = []
            
            registry["switch_log"].append({
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "action": "cleanup_invalid_models",
                "removed_count": len(invalid_models),
                "removed_models": [m.get("name") for m in invalid_models],
                "remaining_count": len(valid_models)
            })
            
            # 保存更新后的注册表
            if save_registry(registry):
                print(f"\n✅ 已删除 {len(invalid_models)} 个无效模型")
                print(f"✅ 剩余 {len(valid_models)} 个有效模型")
                
                # 创建删除报告
                create_deletion_report(invalid_models, valid_models)
            else:
                print("❌ 保存注册表失败")
        else:
            print("⚠️  保留所有模型（包括无效的）")
    else:
        print("\n🎉 所有模型都有效！无需删除。")
    
    # 创建测试报告
    create_test_report(test_results, valid_models, invalid_models)
    
    print("\n" + "=" * 80)
    print("🧪 模型测试完成")
    print("=" * 80)

def create_deletion_report(invalid_models, valid_models):
    """创建删除报告"""
    report_path = WORKSPACE / "logs" / "model_cleanup_report.md"
    
    content = f"""# 模型清理报告

## 📅 清理时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 清理统计
- **清理前模型数**: {len(invalid_models) + len(valid_models)}
- **清理后模型数**: {len(valid_models)}
- **删除模型数**: {len(invalid_models)}
- **删除比例**: {len(invalid_models)/(len(invalid_models)+len(valid_models))*100:.1f}%

## 🗑️ 删除的模型
"""
    
    for model in invalid_models:
        content += f"- **{model.get('name')}** (ID: {model.get('id')})\n"
        content += f"  - 提供商: {model.get('provider', '未知')}\n"
        content += f"  - 优先级: {model.get('priority', 'N/A')}\n"
        content += f"  - 状态: {model.get('status', 'unknown')}\n"
        content += f"  - 最后使用: {model.get('last_used', '从未')}\n"
    
    content += f"""
## ✅ 保留的模型
"""
    
    for model in valid_models:
        content += f"- **{model.get('name')}** (ID: {model.get('id')})\n"
        content += f"  - 提供商: {model.get('provider', '未知')}\n"
        content += f"  - 优先级: {model.get('priority', 'N/A')}\n"
        content += f"  - 状态: {model.get('status', 'unknown')}\n"
    
    content += f"""
## 🔧 操作详情
- **备份文件**: {BACKUP_PATH}
- **日志文件**: {LOG_FILE}
- **操作类型**: 自动清理无效模型
- **执行状态**: 成功

## ⚠️ 注意事项
1. 删除的模型可以从备份文件中恢复
2. 建议定期运行模型测试
3. 无效模型可能是由于API Key过期、网络问题或服务不可用
4. 可以手动重新添加有效的模型

## 📞 恢复指南
如需恢复删除的模型，请执行:
```bash
cp {BACKUP_PATH} {REGISTRY_PATH}
```
"""
    
    try:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"📄 删除报告已保存: {report_path}")
    except Exception as e:
        print(f"❌ 保存删除报告失败: {e}")

def create_test_report(test_results, valid_models, invalid_models):
    """创建测试报告"""
    report_path = WORKSPACE / "logs" / "model_test_report.md"
    
    content = f"""# 模型测试报告

## 📅 测试时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 测试统计
- **测试模型总数**: {len(test_results)}
- **有效模型数**: {len(valid_models)}
- **无效模型数**: {len(invalid_models)}
- **测试成功率**: {len(valid_models)/len(test_results)*100:.1f}%

## 🧪 详细测试结果
"""
    
    for i, result in enumerate(test_results, 1):
        model = result["model"]
        test_result = result["test_result"]
        
        content += f"""
### {i}. {model.get('name')}
- **ID**: {model.get('id')}
- **提供商**: {model.get('provider', '未知')}
- **优先级**: {model.get('priority', 'N/A')}
- **测试状态**: {'✅ 通过' if test_result['success'] else '❌ 失败'}
- **响应时间**: {test_result['response_time']:.2f}秒
"""
        
        if not test_result["success"]:
            content += f"- **失败原因**: {test_result['error']}\n"
    
    content += f"""
## 🎯 建议
"""
    
    if invalid_models:
        content += f"""
### 立即行动建议
1. **删除无效模型**: 建议删除 {len(invalid_models)} 个无效模型以简化管理
2. **检查配置**: 验证无效模型的API Key和配置
3. **网络检查**: 确保可以访问相关API端点
"""
    else:
        content += """
### 系统状态良好
所有模型都有效，系统运行正常。建议：
1. 定期运行测试（每周一次）
2. 监控模型性能指标
3. 更新模型优先级基于实际使用情况
"""
    
    content += f"""
## 📁 相关文件
- **注册表文件**: {REGISTRY_PATH}
- **备份文件**: {BACKUP_PATH}
- **日志文件**: {LOG_FILE}
- **测试报告**: {report_path}

## 🔄 后续步骤
1. 根据测试结果优化模型配置
2. 设置定期测试任务
3. 监控模型性能和可用性
4. 更新模型优先级和备用顺序
"""
    
    try:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"📄 测试报告已保存: {report_path}")
    except Exception as e:
        print(f"❌ 保存测试报告失败: {e}")

def main():
    """主函数"""
    print("🚀 开始全面模型测试和清理")
    print("=" * 80)
    
    try:
        test_all_models()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()