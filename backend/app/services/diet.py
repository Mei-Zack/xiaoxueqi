from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from fastapi import HTTPException, status
from collections import Counter
from fastapi.encoders import jsonable_encoder
import logging

from app.db.models import DietRecord, User
from app.models.diet import (
    DietRecordCreate, DietRecordUpdate, DietRecord as DietRecordSchema, 
    DietStatistics, DietRecordPage
)

logger = logging.getLogger(__name__)

def create_diet_record(db: Session, record_in: DietRecordCreate) -> DietRecord:
    """创建新的饮食记录"""
    # 检查用户是否存在
    user = db.query(User).filter(User.id == record_in.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 创建记录，将Pydantic模型转换为可序列化的JSON
    food_items_json = jsonable_encoder(record_in.food_items)
    db_record = DietRecord(
        id=str(uuid.uuid4()),
        user_id=record_in.user_id,
        meal_type=record_in.meal_type,
        meal_time=record_in.meal_time,
        food_items=food_items_json,
        total_carbs=record_in.total_carbs,
        total_calories=record_in.total_calories,
        notes=record_in.notes,
        image_url=record_in.image_url
    )
    
    # 保存到数据库
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    
    return db_record


def get_diet_record(db: Session, record_id: str) -> Optional[DietRecord]:
    """通过ID获取饮食记录"""
    return db.query(DietRecord).filter(DietRecord.id == record_id).first()


def get_user_diet_records(
    db: Session, 
    user_id: str, 
    skip: int = 0, 
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    meal_type: Optional[str] = None
) -> DietRecordPage:
    """获取用户的饮食记录"""
    logger.info(f"Querying diet records for user_id={user_id} from DB")
    # 构建查询
    query = db.query(DietRecord).filter(DietRecord.user_id == user_id)
    
    # 添加日期过滤
    if start_date:
        query = query.filter(DietRecord.meal_time >= start_date)
    if end_date:
        query = query.filter(DietRecord.meal_time <= end_date)
    
    # 添加餐食类型过滤
    if meal_type:
        query = query.filter(DietRecord.meal_type == meal_type)
    
    # 获取总数
    total = query.count()
    
    # 按时间降序排序，分页
    records = query.order_by(desc(DietRecord.meal_time)).offset(skip).limit(limit).all()
    logger.info(f"DB returned {len(records)} records.")

    # inspect the raw data
    for i, record in enumerate(records):
        logger.info(f"Record {i} | id: {record.id} | food_items type: {type(record.food_items)} | food_items value: {record.food_items}")

    try:
        # Pydantic v2 from_attributes=True allows model_validate to work with ORM models
        validated_data = [DietRecordSchema.model_validate(record) for record in records]
        page = DietRecordPage(total=total, data=validated_data)
        logger.info("Successfully validated records with Pydantic model.")
        return page
    except Exception as e:
        logger.error(f"Pydantic validation failed for user {user_id}'s diet records: {e}", exc_info=True)
        # Re-raise the exception to be caught by the endpoint handler
        raise


def update_diet_record(db: Session, record_id: str, record_in: DietRecordUpdate) -> DietRecord:
    """更新饮食记录"""
    # 获取记录
    db_record = get_diet_record(db, record_id)
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="饮食记录不存在"
        )
    
    # 更新记录
    update_data = record_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(db_record, field) and value is not None:
            setattr(db_record, field, value)
    
    # 保存到数据库
    db.commit()
    db.refresh(db_record)
    
    return db_record


def delete_diet_record(db: Session, record_id: str) -> bool:
    """删除饮食记录"""
    db_record = get_diet_record(db, record_id)
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="饮食记录不存在"
        )
    
    db.delete(db_record)
    db.commit()
    
    return True


def get_diet_statistics(
    db: Session, 
    user_id: str, 
    period: str = "week"
) -> DietStatistics:
    """获取用户的饮食统计数据"""
    # 确定日期范围
    now = datetime.now()
    if period == "day":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    else:
        start_date = now - timedelta(days=90)  # 默认3个月
    
    # 查询记录
    records = db.query(DietRecord).filter(
        and_(
            DietRecord.user_id == user_id,
            DietRecord.meal_time >= start_date
        )
    ).all()
    
    # 如果没有记录，返回空统计
    if not records:
        return DietStatistics(
            average_daily_calories=0,
            average_daily_carbs=0,
            most_frequent_foods=[],
            period=period
        )
    
    # 计算统计数据
    total_days = (now - start_date).days + 1
    total_calories = sum(r.total_calories for r in records)
    total_carbs = sum(r.total_carbs for r in records)
    
    # 计算每日平均值
    avg_daily_calories = total_calories / total_days if total_days > 0 else 0
    avg_daily_carbs = total_carbs / total_days if total_days > 0 else 0
    
    # 统计最常见的食物
    all_foods = []
    for record in records:
        food_items = record.food_items
        if isinstance(food_items, list):
            for item in food_items:
                if isinstance(item, dict) and "name" in item:
                    all_foods.append(item["name"])
    
    # 获取前5个最常见的食物
    food_counter = Counter(all_foods)
    most_common_foods = [food for food, _ in food_counter.most_common(5)]
    
    return DietStatistics(
        average_daily_calories=round(avg_daily_calories, 2),
        average_daily_carbs=round(avg_daily_carbs, 2),
        most_frequent_foods=most_common_foods,
        period=period
    ) 