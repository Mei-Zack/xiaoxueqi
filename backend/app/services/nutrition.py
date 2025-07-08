from typing import List, Optional, Dict, Any, Tuple
from fastapi import UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, desc, asc
from datetime import datetime, timedelta
import os
import uuid
from PIL import Image
import io
import math
import logging

from app.db.models import FoodNutrition
from app.models.nutrition import FoodNutritionCreate, FoodNutritionUpdate, FoodNutritionPage
from app.core.config import settings

logger = logging.getLogger(__name__)


def create_food_nutrition(db: Session, food_in: FoodNutritionCreate) -> FoodNutrition:
    """创建食物营养记录"""
    db_food = FoodNutrition(
        name_cn=food_in.name_cn,
        calories=food_in.calories,
        protein=food_in.protein,
        fat=food_in.fat,
        carbs=food_in.carbs,
        gi=food_in.gi,
        category=food_in.category,
        diabetes_index=food_in.diabetes_index,
        diabetes_friendly=food_in.diabetes_friendly,
        image_url=food_in.image_url
    )
    db.add(db_food)
    db.commit()
    db.refresh(db_food)
    return db_food


def get_food_nutrition(db: Session, food_id: int) -> Optional[FoodNutrition]:
    """获取单个食物营养记录"""
    return db.query(FoodNutrition).filter(FoodNutrition.id == food_id).first()


def get_food_nutrition_list(
    db: Session,
    page: int = 1,
    size: int = 20,
    category: Optional[str] = None,
    diabetes_friendly: Optional[int] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "asc"
) -> FoodNutritionPage:
    """获取食物营养记录列表"""
    query = db.query(FoodNutrition)
    
    # 应用过滤条件
    if category:
        query = query.filter(FoodNutrition.category == category)
        
    if diabetes_friendly is not None:
        query = query.filter(FoodNutrition.diabetes_friendly == diabetes_friendly)
        
    if search:
        search_term = f"%{search}%"
        query = query.filter(FoodNutrition.name_cn.ilike(search_term))
    
    # 应用排序
    if sort_by:
        if sort_by == "calories":
            order_column = FoodNutrition.calories
        elif sort_by == "protein":
            order_column = FoodNutrition.protein
        elif sort_by == "fat":
            order_column = FoodNutrition.fat
        elif sort_by == "carbs":
            order_column = FoodNutrition.carbs
        elif sort_by == "gi":
            order_column = FoodNutrition.gi
        else:
            order_column = FoodNutrition.id
            
        if sort_order == "desc":
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(asc(order_column))
    else:
        # 默认按ID排序
        query = query.order_by(FoodNutrition.id)
    
    # 计算总记录数和总页数
    total = query.count()
    pages = math.ceil(total / size) if total > 0 else 0
    
    # 分页
    skip = (page - 1) * size
    query = query.offset(skip).limit(size)
    
    items = query.all()
    
    # 由于移除了时间戳字段，这里直接返回items而不需要额外处理
    return FoodNutritionPage(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


def update_food_nutrition(
    db: Session,
    food_id: int,
    food_in: FoodNutritionUpdate
) -> Optional[FoodNutrition]:
    """更新食物营养记录"""
    db_food = get_food_nutrition(db, food_id)
    if not db_food:
        return None
    
    update_data = food_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_food, field, value)
    
    db.commit()
    db.refresh(db_food)
    return db_food


def delete_food_nutrition(db: Session, food_id: int) -> bool:
    """删除食物营养记录"""
    db_food = get_food_nutrition(db, food_id)
    if not db_food:
        return False
    
    db.delete(db_food)
    db.commit()
    return True


def import_food_nutrition_data(
    db: Session,
    items: List[FoodNutritionCreate]
) -> Tuple[int, int]:
    """批量导入食物营养数据"""
    imported_count = 0
    failed_count = 0
    
    for item in items:
        try:
            create_food_nutrition(db, item)
            imported_count += 1
        except Exception as e:
            logger.error(f"导入食物数据失败: {e}", exc_info=True)
            failed_count += 1
    
    return imported_count, failed_count


def get_food_by_category(
    db: Session,
    category: str,
    page: int = 1,
    size: int = 20
) -> FoodNutritionPage:
    """按分类获取食物列表"""
    return get_food_nutrition_list(db, page, size, category=category)


def get_all_categories(db: Session) -> List[str]:
    """获取所有食物分类"""
    result = db.query(FoodNutrition.category).distinct().all()
    return [r[0] for r in result]


def get_diabetes_friendly_foods(
    db: Session,
    page: int = 1,
    size: int = 20,
    category: Optional[str] = None
) -> FoodNutritionPage:
    """获取适合糖尿病患者的食物"""
    return get_food_nutrition_list(
        db, 
        page, 
        size, 
        category=category, 
        diabetes_friendly=1
    )


def get_low_gi_foods(
    db: Session,
    page: int = 1,
    size: int = 20,
    threshold: int = 55
) -> FoodNutritionPage:
    """获取低GI食物"""
    query = db.query(FoodNutrition).filter(
        FoodNutrition.gi.isnot(None),
        FoodNutrition.gi <= threshold
    )
    
    # 计算总记录数和总页数
    total = query.count()
    pages = math.ceil(total / size) if total > 0 else 0
    
    # 分页
    skip = (page - 1) * size
    query = query.offset(skip).limit(size)
    
    items = query.all()
    
    return FoodNutritionPage(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


def get_foods_by_gi_range(
    db: Session,
    min_gi: int = 0,
    max_gi: int = 100,
    page: int = 1,
    size: int = 20
) -> FoodNutritionPage:
    """根据血糖指数范围查询食物"""
    query = db.query(FoodNutrition).filter(
        FoodNutrition.gi.isnot(None),
        FoodNutrition.gi >= min_gi,
        FoodNutrition.gi <= max_gi
    )
    
    # 计算总记录数和总页数
    total = query.count()
    pages = math.ceil(total / size) if total > 0 else 0
    
    # 分页
    skip = (page - 1) * size
    query = query.offset(skip).limit(size)
    
    items = query.all()
    
    return FoodNutritionPage(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


def search_foods(
    db: Session,
    query: str,
    page: int = 1,
    size: int = 20
) -> FoodNutritionPage:
    """搜索食物"""
    return get_food_nutrition_list(db, page, size, search=query)


async def upload_food_image(file: UploadFile, food_id: int) -> Dict[str, Any]:
    """上传食物图片"""
    # 确保目录存在
    upload_dir = os.path.join(settings.STATIC_DIR, "uploads", "foods")
    os.makedirs(upload_dir, exist_ok=True)
    
    # 生成文件名
    file_ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    filename = f"food_{food_id}_{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(upload_dir, filename)
    
    # 读取和保存图片
    contents = await file.read()
    
    # 处理图片
    image = Image.open(io.BytesIO(contents))
    # 调整大小到合理尺寸，如果需要的话
    if max(image.size) > 1200:
        image.thumbnail((1200, 1200))
    
    # 保存图片
    image.save(file_path)
    
    # 返回相对路径
    relative_path = f"/uploads/foods/{filename}"
    
    return {
        "file_path": relative_path,
        "file_size": os.path.getsize(file_path)
    }


def delete_food_image(food_id: int, image_url: str) -> bool:
    """删除食物图片"""
    if not image_url:
        return False
    
    # 获取图片的绝对路径
    if image_url.startswith("/uploads/"):
        file_path = os.path.join(settings.STATIC_DIR, image_url[1:])
    else:
        return False
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        return False
    
    # 删除文件
    os.remove(file_path)
    return True 