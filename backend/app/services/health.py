from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from fastapi import HTTPException, status
import logging

from app.db.models import (
    HealthRecord, WeightRecord, BloodPressureRecord, 
    ExerciseRecord, MedicationRecord, User
)
from app.models.health import (
    HealthCreate, HealthUpdate, Health as HealthSchema,
    WeightRecord as WeightRecordSchema,
    BloodPressureRecord as BloodPressureRecordSchema,
    ExerciseRecord as ExerciseRecordSchema,
    MedicationRecord as MedicationRecordSchema
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_health_record(db: Session, record_in: HealthCreate) -> HealthRecord:
    """创建新的健康记录"""
    # 记录请求数据
    logger.info(f"创建健康记录: {record_in.dict()}")
    
    # 检查用户是否存在
    user = db.query(User).filter(User.id == record_in.user_id).first()
    if not user:
        logger.error(f"用户不存在: {record_in.user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    try:
        # 创建健康记录
        db_record = HealthRecord(
            id=str(uuid.uuid4()),
            user_id=record_in.user_id,
            record_date=record_in.record_date,
            notes=record_in.notes
        )
        
        # 保存到数据库
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        
        # 添加体重记录
        if record_in.weight_records:
            for weight_data in record_in.weight_records:
                weight_record = WeightRecord(
                    id=str(uuid.uuid4()),
                    health_record_id=db_record.id,
                    user_id=record_in.user_id,
                    weight=weight_data.weight,
                    bmi=weight_data.bmi,
                    body_fat=weight_data.body_fat,
                    measured_at=weight_data.measured_at,
                    notes=weight_data.notes
                )
                db.add(weight_record)
        
        # 添加血压记录
        if record_in.blood_pressure_records:
            for bp_data in record_in.blood_pressure_records:
                bp_record = BloodPressureRecord(
                    id=str(uuid.uuid4()),
                    health_record_id=db_record.id,
                    user_id=record_in.user_id,
                    systolic=bp_data.systolic,
                    diastolic=bp_data.diastolic,
                    pulse=bp_data.pulse,
                    measured_at=bp_data.measured_at,
                    notes=bp_data.notes
                )
                db.add(bp_record)
        
        # 添加运动记录
        if record_in.exercise_records:
            for exercise_data in record_in.exercise_records:
                exercise_record = ExerciseRecord(
                    id=str(uuid.uuid4()),
                    health_record_id=db_record.id,
                    user_id=record_in.user_id,
                    exercise_type=exercise_data.exercise_type,
                    duration=exercise_data.duration,
                    intensity=exercise_data.intensity,
                    calories_burned=exercise_data.calories_burned,
                    start_time=exercise_data.start_time,
                    end_time=exercise_data.end_time,
                    notes=exercise_data.notes
                )
                db.add(exercise_record)
        
        # 添加药物记录
        if record_in.medication_records:
            for med_data in record_in.medication_records:
                med_record = MedicationRecord(
                    id=str(uuid.uuid4()),
                    health_record_id=db_record.id,
                    user_id=record_in.user_id,
                    name=med_data.name,
                    dosage=med_data.dosage,
                    taken_at=med_data.taken_at,
                    scheduled_at=med_data.scheduled_at,
                    is_taken=med_data.is_taken,
                    notes=med_data.notes
                )
                db.add(med_record)
        
        # 提交所有记录
        db.commit()
        logger.info(f"健康记录创建成功: {db_record.id}")
        return db_record
    except Exception as e:
        db.rollback()
        logger.error(f"创建健康记录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建健康记录失败: {str(e)}"
        )


def get_health_record(db: Session, record_id: str) -> Optional[HealthRecord]:
    """通过ID获取健康记录"""
    logger.info(f"获取健康记录: {record_id}")
    record = db.query(HealthRecord).filter(HealthRecord.id == record_id).first()
    if record:
        logger.info(f"获取健康记录成功: {record_id}")
    else:
        logger.warning(f"健康记录不存在: {record_id}")
    return record


def get_user_health_records(
    db: Session, 
    user_id: str, 
    skip: int = 0, 
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[HealthRecord]:
    """获取用户的健康记录"""
    logger.info(f"获取用户健康记录: user_id={user_id}, skip={skip}, limit={limit}, start_date={start_date}, end_date={end_date}")
    
    # 构建查询
    query = db.query(HealthRecord).filter(HealthRecord.user_id == user_id)
    
    # 添加日期过滤
    if start_date:
        query = query.filter(HealthRecord.record_date >= start_date)
    if end_date:
        query = query.filter(HealthRecord.record_date <= end_date)
    
    # 按时间降序排序，分页
    records = query.order_by(desc(HealthRecord.record_date)).offset(skip).limit(limit).all()
    logger.info(f"获取到 {len(records)} 条健康记录")
    return records


def update_health_record(db: Session, record_id: str, record_in: HealthUpdate) -> HealthRecord:
    """更新健康记录"""
    # 获取记录
    db_record = get_health_record(db, record_id)
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="健康记录不存在"
        )
    
    # 更新记录
    if record_in.notes is not None:
        db_record.notes = record_in.notes
    
    # 更新体重记录
    if record_in.weight_records is not None:
        # 删除现有记录
        db.query(WeightRecord).filter(WeightRecord.health_record_id == record_id).delete()
        
        # 添加新记录
        for weight_data in record_in.weight_records:
            weight_record = WeightRecord(
                id=str(uuid.uuid4()),
                health_record_id=db_record.id,
                user_id=db_record.user_id,
                weight=weight_data.weight,
                bmi=weight_data.bmi,
                body_fat=weight_data.body_fat,
                measured_at=weight_data.measured_at,
                notes=weight_data.notes
            )
            db.add(weight_record)
    
    # 更新血压记录
    if record_in.blood_pressure_records is not None:
        # 删除现有记录
        db.query(BloodPressureRecord).filter(BloodPressureRecord.health_record_id == record_id).delete()
        
        # 添加新记录
        for bp_data in record_in.blood_pressure_records:
            bp_record = BloodPressureRecord(
                id=str(uuid.uuid4()),
                health_record_id=db_record.id,
                user_id=db_record.user_id,
                systolic=bp_data.systolic,
                diastolic=bp_data.diastolic,
                pulse=bp_data.pulse,
                measured_at=bp_data.measured_at,
                notes=bp_data.notes
            )
            db.add(bp_record)
    
    # 更新运动记录
    if record_in.exercise_records is not None:
        # 删除现有记录
        db.query(ExerciseRecord).filter(ExerciseRecord.health_record_id == record_id).delete()
        
        # 添加新记录
        for exercise_data in record_in.exercise_records:
            exercise_record = ExerciseRecord(
                id=str(uuid.uuid4()),
                health_record_id=db_record.id,
                user_id=db_record.user_id,
                exercise_type=exercise_data.exercise_type,
                duration=exercise_data.duration,
                intensity=exercise_data.intensity,
                calories_burned=exercise_data.calories_burned,
                start_time=exercise_data.start_time,
                end_time=exercise_data.end_time,
                notes=exercise_data.notes
            )
            db.add(exercise_record)
    
    # 更新药物记录
    if record_in.medication_records is not None:
        # 删除现有记录
        db.query(MedicationRecord).filter(MedicationRecord.health_record_id == record_id).delete()
        
        # 添加新记录
        for med_data in record_in.medication_records:
            med_record = MedicationRecord(
                id=str(uuid.uuid4()),
                health_record_id=db_record.id,
                user_id=db_record.user_id,
                name=med_data.name,
                dosage=med_data.dosage,
                taken_at=med_data.taken_at,
                scheduled_at=med_data.scheduled_at,
                is_taken=med_data.is_taken,
                notes=med_data.notes
            )
            db.add(med_record)
    
    # 保存到数据库
    db.commit()
    db.refresh(db_record)
    
    return db_record


def delete_health_record(db: Session, record_id: str) -> bool:
    """删除健康记录"""
    db_record = get_health_record(db, record_id)
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="健康记录不存在"
        )
    
    # 删除相关记录
    db.query(WeightRecord).filter(WeightRecord.health_record_id == record_id).delete()
    db.query(BloodPressureRecord).filter(BloodPressureRecord.health_record_id == record_id).delete()
    db.query(ExerciseRecord).filter(ExerciseRecord.health_record_id == record_id).delete()
    db.query(MedicationRecord).filter(MedicationRecord.health_record_id == record_id).delete()
    
    # 删除主记录
    db.delete(db_record)
    db.commit()
    
    return True


# 单独的记录服务
def create_weight_record(db: Session, user_id: str, record_data: WeightRecordSchema) -> WeightRecord:
    """创建体重记录"""
    # 查找或创建今天的健康记录
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    health_record = db.query(HealthRecord).filter(
        and_(
            HealthRecord.user_id == user_id,
            func.date(HealthRecord.record_date) == func.date(today)
        )
    ).first()
    
    if not health_record:
        health_record = HealthRecord(
            id=str(uuid.uuid4()),
            user_id=user_id,
            record_date=today
        )
        db.add(health_record)
        db.commit()
        db.refresh(health_record)
    
    # 创建体重记录
    weight_record = WeightRecord(
        id=str(uuid.uuid4()),
        health_record_id=health_record.id,
        user_id=user_id,
        weight=record_data.weight,
        bmi=record_data.bmi,
        body_fat=record_data.body_fat,
        measured_at=record_data.measured_at or datetime.now(),
        notes=record_data.notes
    )
    
    db.add(weight_record)
    db.commit()
    db.refresh(weight_record)
    
    return weight_record


def create_blood_pressure_record(db: Session, user_id: str, record_data: BloodPressureRecordSchema) -> BloodPressureRecord:
    """创建血压记录"""
    # 查找或创建今天的健康记录
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    health_record = db.query(HealthRecord).filter(
        and_(
            HealthRecord.user_id == user_id,
            func.date(HealthRecord.record_date) == func.date(today)
        )
    ).first()
    
    if not health_record:
        health_record = HealthRecord(
            id=str(uuid.uuid4()),
            user_id=user_id,
            record_date=today
        )
        db.add(health_record)
        db.commit()
        db.refresh(health_record)
    
    # 创建血压记录
    bp_record = BloodPressureRecord(
        id=str(uuid.uuid4()),
        health_record_id=health_record.id,
        user_id=user_id,
        systolic=record_data.systolic,
        diastolic=record_data.diastolic,
        pulse=record_data.pulse,
        measured_at=record_data.measured_at or datetime.now(),
        notes=record_data.notes
    )
    
    db.add(bp_record)
    db.commit()
    db.refresh(bp_record)
    
    return bp_record


def create_exercise_record(db: Session, user_id: str, record_data: ExerciseRecordSchema) -> ExerciseRecord:
    """创建运动记录"""
    # 查找或创建今天的健康记录
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    health_record = db.query(HealthRecord).filter(
        and_(
            HealthRecord.user_id == user_id,
            func.date(HealthRecord.record_date) == func.date(today)
        )
    ).first()
    
    if not health_record:
        health_record = HealthRecord(
            id=str(uuid.uuid4()),
            user_id=user_id,
            record_date=today
        )
        db.add(health_record)
        db.commit()
        db.refresh(health_record)
    
    # 创建运动记录
    exercise_record = ExerciseRecord(
        id=str(uuid.uuid4()),
        health_record_id=health_record.id,
        user_id=user_id,
        exercise_type=record_data.exercise_type,
        duration=record_data.duration,
        intensity=record_data.intensity,
        calories_burned=record_data.calories_burned,
        start_time=record_data.start_time or datetime.now(),
        end_time=record_data.end_time,
        notes=record_data.notes
    )
    
    db.add(exercise_record)
    db.commit()
    db.refresh(exercise_record)
    
    return exercise_record


def create_medication_record(db: Session, user_id: str, record_data: MedicationRecordSchema) -> MedicationRecord:
    """创建药物记录"""
    # 查找或创建今天的健康记录
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    health_record = db.query(HealthRecord).filter(
        and_(
            HealthRecord.user_id == user_id,
            func.date(HealthRecord.record_date) == func.date(today)
        )
    ).first()
    
    if not health_record:
        health_record = HealthRecord(
            id=str(uuid.uuid4()),
            user_id=user_id,
            record_date=today
        )
        db.add(health_record)
        db.commit()
        db.refresh(health_record)
    
    # 创建药物记录
    med_record = MedicationRecord(
        id=str(uuid.uuid4()),
        health_record_id=health_record.id,
        user_id=user_id,
        name=record_data.name,
        dosage=record_data.dosage,
        taken_at=record_data.taken_at or datetime.now(),
        scheduled_at=record_data.scheduled_at,
        is_taken=record_data.is_taken,
        notes=record_data.notes
    )
    
    db.add(med_record)
    db.commit()
    db.refresh(med_record)
    
    return med_record 