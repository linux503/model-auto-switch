#!/usr/bin/env python3
"""
OpenClaw 模型预测性维护模块
功能：
1. 基于历史数据预测模型故障
2. 成本优化分析
3. 时间敏感切换策略
4. 性能趋势分析
"""

import json
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
from collections import defaultdict

WORKSPACE = Path("/Users/a404/.openclaw/workspace")
REGISTRY_FILE = WORKSPACE / "models_registry.json"

def load_registry() -> Dict:
    """加载模型注册表"""
    if REGISTRY_FILE.exists():
        with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"models": [], "performance_stats": {}, "switch_log": [], "settings": {}}

class PredictiveMaintenance:
    """预测性维护分析器"""
    
    def __init__(self):
        self.registry = load_registry()
        self.settings = self.registry.get("settings", {})
    
    def analyze_failure_patterns(self, model_name: str) -> Dict:
        """分析模型故障模式"""
        stats = self.registry.get("performance_stats", {}).get(model_name, {})
        
        if not stats or stats.get("total_tests", 0) < 10:
            return {"confidence": 0, "patterns": []}
        
        # 计算故障率趋势
        failure_rate = stats.get("failed_tests", 0) / stats.get("total_tests", 1)
        
        # 分析响应时间趋势
        response_times = stats.get("response_times", [])
        if len(response_times) >= 5:
            recent_avg = statistics.mean(response_times[-5:])
            overall_avg = statistics.mean(response_times)
            trend = "increasing" if recent_avg > overall_avg * 1.2 else "stable"
        else:
            trend = "unknown"
        
        # 计算故障预测置信度
        confidence = self._calculate_failure_confidence(stats)
        
        return {
            "model": model_name,
            "failure_rate": failure_rate,
            "response_time_trend": trend,
            "predicted_failure_risk": confidence,
            "recommendation": self._get_recommendation(failure_rate, confidence),
            "last_analysis": datetime.utcnow().isoformat() + "Z"
        }
    
    def _calculate_failure_confidence(self, stats: Dict) -> float:
        """计算故障预测置信度"""
        confidence = 0.0
        
        # 基于失败次数
        total_tests = stats.get("total_tests", 0)
        failed_tests = stats.get("failed_tests", 0)
        
        if total_tests > 0:
            failure_rate = failed_tests / total_tests
            confidence += failure_rate * 0.4
        
        # 基于响应时间稳定性
        response_times = stats.get("response_times", [])
        if len(response_times) >= 3:
            cv = statistics.stdev(response_times) / statistics.mean(response_times) if statistics.mean(response_times) > 0 else 0
            stability_score = min(cv, 1.0)  # 变异系数越大越不稳定
            confidence += stability_score * 0.3
        
        # 基于最近表现
        recent_failures = min(failed_tests, 5)  # 考虑最近5次失败
        if recent_failures > 0:
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    def _get_recommendation(self, failure_rate: float, confidence: float) -> str:
        """根据分析结果给出建议"""
        if confidence > 0.8:
            return "立即切换 - 高故障风险"
        elif confidence > 0.6:
            return "准备切换 - 中等故障风险"
        elif confidence > 0.4:
            return "监控观察 - 低故障风险"
        else:
            return "正常使用 - 风险较低"
    
    def analyze_cost_optimization(self) -> List[Dict]:
        """成本优化分析"""
        models = self.registry.get("models", [])
        results = []
        
        # 模拟成本数据（实际应该从配置或API获取）
        cost_data = {
            "deepseek/deepseek-chat": {"cost_per_1k_tokens": 0.001, "reliability": 0.95},
            "aicodee/MiniMax-M2.5-highspeed": {"cost_per_1k_tokens": 0.002, "reliability": 0.93},
            "openai_betterclaude/gpt-5.4": {"cost_per_1k_tokens": 0.005, "reliability": 0.97},
        }
        
        for model in models:
            if model["status"] != "active":
                continue
            
            model_name = model["name"]
            stats = self.registry.get("performance_stats", {}).get(model_name, {})
            
            # 获取成本数据
            cost_info = cost_data.get(model_name, {"cost_per_1k_tokens": 0.003, "reliability": 0.9})
            
            # 计算性价比分数
            cost_score = 1.0 / (cost_info["cost_per_1k_tokens"] * 1000) if cost_info["cost_per_1k_tokens"] > 0 else 0
            reliability = stats.get("success_rate", 0.8) if stats else cost_info["reliability"]
            
            # 综合评分
            value_score = (cost_score * 0.6) + (reliability * 0.4)
            
            results.append({
                "model": model_name,
                "estimated_cost_per_1k": cost_info["cost_per_1k_tokens"],
                "reliability": reliability,
                "value_score": value_score,
                "recommendation": "高性价比" if value_score > 0.7 else "中等性价比" if value_score > 0.5 else "低性价比"
            })
        
        # 按性价比排序
        results.sort(key=lambda x: x["value_score"], reverse=True)
        return results
    
    def time_sensitive_analysis(self) -> Dict:
        """时间敏感分析"""
        now = datetime.now()
        hour = now.hour
        
        # 定义时间段的模型偏好
        time_preferences = {
            "night": (0, 6, ["deepseek/deepseek-chat"], "夜间稳定优先"),
            "morning": (6, 12, ["aicodee/MiniMax-M2.5-highspeed", "deepseek/deepseek-chat"], "上午性能优先"),
            "afternoon": (12, 18, ["openai_betterclaude/gpt-5.4", "aicodee/MiniMax-M2.5-highspeed"], "下午质量优先"),
            "evening": (18, 24, ["deepseek/deepseek-chat", "aicodee/MiniMax-M2.7-highspeed"], "晚间平衡优先")
        }
        
        # 确定当前时间段
        current_period = None
        recommended_models = []
        reason = ""
        
        for period, (start, end, models, period_reason) in time_preferences.items():
            if start <= hour < end:
                current_period = period
                recommended_models = models
                reason = period_reason
                break
        
        return {
            "current_time": now.strftime("%H:%M"),
            "current_period": current_period,
            "recommended_models": recommended_models,
            "reason": reason,
            "analysis": self._get_time_analysis(current_period)
        }
    
    def _get_time_analysis(self, period: str) -> str:
        """获取时间段分析"""
        analyses = {
            "night": "夜间网络稳定，建议使用稳定可靠的模型",
            "morning": "上午用户活跃，建议使用响应快的模型",
            "afternoon": "下午工作需求高，建议使用质量好的模型",
            "evening": "晚间使用平衡，建议使用性价比高的模型"
        }
        return analyses.get(period, "根据历史数据自动选择最佳模型")
    
    def generate_performance_report(self) -> Dict:
        """生成性能报告"""
        stats = self.registry.get("performance_stats", {})
        
        if not stats:
            return {"error": "没有足够的性能数据"}
        
        report = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "summary": {},
            "top_performers": [],
            "needs_attention": [],
            "recommendations": []
        }
        
        # 总体统计
        total_tests = sum(s.get("total_tests", 0) for s in stats.values())
        total_failures = sum(s.get("failed_tests", 0) for s in stats.values())
        avg_success_rate = statistics.mean([s.get("success_rate", 0) for s in stats.values() if s.get("total_tests", 0) > 0]) if any(s.get("total_tests", 0) > 0 for s in stats.values()) else 0
        
        report["summary"] = {
            "total_models": len(stats),
            "total_tests": total_tests,
            "total_failures": total_failures,
            "overall_success_rate": avg_success_rate,
            "analysis_period": "all_time"
        }
        
        # 最佳表现者
        scored_models = []
        for model_name, model_stats in stats.items():
            if model_stats.get("total_tests", 0) >= 5:
                score = (model_stats.get("success_rate", 0) * 0.6) + (1.0 / (model_stats.get("avg_response_time", 1000) / 1000) * 0.4)
                scored_models.append((model_name, score, model_stats))
        
        scored_models.sort(key=lambda x: x[1], reverse=True)
        
        for model_name, score, model_stats in scored_models[:3]:
            report["top_performers"].append({
                "model": model_name,
                "score": round(score, 3),
                "success_rate": model_stats.get("success_rate", 0),
                "avg_response_time": model_stats.get("avg_response_time", 0),
                "total_tests": model_stats.get("total_tests", 0)
            })
        
        # 需要关注的模型
        for model_name, model_stats in stats.items():
            if model_stats.get("total_tests", 0) >= 3:
                failure_rate = model_stats.get("failed_tests", 0) / model_stats.get("total_tests", 1)
                if failure_rate > 0.3 or model_stats.get("avg_response_time", 0) > 5000:
                    report["needs_attention"].append({
                        "model": model_name,
                        "failure_rate": failure_rate,
                        "avg_response_time": model_stats.get("avg_response_time", 0),
                        "issue": "高故障率" if failure_rate > 0.3 else "高延迟"
                    })
        
        # 生成建议
        if report["needs_attention"]:
            report["recommendations"].append("建议检查并可能禁用高故障率模型")
        
        if len(report["top_performers"]) > 0:
            best_model = report["top_performers"][0]
            report["recommendations"].append(f"建议优先使用 {best_model['model']} (评分: {best_model['score']:.3f})")
        
        if avg_success_rate < 0.8:
            report["recommendations"].append("整体成功率较低，建议优化模型配置")
        
        return report
    
    def predict_optimal_model(self, context: Dict = None) -> Dict:
        """预测最佳模型（考虑多种因素）"""
        if context is None:
            context = {}
        
        models = self.registry.get("models", [])
        active_models = [m for m in models if m.get("status") == "active"]
        
        if not active_models:
            return {"error": "没有活跃模型"}
        
        # 获取当前时间
        now = datetime.now()
        
        # 计算每个模型的综合评分
        scored_models = []
        for model in active_models:
            model_name = model["name"]
            stats = self.registry.get("performance_stats", {}).get(model_name, {})
            
            # 基础评分
            base_score = 0.5
            
            # 性能因素
            if stats:
                success_rate = stats.get("success_rate", 0.5)
                avg_response = stats.get("avg_response_time", 3000)
                response_score = 1.0 / (avg_response / 1000) if avg_response > 0 else 0
                base_score = (success_rate * 0.6) + (response_score * 0.4)
            
            # 优先级因素
            priority = model.get("priority", 10)
            priority_factor = 1.0 / (priority * 0.1)
            base_score *= (0.7 + 0.3 * priority_factor)
            
            # 时间因素（如果是工作时间，偏好高质量模型）
            if 9 <= now.hour < 18:  # 工作时间
                if "gpt" in model_name.lower() or "claude" in model_name.lower():
                    base_score *= 1.1
            
            # 成本因素（如果指定了成本敏感）
            if context.get("cost_sensitive", False):
                # 简单成本估算
                if "mini" in model_name.lower() or "chat" in model_name.lower():
                    base_score *= 1.05  # 便宜模型加分
            
            scored_models.append({
                "model": model_name,
                "score": base_score,
                "priority": priority,
                "success_rate": stats.get("success_rate", 0) if stats else 0,
                "response_time": stats.get("avg_response_time", 0) if stats else 0
            })
        
        # 选择最佳模型
        scored_models.sort(key=lambda x: x["score"], reverse=True)
        best_model = scored_models[0]
        
        return {
            "recommended_model": best_model["model"],
            "score": best_model["score"],
            "confidence": min(best_model["score"] * 1.5, 1.0),
            "alternatives": [m["model"] for m in scored_models[1:4]],
            "analysis_time": now.isoformat(),
            "factors_considered": ["performance", "priority", "time_of_day", "cost"]
        }

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python3 model_predictive_maintenance.py <命令>")
        print("命令:")
        print("  analyze <model>     分析指定模型的故障模式")
        print("  cost                成本优化分析")
        print("  time                时间敏感分析")
        print("  report              生成性能报告")
        print("  predict             预测最佳模型")
        print("  all                 运行所有分析")
        return
    
    command = sys.argv[1]
    analyzer = PredictiveMaintenance()
    
    if command == "analyze":
        if len(sys.argv) > 2:
            model_name = sys.argv[2]
            result = analyzer.analyze_failure_patterns(model_name)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("错误: 请指定模型名称")
    
    elif command == "cost":
        results = analyzer.analyze_cost_optimization()
        print("成本优化分析:")
        print("=" * 80)
        for result in results:
            print(f"模型: {result['model']}")
            print(f"  预估成本: ${result['estimated_cost_per_1k']:.4f}/1K tokens")
            print(f"  可靠性: {result['reliability']:.1%}")
            print(f"  性价比评分: {result['value_score']:.3f}")
            print(f"  建议: {result['recommendation']}")
            print()
    
    elif command == "time":
        result = analyzer.time_sensitive_analysis()
        print("时间敏感分析:")
        print("=" * 80)
        print(f"当前时间: {result['current_time']}")
        print(f"时间段: {result['current_period']}")
        print(f"分析: {result['analysis']}")
        print(f"推荐模型: {', '.join(result['recommended_models'])}")
        print(f"理由: {result['reason']}")
    
    elif command == "report":
        report = analyzer.generate_performance_report()
        print("性能分析报告:")
        print("=" * 80)
        print(f"生成时间: {report['generated_at']}")
        print()
        
        print("📊 总体统计:")
        summary = report['summary']
        print(f"  模型数量: {summary['total_models']}")
        print(f"  总测试次数: {summary['total_tests']}")
        print(f"  总失败次数: {summary['total_failures']}")
        print(f"  整体成功率: {summary['overall_success_rate']:.1%}")
        print()
        
        if report['top_performers']:
            print("🏆 最佳表现者:")
            for i, model in enumerate(report['top_performers'], 1):
                print(f"  {i}. {model['model']}")
                print(f"     评分: {model['score']:.3f}, 成功率: {model['success_rate']:.1%}, 响应: {model['avg_response_time']:.0f}ms")
            print()
        
        if report['needs_attention']:
            print("⚠️  需要关注:")
            for model in report['needs_attention']:
                print(f"  • {model['model']}: {model['issue']} (故障率: {model['failure_rate']:.1%}, 响应: {model['avg_response_time']:.0f}ms)")
            print()
        
        if report['recommendations']:
            print("💡 建议:")
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"  {i}. {rec}")
    
    elif command == "predict":
        context = {}
        if len(sys.argv) > 2 and sys.argv[2] == "--cost-sensitive":
            context["cost_sensitive"] = True
        
        result = analyzer.predict_optimal_model(context)
        print("最佳模型预测:")
        print("=" * 80)
        print(f"推荐模型: {result['recommended_model']}")
        print(f"预测评分: {result['score']:.3f}")
        print(f"置信度: {result['confidence']:.1%}")
        print(f"分析时间: {result['analysis_time']}")
        print(f"考虑因素: {', '.join(result['factors_considered'])}")
        
        if result.get('alternatives'):
            print(f"备选模型: {', '.join(result['alternatives'])}")
    
    elif command == "all":
        print("运行所有分析...")
        print()
        
        # 时间分析
        time_result = analyzer.time_sensitive_analysis()
        print("⏰ 时间敏感分析:")
        print(f"  当前: {time_result['current_time']} ({time_result['current_period']})")
        print(f"  推荐: {', '.join(time_result['recommended_models'])}")
        print()
        
        # 成本分析
        cost_results = analyzer.analyze_cost_optimization()
        if cost_results:
            print("💰 成本优化分析:")
            best_cost = cost_results[0]
            print(f"  最具性价比: {best_cost['model']} (评分: {best_cost['value_score']:.3f})")
            print()
        
        # 性能报告
        report = analyzer.generate_performance_report()
        print("📊 性能概况:")
        print(f"  整体成功率: {report['summary']['overall_success_rate']:.1%}")
        print(f"  总测试: {report['summary']['total_tests']}")
        
        if report['top_performers']:
            print(f"  最佳模型: {report['top_performers'][0]['model']}")
        
        if report['needs_attention']:
            print(f"  需关注: {len(report['needs_attention'])} 个模型")
        print()
        
        # 预测最佳模型
        prediction = analyzer.predict_optimal_model()
        print("🎯 综合推荐:")
        print(f"  最佳选择: {prediction['recommended_model']}")
        print(f"  预测评分: {prediction['score']:.3f}")
    
    else:
        print(f"错误: 未知命令 '{command}'")

if __name__ == "__main__":
    main()