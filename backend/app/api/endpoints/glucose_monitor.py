from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.api.deps import get_current_user, get_db
from app.db.models import User
from app.services.glucose_monitor import glucose_monitor_service
from app.core.scheduler import glucose_scheduler
from app.services.glucose import get_user_glucose_records
from app.ml.ollama_service import ollama_service
import logging

router = APIRouter()

logger = logging.getLogger(__name__)

# 请求和响应模型
class DeviceDataRequest(BaseModel):
    device_type: str
    params: Optional[Dict[str, Any]] = None
    
class GlucoseDataResponse(BaseModel):
    timestamp: str
    value: float
    unit: str
    
class AnalysisRequest(BaseModel):
    hours: int = 24
    
class AlertResponse(BaseModel):
    type: str
    value: float
    threshold: float
    timestamp: Optional[str] = None
    from_time: Optional[str] = None
    to_time: Optional[str] = None
    from_value: Optional[float] = None
    to_value: Optional[float] = None
    severity: str
    
class AnalysisResponse(BaseModel):
    status: str
    statistics: Optional[Dict[str, Any]] = None
    alerts: Optional[List[AlertResponse]] = None
    has_alerts: bool = False
    message: Optional[str] = None
    alert_message: Optional[str] = None

class DeviceRegistrationRequest(BaseModel):
    device_type: str
    params: Optional[Dict[str, Any]] = None
    enable_auto_sync: bool = True

# 新增：直接导入血糖数据的请求模型
class GlucoseImportRequest(BaseModel):
    device_id: str
    data: List[Dict[str, Any]]

class GlucoseAnalysisRequest(BaseModel):
    hours: int = 24

class GlucoseTrendAnalysisRequest(BaseModel):
    days: Optional[int] = 3

