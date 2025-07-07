import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db.models import GlucoseRecord, User
from app.ml.ollama_service import ollama_service
from app.services.glucose import get_user_glucose_records
from app.core.config import settings

# 配置日志
logger = logging.getLogger(__name__)

class GlucoseMonitorService:
    """血糖监测服务，用于从设备获取血糖数据并进行预警"""
    
    def __init__(self):
        self.alert_thresholds = {
            "low": 3.9,  # 低血糖阈值，单位mmol/L
            "high": 10.0,  # 高血糖阈值，单位mmol/L
            "rapid_drop": 2.0,  # 快速下降阈值，单位mmol/L/小时
            "rapid_rise": 2.5,  # 快速上升阈值，单位mmol/L/小时
        }
        # 支持的设备类型
        self.supported_devices = ["freestyle_libre", "dexcom", "medtronic"]
        
    async def get_device_data(self, device_type: str, user_id: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        从设备获取血糖数据
        
        Args:
            device_type: 设备类型（freestyle_libre, dexcom, medtronic等）
            user_id: 用户ID
            params: 设备特定的参数
            
        Returns:
            血糖数据列表
        """
        if device_type not in self.supported_devices:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的设备类型: {device_type}"
            )
            
        try:
            if device_type == "freestyle_libre":
                return await self._get_freestyle_libre_data(user_id, params)
            elif device_type == "dexcom":
                return await self._get_dexcom_data(user_id, params)
            elif device_type == "medtronic":
                return await self._get_medtronic_data(user_id, params)
            else:
                return []
        except Exception as e:
            logger.error(f"获取设备数据失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取设备数据失败: {str(e)}"
            )
    
    async def _get_freestyle_libre_data(self, user_id: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        从Freestyle Libre设备获取血糖数据
        
        参考文章: https://frdmtoplay.com/freeing-glucose-data-from-the-freestyle-libre-3/
        
        Args:
            user_id: 用户ID
            params: 设备特定的参数，可能包含:
                - db_path: RealmDB文件路径
                - encryption_key: 解密密钥
                
        Returns:
            血糖数据列表
        """
        logger.info(f"尝试从Freestyle Libre获取用户 {user_id} 的血糖数据")
        
        # 这里应该实现与Freestyle Libre设备的集成
        # 由于需要特定的硬件和软件环境，此处提供模拟数据
        # 实际实现应该根据参考文章中的方法解密RealmDB
        
        # 模拟数据
        now = datetime.now()
        data = []
        for i in range(24):  # 模拟24小时的数据，每小时一条
            timestamp = now - timedelta(hours=i)
            # 模拟一个在4.0-10.0之间的血糖值
            value = 7.0 + (i % 5 - 2) * 0.8
            data.append({
                "timestamp": timestamp.isoformat(),
                "value": round(value, 1),
                "unit": "mmol/L"
            })
            
        return data
    
    async def _get_dexcom_data(self, user_id: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        从Dexcom设备获取血糖数据
        
        参考: https://github.com/coderkearns/dexcom
        
        Args:
            user_id: 用户ID
            params: 设备特定的参数，可能包含:
                - username: Dexcom账号用户名
                - password: Dexcom账号密码
                
        Returns:
            血糖数据列表
        """
        logger.info(f"尝试从Dexcom获取用户 {user_id} 的血糖数据")
        
        # 这里应该实现与Dexcom API的集成
        # 实际实现应该使用Dexcom Share API
        
        # 模拟数据
        now = datetime.now()
        data = []
        for i in range(24):  # 模拟24小时的数据，每小时一条
            timestamp = now - timedelta(hours=i)
            # 模拟一个在4.0-10.0之间的血糖值，与时间相关
            value = 7.0 + (i % 6 - 3) * 0.7
            data.append({
                "timestamp": timestamp.isoformat(),
                "value": round(value, 1),
                "unit": "mmol/L"
            })
            
        return data
    
    async def _get_medtronic_data(self, user_id: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """从Medtronic设备获取血糖数据"""
        # 实现类似于其他设备的方法
        # 此处省略实现细节
        return []
    
    async def save_glucose_data(self, db: Session, user_id: str, glucose_data: List[Dict[str, Any]]) -> List[GlucoseRecord]:
        """
        保存血糖数据到数据库
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            glucose_data: 血糖数据列表
            
        Returns:
            保存的血糖记录列表
        """
        import uuid
        from app.models.glucose import MeasurementTimeEnum, MeasurementMethodEnum
        
        saved_records = []
        for data in glucose_data:
            try:
                # 获取时间戳
                timestamp_str = data.get("timestamp", data.get("measured_at"))
                if not timestamp_str:
                    logger.error(f"数据缺少时间戳: {data}")
                    continue
                
                # 解析时间戳
                try:
                    measured_at = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                except ValueError:
                    # 尝试其他格式
                    try:
                        measured_at = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")
                    except ValueError:
                        logger.error(f"无法解析时间戳: {timestamp_str}")
                        continue
                
                # 确定测量时间类型
                if "measurement_time" in data:
                    # 使用提供的测量时间类型
                    measurement_time = data["measurement_time"]
                else:
                    # 根据小时自动确定测量时间类型
                    hour = measured_at.hour
                    if 4 <= hour < 7:
                        measurement_time = "BEFORE_BREAKFAST"
                    elif 7 <= hour < 10:
                        measurement_time = "AFTER_BREAKFAST"
                    elif 10 <= hour < 12:
                        measurement_time = "BEFORE_LUNCH"
                    elif 12 <= hour < 15:
                        measurement_time = "AFTER_LUNCH"
                    elif 15 <= hour < 18:
                        measurement_time = "BEFORE_DINNER"
                    elif 18 <= hour < 21:
                        measurement_time = "AFTER_DINNER"
                    else:
                        measurement_time = "BEFORE_SLEEP"
                
                # 获取血糖值
                glucose_value = data.get("value", data.get("glucose_value"))
                if glucose_value is None:
                    logger.error(f"数据缺少血糖值: {data}")
                    continue
                
                # 创建记录
                record = GlucoseRecord(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    value=glucose_value,
                    measurement_time=measurement_time,
                    measurement_method="FINGER_STICK",
                    measured_at=measured_at,
                    notes=data.get("notes", "从设备自动导入"),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                # 保存到数据库
                db.add(record)
                db.commit()
                db.refresh(record)
                saved_records.append(record)
                logger.info(f"创建血糖记录: {record.__dict__}")
                
            except Exception as e:
                db.rollback()
                logger.error(f"保存血糖记录失败: {str(e)}")
        
        return saved_records
    
    async def analyze_glucose_data(self, db: Session, user_id: str, hours: int = 24) -> Dict[str, Any]:
        """
        分析血糖数据并检测异常
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            hours: 分析最近多少小时的数据
            
        Returns:
            分析结果
        """
        # 获取用户设置的目标血糖范围
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 使用用户设置的目标范围，如果没有设置则使用默认值
        target_min = user.target_glucose_min or self.alert_thresholds["low"]
        target_max = user.target_glucose_max or self.alert_thresholds["high"]
        
        # 获取最近的血糖数据
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=hours)
        
        # 直接查询glucose_records表
        records = db.query(GlucoseRecord).filter(
            GlucoseRecord.user_id == user_id,
            GlucoseRecord.measured_at >= start_date,
            GlucoseRecord.measured_at <= end_date
        ).order_by(GlucoseRecord.measured_at.desc()).all()
        
        if not records:
            return {
                "status": "no_data",
                "message": f"没有找到最近{hours}小时的血糖数据"
            }
        
        # 分析数据
        values = [r.value for r in records]
        timestamps = [r.measured_at for r in records]
        
        # 计算统计数据
        avg_value = sum(values) / len(values)
        max_value = max(values)
        min_value = min(values)
        
        # 检测异常
        alerts = []
        
        # 检查是否有低血糖
        if min_value < target_min:
            alerts.append({
                "type": "low_glucose",
                "value": min_value,
                "threshold": target_min,
                "timestamp": timestamps[values.index(min_value)].isoformat(),
                "severity": "high" if min_value < target_min - 1 else "medium"
            })
        
        # 检查是否有高血糖
        if max_value > target_max:
            alerts.append({
                "type": "high_glucose",
                "value": max_value,
                "threshold": target_max,
                "timestamp": timestamps[values.index(max_value)].isoformat(),
                "severity": "high" if max_value > target_max + 2 else "medium"
            })
        
        # 检查快速变化
        if len(records) >= 2:
            for i in range(len(records) - 1):
                time_diff = (timestamps[i] - timestamps[i+1]).total_seconds() / 3600  # 小时
                if time_diff > 0:
                    value_diff = values[i] - values[i+1]
                    rate = value_diff / time_diff
                    
                    if rate > self.alert_thresholds["rapid_rise"]:
                        alerts.append({
                            "type": "rapid_rise",
                            "value": rate,
                            "threshold": self.alert_thresholds["rapid_rise"],
                            "from_value": values[i+1],
                            "to_value": values[i],
                            "from_time": timestamps[i+1].isoformat(),
                            "to_time": timestamps[i].isoformat(),
                            "severity": "medium"
                        })
                    elif rate < -self.alert_thresholds["rapid_drop"]:
                        alerts.append({
                            "type": "rapid_drop",
                            "value": abs(rate),
                            "threshold": self.alert_thresholds["rapid_drop"],
                            "from_value": values[i+1],
                            "to_value": values[i],
                            "from_time": timestamps[i+1].isoformat(),
                            "to_time": timestamps[i].isoformat(),
                            "severity": "high"
                        })
        
        return {
            "status": "ok",
            "statistics": {
                "average": round(avg_value, 2),
                "max": max_value,
                "min": min_value,
                "count": len(values),
                "period_hours": hours
            },
            "alerts": alerts,
            "has_alerts": len(alerts) > 0
        }
    
    async def generate_alert_message(self, analysis_result: Dict[str, Any], user_name: str) -> str:
        """
        根据分析结果生成预警消息
        
        Args:
            analysis_result: 分析结果
            user_name: 用户姓名
            
        Returns:
            预警消息
        """
        if analysis_result["status"] != "ok" or not analysis_result["has_alerts"]:
            return f"{user_name}的血糖状态正常，无需预警。"
        
        # 构建提示词
        alerts = analysis_result["alerts"]
        stats = analysis_result["statistics"]
        
        prompt = f"""
        我需要为糖尿病患者{user_name}生成一条血糖预警消息。以下是患者的血糖数据分析结果：
        
        - 平均血糖: {stats['average']} mmol/L
        - 最高血糖: {stats['max']} mmol/L
        - 最低血糖: {stats['min']} mmol/L
        - 数据点数量: {stats['count']}
        - 分析周期: 最近{stats['period_hours']}小时
        
        检测到以下预警情况：
        """
        
        for alert in alerts:
            if alert["type"] == "low_glucose":
                prompt += f"- 低血糖预警: 血糖值 {alert['value']} mmol/L，低于阈值 {alert['threshold']} mmol/L，时间: {alert['timestamp']}，严重程度: {alert['severity']}\n"
            elif alert["type"] == "high_glucose":
                prompt += f"- 高血糖预警: 血糖值 {alert['value']} mmol/L，高于阈值 {alert['threshold']} mmol/L，时间: {alert['timestamp']}，严重程度: {alert['severity']}\n"
            elif alert["type"] == "rapid_rise":
                prompt += f"- 血糖快速上升预警: 上升速率 {round(alert['value'], 2)} mmol/L/小时，从 {alert['from_value']} 上升到 {alert['to_value']}，时间段: {alert['from_time']} 到 {alert['to_time']}，严重程度: {alert['severity']}\n"
            elif alert["type"] == "rapid_drop":
                prompt += f"- 血糖快速下降预警: 下降速率 {round(alert['value'], 2)} mmol/L/小时，从 {alert['from_value']} 下降到 {alert['to_value']}，时间段: {alert['from_time']} 到 {alert['to_time']}，严重程度: {alert['severity']}\n"
        
        prompt += """
        请根据以上信息，生成一条简短、清晰的预警消息，包括：
        1. 当前血糖状态的简要描述
        2. 可能的风险和建议
        3. 需要采取的措施
        
        消息应该专业但易于理解，不要过于专业化，适合患者本人阅读。
        """
        
        try:
            # 调用Ollama生成预警消息
            response = await ollama_service.generate(
                prompt=prompt,
                model="deepseek-r1:1.5b",  # 使用指定的模型
                temperature=0.7,
                max_tokens=512
            )
            
            alert_message = response.get("response", "无法生成预警消息")
            return alert_message
        except Exception as e:
            logger.error(f"生成预警消息失败: {str(e)}")
            # 如果生成失败，返回一个基本的预警消息
            return f"警告: {user_name}的血糖出现异常，请查看详细分析结果。"


# 创建服务实例
glucose_monitor_service = GlucoseMonitorService() 