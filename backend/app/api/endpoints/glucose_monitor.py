from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.api.deps import get_current_user, get_db
from app.db.models import User
from app.services.glucose_monitor import glucose_monitor_service
from app.core.scheduler import glucose_scheduler

router = APIRouter()

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
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    分析血糖数据并检测异常
    """
    try:
        # 分析数据
        analysis_result = await glucose_monitor_service.analyze_glucose_data(
            db=db,
            user_id=current_user.id,
            hours=request.hours
        )
        
        # 如果有预警，生成预警消息
        alert_message = None
        if analysis_result.get("status") == "ok" and analysis_result.get("has_alerts", False):
            alert_message = await glucose_monitor_service.generate_alert_message(
                analysis_result=analysis_result,
                user_name=current_user.name
            )
        
        # 构建响应
        response = {
            **analysis_result,
            "alert_message": alert_message
        }
        
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分析血糖数据失败: {str(e)}"
        )

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
            from logging import getLogger
            logger = getLogger(__name__)
            logger.warning(f"用户{user_name}的血糖预警: {alert_message}")
    except Exception as e:
        from logging import getLogger
        logger = getLogger(__name__)
        logger.error(f"后台分析血糖数据失败: {str(e)}") 