# API端点
@router.post("/device-data", response_model=List[GlucoseDataResponse])
async def get_device_data(
    request: DeviceDataRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    从设备获取血糖数据
    """
    try:
        data = await glucose_monitor_service.get_device_data(
            device_type=request.device_type,
            user_id=current_user.id,
            params=request.params
        )
        return data
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取设备数据失败: {str(e)}"
        )

@router.post("/import-device-data")
async def import_device_data(
    request: DeviceDataRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    从设备导入血糖数据并保存到数据库
    """
    try:
        # 获取设备数据
        data = await glucose_monitor_service.get_device_data(
            device_type=request.device_type,
            user_id=current_user.id,
            params=request.params
        )
        
        # 保存到数据库
        saved_records = await glucose_monitor_service.save_glucose_data(
            db=db,
            user_id=current_user.id,
            glucose_data=data
        )
        
        # 在后台进行数据分析
        background_tasks.add_task(
            analyze_and_alert,
            db=db,
            user_id=current_user.id,
            user_name=current_user.name
        )
        
        return {
            "status": "success",
            "message": f"成功导入{len(saved_records)}条血糖记录",
            "imported_count": len(saved_records)
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导入设备数据失败: {str(e)}"
        )

@router.post("/devices/import")
async def import_glucose_data(
    request: GlucoseImportRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    直接导入血糖数据并保存到数据库
    """
    try:
        # 格式化数据为服务需要的格式
        glucose_data = []
        for item in request.data:
            # 确保数据格式正确
            if "value" not in item or "measured_at" not in item or "measurement_time" not in item:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="数据格式错误，必须包含value、measured_at和measurement_time字段"
                )
                
            glucose_data.append({
                "timestamp": item["measured_at"],
                "value": item["value"],
                "unit": "mmol/L",
                "measurement_time": item["measurement_time"]
            })
        
        # 保存到数据库
        saved_records = await glucose_monitor_service.save_glucose_data(
            db=db,
            user_id=current_user.id,
            glucose_data=glucose_data
        )
        
        # 在后台进行数据分析
        background_tasks.add_task(
            analyze_and_alert,
            db=db,
            user_id=current_user.id,
            user_name=current_user.name
        )
        
        return {
            "status": "success",
            "message": f"成功导入{len(saved_records)}条血糖记录",
            "imported_count": len(saved_records)
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导入血糖数据失败: {str(e)}"
        )

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_glucose(
    request: GlucoseAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    分析最近一段时间的血糖数据并检查异常
    """
    try:
        # 获取指定时间范围内的血糖记录
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=request.hours)
        
        records = get_user_glucose_records(
            db=db,
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )
        
        if not records:
            return {
                "status": "ok",
                "message": f"近{request.hours}小时内没有血糖记录",
                "has_alerts": False
            }
        
        # 计算统计数据
        values = [record.value for record in records]
        avg_value = sum(values) / len(values)
        max_value = max(values)
        min_value = min(values)
        
        # 检查是否有异常
        alerts = []
        
        # 检查低血糖
        low_threshold = 3.9
        if min_value < low_threshold:
            low_records = [r for r in records if r.value < low_threshold]
            for record in low_records:
                severity = "high" if record.value < 2.9 else "medium"
                alerts.append({
                    "type": "low_glucose",
                    "value": record.value,
                    "threshold": low_threshold,
                    "timestamp": record.measured_at.isoformat(),
                    "severity": severity
                })
        
        # 检查高血糖
        high_threshold = 10.0
        if max_value > high_threshold:
            high_records = [r for r in records if r.value > high_threshold]
            for record in high_records:
                severity = "high" if record.value > 12.0 else "medium"
                alerts.append({
                    "type": "high_glucose",
                    "value": record.value,
                    "threshold": high_threshold,
                    "timestamp": record.measured_at.isoformat(),
                    "severity": severity
                })
        
        # 检查血糖快速上升和下降
        if len(records) >= 2:
            # 按时间排序
            sorted_records = sorted(records, key=lambda r: r.measured_at)
            
            for i in range(1, len(sorted_records)):
                prev_record = sorted_records[i-1]
                curr_record = sorted_records[i]
                
                # 计算时间差（小时）
                time_diff = (curr_record.measured_at - prev_record.measured_at).total_seconds() / 3600
                
                # 如果时间差在6小时内
                if 0 < time_diff <= 6:
                    # 计算变化率（mmol/L/小时）
                    rate = (curr_record.value - prev_record.value) / time_diff
                    
                    # 检查快速下降
                    if rate < -2.0:
                        alerts.append({
                            "type": "rapid_drop",
                            "value": abs(rate),
                            "from_value": prev_record.value,
                            "to_value": curr_record.value,
                            "time_diff": time_diff,
                            "timestamp": curr_record.measured_at.isoformat(),
                            "severity": "high" if rate < -3.0 else "medium"
                        })
                    
                    # 检查快速上升
                    elif rate > 2.5:
                        alerts.append({
                            "type": "rapid_rise",
                            "value": rate,
                            "from_value": prev_record.value,
                            "to_value": curr_record.value,
                            "time_diff": time_diff,
                            "timestamp": curr_record.measured_at.isoformat(),
                            "severity": "high" if rate > 4.0 else "medium"
                        })
        
        # 生成警报消息
        alert_message = None
        if alerts:
            try:
                # 使用Ollama生成警报消息
                alert_message = await generate_alert_message(current_user, alerts, records)
            except Exception as e:
                logger.error(f"生成警报消息失败: {str(e)}")
                # 如果生成失败，使用默认消息
                if any(a["type"] == "low_glucose" for a in alerts):
                    alert_message = f"检测到低血糖情况，最低值为 {min_value} mmol/L，请及时处理。"
                elif any(a["type"] == "high_glucose" for a in alerts):
                    alert_message = f"检测到高血糖情况，最高值为 {max_value} mmol/L，请注意控制饮食和用药。"
                elif any(a["type"] == "rapid_drop" for a in alerts):
                    alert_message = "检测到血糖快速下降，请密切关注血糖变化。"
                elif any(a["type"] == "rapid_rise" for a in alerts):
                    alert_message = "检测到血糖快速上升，请检查饮食情况并考虑适当运动。"
        
        return {
            "status": "ok",
            "statistics": {
                "average": avg_value,
                "max": max_value,
                "min": min_value,
                "count": len(records),
                "period_hours": request.hours
            },
            "alerts": alerts,
            "has_alerts": len(alerts) > 0,
            "alert_message": alert_message
        }
    
    except Exception as e:
        logger.error(f"分析血糖数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析血糖数据失败: {str(e)}")

@router.post("/analyze-trend")
async def analyze_glucose_trend(
    request: GlucoseTrendAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    分析用户近三天的血糖趋势并提供智能建议
    """
    try:
        # 默认分析近三天数据
        days = request.days if request.days else 3
        
        # 获取近三天的血糖记录
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        records = get_user_glucose_records(
            db=db,
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )
        
        if not records or len(records) < 3:  # 至少需要3条记录才能分析
            return {
                "status": "error",
                "message": f"近{days}天内没有足够的血糖记录",
                "has_data": False
            }
        
        # 计算统计数据
        values = [record.value for record in records]
        avg_value = sum(values) / len(values)
        max_value = max(values)
        min_value = min(values)
        
        # 计算标准差
        import numpy as np
        std_value = np.std(values)
        
        # 计算达标率
        target_min = 3.9
        target_max = 7.8
        in_range_count = sum(1 for v in values if target_min <= v <= target_max)
        in_range_percentage = (in_range_count / len(values)) * 100
        
        # 计算高血糖和低血糖比例
        high_count = sum(1 for v in values if v > target_max)
        low_count = sum(1 for v in values if v < target_min)
        high_percentage = (high_count / len(values)) * 100
        low_percentage = (low_count / len(values)) * 100
        
        # 分析血糖模式
        patterns = analyze_glucose_patterns(records)
        
        # 使用大模型生成智能建议
        advice = await generate_glucose_advice(current_user, records, {
            "average": avg_value,
            "max": max_value,
            "min": min_value,
            "std": std_value,
            "in_range_percentage": in_range_percentage,
            "high_percentage": high_percentage,
            "low_percentage": low_percentage
        }, patterns)
        
        return {
            "status": "success",
            "has_data": True,
            "days": days,
            "record_count": len(records),
            "statistics": {
                "average": avg_value,
                "max": max_value,
                "min": min_value,
                "std": std_value,
                "in_range_percentage": in_range_percentage,
                "high_percentage": high_percentage,
                "low_percentage": low_percentage
            },
            "patterns": patterns,
            "advice": advice
        }
    except Exception as e:
        logger.error(f"分析血糖趋势失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析血糖趋势失败: {str(e)}")

@router.get("/supported-devices")
async def get_supported_devices() -> Dict[str, List[str]]:
    """
    获取支持的设备类型列表
    """
    return {
        "devices": glucose_monitor_service.supported_devices
    }

@router.post("/register-device")
async def register_device(
    request: DeviceRegistrationRequest,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    注册血糖监测设备，启用自动同步
    """
    if request.device_type not in glucose_monitor_service.supported_devices:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的设备类型: {request.device_type}"
        )
    
    try:
        # 注册设备到调度器
        if request.enable_auto_sync:
            glucose_scheduler.register_device(
                user_id=current_user.id,
                device_type=request.device_type,
                params=request.params
            )
            
        return {
            "status": "success",
            "message": f"成功注册{request.device_type}设备",
            "auto_sync": request.enable_auto_sync
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册设备失败: {str(e)}"
        )

@router.post("/unregister-device")
async def unregister_device(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    取消注册血糖监测设备，停止自动同步
    """
    try:
        glucose_scheduler.unregister_device(user_id=current_user.id)
        
        return {
            "status": "success",
            "message": "成功取消注册设备"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消注册设备失败: {str(e)}"
        )

# 后台任务
async def analyze_and_alert(db: Session, user_id: str, user_name: str):
    """
    后台任务：分析血糖数据并生成预警
    """
    try:
        # 分析最近24小时的数据
        analysis_result = await glucose_monitor_service.analyze_glucose_data(
            db=db,
            user_id=user_id,
            hours=24
        )
        
        # 如果有预警，生成预警消息
        if analysis_result.get("status") == "ok" and analysis_result.get("has_alerts", False):
            alert_message = await glucose_monitor_service.generate_alert_message(
                analysis_result=analysis_result,
                user_name=user_name
            )
            
            # 这里可以添加发送预警通知的逻辑，如发送短信、推送通知等
            # 目前只记录日志
            logger.warning(f"用户{user_name}的血糖预警: {alert_message}")
    except Exception as e:
        logger.error(f"后台分析血糖数据失败: {str(e)}")

# 分析血糖模式
def analyze_glucose_patterns(records):
    """分析血糖变化模式"""
    try:
        # 按时间排序
        sorted_records = sorted(records, key=lambda r: r.measured_at)
        
        # 按日期分组
        from collections import defaultdict
        import datetime
        
        records_by_date = defaultdict(list)
        for record in sorted_records:
            date_key = record.measured_at.date()
            records_by_date[date_key].append(record)
        
        # 分析早晨、下午、晚上的趋势
        morning_values = []
        afternoon_values = []
        evening_values = []
        
        for date, day_records in records_by_date.items():
            for record in day_records:
                hour = record.measured_at.hour
                if 5 <= hour < 12:
                    morning_values.append(record.value)
                elif 12 <= hour < 18:
                    afternoon_values.append(record.value)
                else:
                    evening_values.append(record.value)
        
        # 分析空腹和餐后血糖
        fasting_values = []
        postprandial_values = []
        
        for record in sorted_records:
            if record.measurement_time in ["BEFORE_BREAKFAST", "BEFORE_LUNCH", "BEFORE_DINNER"]:
                fasting_values.append(record.value)
            elif record.measurement_time in ["AFTER_BREAKFAST", "AFTER_LUNCH", "AFTER_DINNER"]:
                postprandial_values.append(record.value)
        
        # 计算日间变异性
        day_variances = []
        for date, day_records in records_by_date.items():
            if len(day_records) >= 2:
                day_values = [r.value for r in day_records]
                day_variances.append(max(day_values) - min(day_values))
        
        day_to_day_variance = sum(day_variances) / len(day_variances) if day_variances else 0
        
        # 计算高低血糖频次
        high_count = sum(1 for r in sorted_records if r.value > 10.0)
        low_count = sum(1 for r in sorted_records if r.value < 3.9)
        
        return {
            "morning_avg": sum(morning_values) / len(morning_values) if morning_values else 0,
            "afternoon_avg": sum(afternoon_values) / len(afternoon_values) if afternoon_values else 0,
            "evening_avg": sum(evening_values) / len(evening_values) if evening_values else 0,
            "fasting_avg": sum(fasting_values) / len(fasting_values) if fasting_values else 0,
            "postprandial_avg": sum(postprandial_values) / len(postprandial_values) if postprandial_values else 0,
            "day_to_day_variance": day_to_day_variance,
            "high_frequency": high_count,
            "low_frequency": low_count
        }
    except Exception as e:
        logger.error(f"分析血糖模式失败: {str(e)}")
        return {}

# 生成警报消息
async def generate_alert_message(user, alerts, records):
    """使用Ollama生成警报消息"""
    try:
        # 获取最新的警报
        latest_alert = sorted(alerts, key=lambda a: a.get("timestamp", ""), reverse=True)[0]
        
        # 构建提示词
        prompt = f"""
        我需要为糖尿病患者{user.name}生成一条血糖预警消息。以下是患者的血糖数据分析结果：
        
        警报类型: {latest_alert["type"]}
        警报严重程度: {latest_alert["severity"]}
        """
        
        if latest_alert["type"] == "low_glucose":
            prompt += f"""
            检测到低血糖情况:
            - 血糖值: {latest_alert["value"]} mmol/L
            - 低于正常范围: {latest_alert["threshold"]} mmol/L
            - 发生时间: {latest_alert["timestamp"]}
            """
        elif latest_alert["type"] == "high_glucose":
            prompt += f"""
            检测到高血糖情况:
            - 血糖值: {latest_alert["value"]} mmol/L
            - 高于正常范围: {latest_alert["threshold"]} mmol/L
            - 发生时间: {latest_alert["timestamp"]}
            """
        elif latest_alert["type"] in ["rapid_rise", "rapid_drop"]:
            direction = "上升" if latest_alert["type"] == "rapid_rise" else "下降"
            prompt += f"""
            检测到血糖快速{direction}:
            - 变化率: {latest_alert["value"]:.1f} mmol/L/小时
            - 从 {latest_alert["from_value"]} mmol/L 到 {latest_alert["to_value"]} mmol/L
            - 时间跨度: {latest_alert["time_diff"]:.1f} 小时
            - 发生时间: {latest_alert["timestamp"]}
            """
        
        prompt += """
        请生成一条简短的预警消息，包含以下内容：
        1. 当前状态描述
        2. 可能的风险
        3. 建议采取的措施
        
        请使用简洁、易懂的语言，不超过100字。
        """
        
        # 调用Ollama服务生成警报消息
        logger.info(f"使用模型 deepseek-r1:1.5b 生成回复，提示词:\n{prompt}")
        response = await ollama_service.generate(
            prompt=prompt,
            model="deepseek-r1:1.5b",
            temperature=0.7,
            max_tokens=200
        )
        
        return response.get("response", "无法生成警报消息")
    except Exception as e:
        logger.error(f"生成警报消息失败: {str(e)}")
        return None

# 使用大模型生成血糖管理建议
async def generate_glucose_advice(user, records, statistics, patterns):
    """使用Ollama生成个性化血糖管理建议"""
    try:
        # 构建提示词，包含更多上下文
        prompt = f"""
        我需要为糖尿病患者生成一份详细的血糖分析报告和管理建议。以下是患者近三天的血糖数据分析结果：
        
        患者基本信息:
        - 姓名: {user.name}
        - 糖尿病类型: {getattr(user, 'diabetes_type', '未知')}
        
        血糖统计数据:
        - 平均血糖: {statistics['average']:.1f} mmol/L
        - 最高血糖: {statistics['max']:.1f} mmol/L
        - 最低血糖: {statistics['min']:.1f} mmol/L
        - 标准差: {statistics['std']:.2f} mmol/L
        - 记录总数: {len(records)}
        - 目标范围内比例: {statistics['in_range_percentage']:.1f}%
        - 高于目标范围比例: {statistics['high_percentage']:.1f}%
        - 低于目标范围比例: {statistics['low_percentage']:.1f}%
        
        血糖模式分析:
        - 早晨平均血糖: {patterns.get('morning_avg', 0):.1f} mmol/L
        - 下午平均血糖: {patterns.get('afternoon_avg', 0):.1f} mmol/L
        - 晚上平均血糖: {patterns.get('evening_avg', 0):.1f} mmol/L
        - 空腹平均血糖: {patterns.get('fasting_avg', 0):.1f} mmol/L
        - 餐后平均血糖: {patterns.get('postprandial_avg', 0):.1f} mmol/L
        - 日间波动情况: {patterns.get('day_to_day_variance', 0):.1f} mmol/L
        - 高血糖发生频次: {patterns.get('high_frequency', 0)}
        - 低血糖发生频次: {patterns.get('low_frequency', 0)}
        
        请根据以上数据，提供以下内容：
        1. 血糖控制总体评估（良好/一般/需要改善）
        2. 具体问题分析（如晨间高血糖、餐后血糖波动大等）
        3. 针对性的改善建议（饮食、运动、用药调整等，但注明这些建议需咨询医生确认）
        4. 近期血糖监测重点（应特别关注的时间段或情况）
        
        请用通俗易懂的语言，条理清晰地回答，避免过于专业的医学术语。
        """
        
        # 调用Ollama服务生成建议
        logger.info(f"使用模型 deepseek-r1:1.5b 生成血糖管理建议")
        response = await ollama_service.generate(
            prompt=prompt,
            model="deepseek-r1:1.5b",
            temperature=0.7,
            max_tokens=800
        )
        
        return response.get("response", "无法生成血糖管理建议")
    except Exception as e:
        logger.error(f"生成血糖管理建议失败: {str(e)}")
        return "生成建议时发生错误，请稍后再试" 