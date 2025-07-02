from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os
import uuid
from PIL import Image
import io
import logging

from app.api.deps import get_current_user, get_db
from app.db.models import User
from app.models.diet import DietRecordCreate, DietRecordUpdate, DietRecord, DietStatistics, MealTypeEnum, DietRecordPage
from app.services.diet import (
    create_diet_record, get_diet_record, get_user_diet_records,
    update_diet_record, delete_diet_record, get_diet_statistics
)
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", response_model=DietRecord)
def create_record(
    record_in: DietRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    创建新的饮食记录
    """
    # 确保只能为自己创建记录
    if record_in.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能为自己创建记录"
        )
    
    return create_diet_record(db=db, record_in=record_in)


@router.get("", response_model=DietRecordPage)
def read_records(
    skip: int = 0,
    limit: int = 10,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    meal_type: Optional[MealTypeEnum] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取当前用户的饮食记录
    """
    logger.info(f"User {current_user.id} fetching diet records with skip={skip}, limit={limit}")
    try:
        result = get_user_diet_records(
            db=db, 
            user_id=current_user.id, 
            skip=skip, 
            limit=limit,
            start_date=start_date,
            end_date=end_date,
            meal_type=meal_type
        )
        logger.info(f"Successfully fetched {len(result.data)} records for user {current_user.id}")
        return result
    except Exception as e:
        logger.error(f"Error fetching diet records for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取饮食记录时发生内部错误"
        )


@router.get("/statistics", response_model=DietStatistics)
def read_statistics(
    period: str = Query("week", enum=["day", "week", "month", "quarter"]),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取饮食统计数据
    """
    return get_diet_statistics(db=db, user_id=current_user.id, period=period)


@router.get("/recent", response_model=List[DietRecord])
def read_recent_records(
    days: int = Query(7, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取最近几天的饮食记录
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    return get_user_diet_records(
        db=db, 
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/{record_id}", response_model=DietRecord)
def read_record(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取单条饮食记录
    """
    record = get_diet_record(db=db, record_id=record_id)
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


@router.put("/{record_id}", response_model=DietRecord)
def update_record(
    record_id: str,
    record_in: DietRecordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    更新饮食记录
    """
    record = get_diet_record(db=db, record_id=record_id)
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
    
    return update_diet_record(db=db, record_id=record_id, record_in=record_in)


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """
    删除饮食记录
    """
    record = get_diet_record(db=db, record_id=record_id)
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
    
    delete_diet_record(db=db, record_id=record_id)


@router.post("/upload-image", response_model=dict)
async def upload_food_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    上传食物图片
    """
    # 验证文件类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能上传图片文件"
        )
    
    # 创建用户上传目录
    upload_dir = os.path.join("uploads", "diet", current_user.id)
    os.makedirs(upload_dir, exist_ok=True)
    
    # 生成唯一文件名
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # 保存文件
    try:
        # 读取上传的文件内容
        contents = await file.read()
        
        # 使用PIL处理图片
        image = Image.open(io.BytesIO(contents))
        
        # 调整图片大小（可选）
        max_size = (1024, 1024)
        image.thumbnail(max_size)
        
        # 保存处理后的图片
        image.save(file_path)
        
        # 生成URL路径
        image_url = f"/uploads/diet/{current_user.id}/{unique_filename}"
        
        # TODO: 这里可以添加食物识别功能
        
        return {
            "image_url": image_url,
            "filename": unique_filename,
            "size": len(contents)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传图片失败: {str(e)}"
        ) 