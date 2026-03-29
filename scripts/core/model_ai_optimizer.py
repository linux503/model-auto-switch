#!/usr/bin/env python3
"""
AI 优化的智能切换算法 - 增强版
基于多维度评分和时间敏感切换
"""

import json
import time
import statistics
from datetime import datetime, time as dt_time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import math

# 配置
WORKSPACE = Path("/Users/a404/.openclaw/workspace")
REGISTRY_PATH = WORKSPACE / "models_registry.json"
PERFORMANCE_DB = WORKSPACE / "logs" / "model_performance.json"

class ModelAIOptimizer:
    """AI 优化的模型选择器"""
    
    def __init__(self):
        self.registry = self.load_registry()
        self.performance_data = self.load_performance_data()
        
    def load_registry(self) -> Dict:
        """加载模型注册表"""
        if not REGISTRY_PATH.exists():
            return {"models": []}
        
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def load_performance_data(self) -> Dict:
        """加载性能数据"""
        if not PERFORMANCE_DB.exists():
            return {"models": {}}
        
        with open(PERFORMANCE_DB, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def save_performance_data(self):
        """保存性能数据"""
        PERFORMANCE_DB.parent.mkdir(parents=True, exist_ok=True)
        with open(PERFORMANCE_DB, "w", encoding="utf-8") as f:
            json.dump(self.performance_data, f, indent=2, ensure_ascii=False)
    
    def get_current_time_context(self) -> Dict:
        """获取当前时间上下文"""
        now = datetime.now()
        hour = now.hour
        
        # 时间分段
        if 9 <= hour < 18:  # 工作时间
            return {
                "period": "work_hours",
                "priority": "performance",  # 优先性能
                "weight_response_time": 0.4,
                "weight_success_rate": 0.4,
                "weight_cost": 0.1,
                "weight_stability": 0.1
            }
        elif 18 <= hour < 23:  # 晚间高峰
            return {
                "period": "evening_peak",
                "priority": "balanced",  # 平衡性能与成本
                "weight_response_time": 0.3,
                "weight_success_rate": 0.3,
                "weight_cost": 0.2,
                "weight_stability": 0.2
            }
        else:  # 夜间非高峰
            return {
                "period": "off_peak",
                "priority": "cost_efficiency",  # 优先成本效率
                "weight_response_time": 0.2,
                "weight_success_rate": 0.3,
                "weight_cost": 0.4,
                "weight_stability": 0.1
            }
    
    def calculate_response_time_score(self, model_name: str, time_context: Dict) -> float:
        """计算响应时间评分"""
        model_data = self.performance_data.get("models", {}).get(model_name, {})
        
        if not model_data or "response_times" not in model_data:
            return 0.5  # 默认评分
        
        response_times = model_data["response_times"][-100:]  # 最近100次
        
        if not response_times:
            return 0.5
        
        # 计算百分位数
        try:
            p50 = statistics.median(response_times)
            p95 = sorted(response_times)[int(len(response_times) * 0.95)]
        except:
            return 0.5
        
        # 根据时间上下文调整评分标准
        if time_context["period"] == "work_hours":
            # 工作时间要求快速响应
            if p50 < 1000:  # < 1秒
                return 1.0
            elif p50 < 2000:  # < 2秒
                return 0.8
            elif p50 < 5000:  # < 5秒
                return 0.6
            else:
                return 0.3
        else:
            # 非工作时间可以接受较慢响应
            if p50 < 2000:  # < 2秒
                return 1.0
            elif p50 < 5000:  # < 5秒
                return 0.8
            elif p50 < 10000:  # < 10秒
                return 0.6
            else:
                return 0.4
    
    def calculate_success_rate_score(self, model_name: str) -> float:
        """计算成功率评分"""
        model_data = self.performance_data.get("models", {}).get(model_name, {})
        
        if not model_data:
            return 0.5
        
        total_requests = model_data.get("total_requests", 0)
        successful_requests = model_data.get("successful_requests", 0)
        
        if total_requests == 0:
            return 0.5
        
        success_rate = successful_requests / total_requests
        
        # 成功率评分
        if success_rate >= 0.99:  # 99%+
            return 1.0
        elif success_rate >= 0.95:  # 95-99%
            return 0.9
        elif success_rate >= 0.90:  # 90-95%
            return 0.7
        elif success_rate >= 0.80:  # 80-90%
            return 0.5
        else:  # < 80%
            return 0.2
    
    def calculate_cost_efficiency_score(self, model_name: str, time_context: Dict) -> float:
        """计算成本效率评分"""
        model_data = self.performance_data.get("models", {}).get(model_name, {})
        
        if not model_data:
            return 0.5
        
        # 模拟成本数据（实际应从配置或API获取）
        cost_per_token = model_data.get("cost_per_token", 0.001)
        avg_tokens_per_request = model_data.get("avg_tokens_per_request", 1000)
        
        avg_cost_per_request = cost_per_token * avg_tokens_per_request
        
        # 成本评分（成本越低评分越高）
        if avg_cost_per_request < 0.001:  # < $0.001
            return 1.0
        elif avg_cost_per_request < 0.005:  # < $0.005
            return 0.8
        elif avg_cost_per_request < 0.01:  # < $0.01
            return 0.6
        elif avg_cost_per_request < 0.02:  # < $0.02
            return 0.4
        else:  # >= $0.02
            return 0.2
    
    def calculate_stability_score(self, model_name: str) -> float:
        """计算稳定性评分"""
        model_data = self.performance_data.get("models", {}).get(model_name, {})
        
        if not model_data or "uptime_24h" not in model_data:
            return 0.5
        
        uptime = model_data["uptime_24h"]
        
        # 稳定性评分
        if uptime >= 0.999:  # 99.9%+
            return 1.0
        elif uptime >= 0.99:  # 99-99.9%
            return 0.9
        elif uptime >= 0.95:  # 95-99%
            return 0.7
        elif uptime >= 0.90:  # 90-95%
            return 0.5
        else:  # < 90%
            return 0.2
    
    def calculate_priority_adjustment(self, priority: int) -> float:
        """计算优先级调整"""
        # 优先级越低（数字越小）调整越高
        if priority == 1:
            return 0.2
        elif priority <= 3:
            return 0.1
        elif priority <= 5:
            return 0.05
        elif priority <= 10:
            return 0.02
        else:
            return 0.0
    
    def calculate_usage_pattern_score(self, model_name: str, hour: int) -> float:
        """计算使用模式评分（基于历史使用模式）"""
        model_data = self.performance_data.get("models", {}).get(model_name, {})
        
        if not model_data or "usage_by_hour" not in model_data:
            return 0.5
        
        usage_by_hour = model_data["usage_by_hour"]
        
        # 获取当前小时的典型使用量
        typical_usage = usage_by_hour.get(str(hour), 0)
        
        # 如果这个小时通常使用较多，说明模型在这个时间段表现良好
        if typical_usage > 10:
            return 0.9
        elif typical_usage > 5:
            return 0.7
        elif typical_usage > 0:
            return 0.6
        else:
            return 0.5
    
    def calculate_ai_score(self, model: Dict) -> Tuple[float, Dict]:
        """计算AI综合评分"""
        model_name = model["name"]
        priority = model.get("priority", 999)
        
        # 获取时间上下文
        time_context = self.get_current_time_context()
        current_hour = datetime.now().hour
        
        # 计算各项评分
        scores = {
            "response_time": self.calculate_response_time_score(model_name, time_context),
            "success_rate": self.calculate_success_rate_score(model_name),
            "cost_efficiency": self.calculate_cost_efficiency_score(model_name, time_context),
            "stability": self.calculate_stability_score(model_name),
            "priority_adjustment": self.calculate_priority_adjustment(priority),
            "usage_pattern": self.calculate_usage_pattern_score(model_name, current_hour)
        }
        
        # 应用时间敏感的权重
        weights = {
            "response_time": time_context["weight_response_time"],
            "success_rate": time_context["weight_success_rate"],
            "cost_efficiency": time_context["weight_cost"],
            "stability": time_context["weight_stability"],
            "priority_adjustment": 0.1,  # 固定权重
            "usage_pattern": 0.1  # 固定权重
        }
        
        # 计算加权总分
        total_score = 0
        for key in scores:
            total_score += scores[key] * weights[key]
        
        # 确保分数在0-1之间
        total_score = max(0, min(1, total_score))
        
        return total_score, {
            "scores": scores,
            "weights": weights,
            "time_context": time_context,
            "total_score": total_score
        }
    
    def predict_performance_trend(self, model_name: str) -> Dict:
        """预测性能趋势"""
        model_data = self.performance_data.get("models", {}).get(model_name, {})
        
        if not model_data or "response_times" not in model_data:
            return {"trend": "stable", "confidence": 0.5}
        
        response_times = model_data["response_times"][-50:]  # 最近50次
        
        if len(response_times) < 10:
            return {"trend": "stable", "confidence": 0.5}
        
        # 简单趋势分析
        first_half = statistics.mean(response_times[:len(response_times)//2])
        second_half = statistics.mean(response_times[len(response_times)//2:])
        
        trend_ratio = second_half / first_half if first_half > 0 else 1
        
        if trend_ratio > 1.5:  # 性能下降超过50%
            return {"trend": "degrading", "confidence": 0.8, "ratio": trend_ratio}
        elif trend_ratio > 1.2:  # 性能下降20-50%
            return {"trend": "slightly_degrading", "confidence": 0.7, "ratio": trend_ratio}
        elif trend_ratio < 0.8:  # 性能提升超过20%
            return {"trend": "improving", "confidence": 0.7, "ratio": trend_ratio}
        else:
            return {"trend": "stable", "confidence": 0.6, "ratio": trend_ratio}
    
    def select_best_model(self) -> Tuple[Optional[Dict], Dict]:
        """选择最佳模型"""
        models = self.registry.get("models", [])
        
        if not models:
            return None, {"error": "没有可用的模型"}
        
        scored_models = []
        
        for model in models:
            if model.get("status") != "active":
                continue
            
            score, details = self.calculate_ai_score(model)
            trend = self.predict_performance_trend(model["name"])
            
            scored_models.append({
                "model": model,
                "score": score,
                "details": details,
                "trend": trend
            })
        
        if not scored_models:
            return None, {"error": "没有活跃的模型"}
        
        # 按评分排序
        scored_models.sort(key=lambda x: x["score"], reverse=True)
        
        best_model = scored_models[0]
        
        # 生成选择理由
        reason = self.generate_selection_reason(best_model, scored_models)
        
        return best_model["model"], {
            "selected_model": best_model["model"]["name"],
            "score": best_model["score"],
            "details": best_model["details"],
            "trend": best_model["trend"],
            "reason": reason,
            "all_scores": [
                {
                    "model": m["model"]["name"],
                    "score": m["score"],
                    "priority": m["model"].get("priority", 999)
                }
                for m in scored_models
            ]
        }
    
    def generate_selection_reason(self, best_model: Dict, all_models: List) -> str:
        """生成选择理由"""
        model_name = best_model["model"]["name"]
        score = best_model["score"]
        details = best_model["details"]
        trend = best_model["trend"]
        
        time_context = details["time_context"]
        scores = details["scores"]
        
        # 构建理由
        reasons = []
        
        # 时间相关理由
        if time_context["period"] == "work_hours":
            reasons.append("当前是工作时间，优先选择性能最佳的模型")
        elif time_context["period"] == "evening_peak":
            reasons.append("当前是晚间高峰时段，平衡性能与成本")
        else:
            reasons.append("当前是非高峰时段，优先考虑成本效率")
        
        # 性能相关理由
        if scores["response_time"] > 0.8:
            reasons.append("响应时间表现优秀")
        if scores["success_rate"] > 0.9:
            reasons.append("成功率高达{:.1f}%".format(scores["success_rate"] * 100))
        if scores["cost_efficiency"] > 0.8:
            reasons.append("成本效率高")
        
        # 趋势相关理由
        if trend["trend"] == "improving":
            reasons.append("性能正在提升中")
        elif trend["trend"] == "degrading":
            reasons.append("注意：性能有下降趋势，但当前仍是最佳选择")
        
        # 优先级理由
        if best_model["model"].get("priority", 999) <= 3:
            reasons.append("配置优先级高")
        
        return "；".join(reasons)
    
    def record_performance(self, model_name: str, response_time: float, success: bool):
        """记录性能数据"""
        if "models" not in self.performance_data:
            self.performance_data["models"] = {}
        
        if model_name not in self.performance_data["models"]:
            self.performance_data["models"][model_name] = {
                "response_times": [],
                "total_requests": 0,
                "successful_requests": 0,
                "usage_by_hour": {}
            }
        
        model_data = self.performance_data["models"][model_name]
        
        # 记录响应时间
        model_data.setdefault("response_times", []).append(response_time)
        if len(model_data["response_times"]) > 1000:  # 保留最近1000次
            model_data["response_times"] = model_data["response_times"][-1000:]
        
        # 记录请求统计
        model_data["total_requests"] = model_data.get("total_requests", 0) + 1
        if success:
            model_data["successful_requests"] = model_data.get("successful_requests", 0) + 1
        
        # 记录按小时使用
        current_hour = datetime.now().hour
        hour_key = str(current_hour)
        model_data.setdefault("usage_by_hour", {})
        model_data["usage_by_hour"][hour_key] = model_data["usage_by_hour"].get(hour_key, 0) + 1
        
        # 计算24小时可用性
        if model_data["total_requests"] > 0:
            success_rate = model_data["successful_requests"] / model_data["total_requests"]
            model_data["uptime_24h"] = success_rate
        
        self.save_performance_data()

def main():
    """主函数"""
    print("🧠 AI 优化的智能切换算法")
    print("=" * 80)
    
    optimizer = ModelAIOptimizer()
    
    # 选择最佳模型
    best_model, selection_info = optimizer.select_best_model()
    
    if not best_model:
        print("❌ 没有找到合适的模型")
        return
    
    print(f"🎯 最佳模型: {best_model['name']}")
    print(f"📊 综合评分: {selection_info['score']:.3f}")
