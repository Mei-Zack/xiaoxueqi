from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.api.deps import get_current_user, get_db
from app.db.models import User
from app.models.glucose import GlucoseCreate, GlucoseUpdate, Glucose, GlucoseStatistics
from app.services.glucose import (
    create_glucose_record, get_glucose_record, get_user_glucose_records,
    update_glucose_record, delete_glucose_record, get_glucose_statistics
)

router = APIRouter()


@router.post("", response_model=Glucose)
def create_record(
    record_in: GlucoseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    创建新的血糖记录
    """
    # 确保只能为自己创建记录
    if record_in.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能为自己创建记录"
        )
    
    return create_glucose_record(db=db, record_in=record_in)


@router.get("", response_model=List[Glucose])
def read_records(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取当前用户的血糖记录
    """
    return get_user_glucose_records(
        db=db, 
        user_id=current_user.id, 
        skip=skip, 
        limit=limit,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/statistics", response_model=GlucoseStatistics)
def read_statistics(
    period: str = Query("week", enum=["day", "week", "month", "quarter"]),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取血糖统计数据
    """
    return get_glucose_statistics(db=db, user_id=current_user.id, period=period)


@router.get("/recent", response_model=List[Glucose])
def read_recent_records(
    days: int = Query(7, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取最近几天的血糖记录
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    return get_user_glucose_records(
        db=db, 
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/{record_id}", response_model=Glucose)
def read_record(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取单条血糖记录
    """
    record = get_glucose_record(db=db, record_id=record_id)
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


@router.put("/{record_id}", response_model=Glucose)
def update_record(
    record_id: str,
    record_in: GlucoseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    更新血糖记录
    """
    record = get_glucose_record(db=db, record_id=record_id)
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
    
    return update_glucose_record(db=db, record_id=record_id, record_in=record_in)


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """
    删除血糖记录
    """
    record = get_glucose_record(db=db, record_id=record_id)
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
    
    delete_glucose_record(db=db, record_id=record_id) 