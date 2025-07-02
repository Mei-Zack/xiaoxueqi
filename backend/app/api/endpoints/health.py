from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.api.deps import get_current_user, get_db
from app.db.models import User
from app.models.health import (
    HealthCreate, HealthUpdate, Health,
    WeightRecord, BloodPressureRecord, ExerciseRecord, MedicationRecord
)
from app.services.health import (
    create_health_record, get_health_record, get_user_health_records,
    update_health_record, delete_health_record,
    create_weight_record, create_blood_pressure_record,
    create_exercise_record, create_medication_record
)

router = APIRouter()


@router.post("", response_model=Health)
def create_record(
    record_in: HealthCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    创建新的健康记录
    """
    # 确保只能为自己创建记录
    if record_in.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能为自己创建记录"
        )
    
    return create_health_record(db=db, record_in=record_in)


@router.get("", response_model=List[Health])
def read_records(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取当前用户的健康记录
    """
    return get_user_health_records(
        db=db, 
        user_id=current_user.id, 
        skip=skip, 
        limit=limit,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/recent", response_model=List[Health])
def read_recent_records(
    days: int = Query(7, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取最近几天的健康记录
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    return get_user_health_records(
        db=db, 
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/{record_id}", response_model=Health)
def read_record(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取单条健康记录
    """
    record = get_health_record(db=db, record_id=record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )
    
    # 确保只能查看自己的记录
    if record.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此记录"
        )
    
    return record


@router.put("/{record_id}", response_model=Health)
def update_record(
    record_id: str,
    record_in: HealthUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    更新健康记录
    """
    record = get_health_record(db=db, record_id=record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )
    
    # 确保只能更新自己的记录
    if record.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权更新此记录"
        )
    
    return update_health_record(db=db, record_id=record_id, record_in=record_in)


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """
    删除健康记录
    """
    record = get_health_record(db=db, record_id=record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )
    
    # 确保只能删除自己的记录
    if record.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此记录"
        )
    
    delete_health_record(db=db, record_id=record_id)


# 单独的记录端点
@router.post("/weight", response_model=dict)
def create_weight(
    record_in: WeightRecord,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    创建体重记录
    """
    # 确保只能为自己创建记录
    if record_in.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能为自己创建记录"
        )
    
    record = create_weight_record(db=db, user_id=current_user.id, record_data=record_in)
    
    return {
        "id": record.id,
        "message": "体重记录创建成功",
        "weight": record.weight,
        "measured_at": record.measured_at
    }


@router.post("/blood-pressure", response_model=dict)
def create_blood_pressure(
    record_in: BloodPressureRecord,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    创建血压记录
    """
    # 确保只能为自己创建记录
    if record_in.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能为自己创建记录"
        )
    
    record = create_blood_pressure_record(db=db, user_id=current_user.id, record_data=record_in)
    
    return {
        "id": record.id,
        "message": "血压记录创建成功",
        "systolic": record.systolic,
        "diastolic": record.diastolic,
        "measured_at": record.measured_at
    }


@router.post("/exercise", response_model=dict)
def create_exercise(
    record_in: ExerciseRecord,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    创建运动记录
    """
    # 确保只能为自己创建记录
    if record_in.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能为自己创建记录"
        )
    
    record = create_exercise_record(db=db, user_id=current_user.id, record_data=record_in)
    
    return {
        "id": record.id,
        "message": "运动记录创建成功",
        "exercise_type": record.exercise_type,
        "duration": record.duration,
        "start_time": record.start_time
    }


@router.post("/medication", response_model=dict)
def create_medication(
    record_in: MedicationRecord,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    创建药物记录
    """
    # 确保只能为自己创建记录
    if record_in.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能为自己创建记录"
        )
    
    record = create_medication_record(db=db, user_id=current_user.id, record_data=record_in)
    
    return {
        "id": record.id,
        "message": "药物记录创建成功",
        "name": record.name,
        "dosage": record.dosage,
        "taken_at": record.taken_at
    } 