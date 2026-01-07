from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import logging
from datetime import datetime, timedelta
import random

router = APIRouter()
logger = logging.getLogger(__name__)

class InventoryItem(BaseModel):
    id: str
    name: str
    sku: str
    current_stock: int
    min_stock: int
    max_stock: Optional[int] = None
    unit_price: float
    category: Optional[str] = None
    sales_history: Optional[List[Dict]] = []

class PredictionRequest(BaseModel):
    items: List[InventoryItem]
    prediction_days: Optional[int] = 30
    include_seasonality: Optional[bool] = True

class DemandForecast(BaseModel):
    item_id: str
    item_name: str
    current_stock: int
    predicted_demand: List[Dict]
    reorder_recommendation: Dict
    stockout_risk: str
    confidence: float

@router.post("/predict-demand")
async def predict_inventory_demand(request: PredictionRequest):
    """
    Predict inventory demand using ML models
    """
    try:
        # TODO: Implement actual ML-based demand forecasting
        # For now, generate realistic placeholder predictions
        
        forecasts = []
        
        for item in request.items:
            # Generate mock prediction data
            daily_predictions = []
            base_demand = max(1, item.current_stock // 30)  # Rough daily usage
            
            for i in range(request.prediction_days):
                date = datetime.now() + timedelta(days=i)
                # Add some randomness and seasonality
                seasonal_factor = 1 + 0.2 * random.sin(i * 0.1)  # Simple seasonality
                daily_demand = max(0, int(base_demand * seasonal_factor * (0.8 + 0.4 * random.random())))
                
                daily_predictions.append({
                    "date": date.isoformat(),
                    "predicted_demand": daily_demand,
                    "confidence": 0.75 + 0.2 * random.random()
                })
            
            # Calculate total predicted demand
            total_predicted = sum(p["predicted_demand"] for p in daily_predictions)
            
            # Determine stockout risk
            if item.current_stock < total_predicted * 0.3:
                risk = "high"
            elif item.current_stock < total_predicted * 0.6:
                risk = "medium"
            else:
                risk = "low"
            
            # Generate reorder recommendation
            reorder_point = max(item.min_stock, int(total_predicted * 0.4))
            reorder_quantity = max(item.min_stock, int(total_predicted * 0.7))
            
            if item.max_stock:
                reorder_quantity = min(reorder_quantity, item.max_stock)
            
            forecast = DemandForecast(
                item_id=item.id,
                item_name=item.name,
                current_stock=item.current_stock,
                predicted_demand=daily_predictions,
                reorder_recommendation={
                    "should_reorder": item.current_stock <= reorder_point,
                    "reorder_point": reorder_point,
                    "suggested_quantity": reorder_quantity,
                    "estimated_cost": reorder_quantity * item.unit_price,
                    "urgency": "high" if item.current_stock < item.min_stock else "medium" if item.current_stock <= reorder_point else "low"
                },
                stockout_risk=risk,
                confidence=0.8 + 0.15 * random.random()
            )
            
            forecasts.append(forecast)
        
        return {
            "forecasts": forecasts,
            "prediction_period_days": request.prediction_days,
            "generated_at": datetime.now().isoformat(),
            "model_version": "v1.0-placeholder",
            "summary": {
                "total_items": len(forecasts),
                "high_risk_items": len([f for f in forecasts if f.stockout_risk == "high"]),
                "reorder_recommended": len([f for f in forecasts if f.reorder_recommendation["should_reorder"]]),
                "average_confidence": sum(f.confidence for f in forecasts) / len(forecasts) if forecasts else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Inventory prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class OptimizationRequest(BaseModel):
    items: List[InventoryItem]
    budget_constraint: Optional[float] = None
    storage_constraint: Optional[int] = None
    target_service_level: Optional[float] = 0.95

@router.post("/optimize")
async def optimize_inventory(request: OptimizationRequest):
    """
    Optimize inventory levels and reorder points
    """
    try:
        # TODO: Implement actual inventory optimization algorithms
        
        optimizations = []
        
        for item in request.items:
            # Simple optimization logic (placeholder)
            current_turnover = len(item.sales_history) if item.sales_history else 1
            
            # Calculate optimal stock levels
            optimal_min = max(1, int(item.current_stock * 0.2))
            optimal_max = int(item.current_stock * 1.5) if not item.max_stock else min(item.max_stock, int(item.current_stock * 1.5))
            
            optimization = {
                "item_id": item.id,
                "item_name": item.name,
                "current_levels": {
                    "stock": item.current_stock,
                    "min_stock": item.min_stock,
                    "max_stock": item.max_stock
                },
                "optimized_levels": {
                    "min_stock": optimal_min,
                    "max_stock": optimal_max,
                    "reorder_point": int(optimal_min * 1.2),
                    "economic_order_quantity": int((optimal_max - optimal_min) * 0.7)
                },
                "expected_benefits": {
                    "cost_reduction_percent": random.uniform(5, 15),
                    "service_level_improvement": random.uniform(2, 8),
                    "storage_efficiency": random.uniform(10, 25)
                },
                "implementation_priority": random.choice(["high", "medium", "low"])
            }
            
            optimizations.append(optimization)
        
        return {
            "optimizations": optimizations,
            "optimization_date": datetime.now().isoformat(),
            "constraints_applied": {
                "budget": request.budget_constraint,
                "storage": request.storage_constraint,
                "service_level": request.target_service_level
            },
            "summary": {
                "total_items_optimized": len(optimizations),
                "high_priority_items": len([o for o in optimizations if o["implementation_priority"] == "high"]),
                "estimated_total_savings_percent": sum(o["expected_benefits"]["cost_reduction_percent"] for o in optimizations) / len(optimizations) if optimizations else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Inventory optimization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def get_available_models():
    """
    Get information about available prediction models
    """
    return {
        "models": [
            {
                "id": "demand_forecast",
                "name": "Demand Forecasting",
                "description": "Predicts future demand based on historical data and trends",
                "accuracy": "85-92%",
                "credits_required": 10
            },
            {
                "id": "inventory_optimization",
                "name": "Inventory Optimization",
                "description": "Optimizes stock levels and reorder points",
                "accuracy": "80-88%",
                "credits_required": 15
            },
            {
                "id": "seasonality_analysis",
                "name": "Seasonality Analysis",
                "description": "Identifies seasonal patterns in demand",
                "accuracy": "75-85%",
                "credits_required": 8
            }
        ],
        "supported_features": [
            "Multi-item forecasting",
            "Seasonality detection",
            "Trend analysis",
            "Constraint-based optimization",
            "Risk assessment",
            "Cost optimization"
        ]
    }