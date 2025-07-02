from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, get_current_active_superuser
from app.db.models import User, KnowledgeBase
from app.models.assistant import KnowledgeBaseCreate, KnowledgeBaseUpdate
from app.services.assistant import (
    create_knowledge_base_entry, get_knowledge_base_entry, 
    get_knowledge_base_entries, update_knowledge_base_entry,
    delete_knowledge_base_entry
)

router = APIRouter()


@router.post("", response_model=dict)
def create_entry(
    entry_in: KnowledgeBaseCreate,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    创建新的知识库条目（仅管理员）
    """
    entry = create_knowledge_base_entry(db=db, entry_in=entry_in)
    
    return {
        "id": entry.id,
        "title": entry.title,
        "message": "知识库条目创建成功"
    }


@router.get("", response_model=List[dict])
def read_entries(
    skip: int = 0,
    limit: int = 100,
    tag: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取知识库条目列表
    """
    entries = get_knowledge_base_entries(db=db, skip=skip, limit=limit, tag=tag)
    
    # 转换为响应格式
    result = []
    for entry in entries:
        result.append({
            "id": entry.id,
            "title": entry.title,
            "source": entry.source,
            "tags": entry.tags,
            "created_at": entry.created_at,
            "updated_at": entry.updated_at
        })
    
    return result


@router.get("/{entry_id}", response_model=dict)
def read_entry(
    entry_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取单个知识库条目
    """
    entry = get_knowledge_base_entry(db=db, entry_id=entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库条目不存在"
        )
    
    return {
        "id": entry.id,
        "title": entry.title,
        "content": entry.content,
        "source": entry.source,
        "tags": entry.tags,
        "created_at": entry.created_at,
        "updated_at": entry.updated_at
    }


@router.put("/{entry_id}", response_model=dict)
def update_entry(
    entry_id: str,
    entry_in: KnowledgeBaseUpdate,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    更新知识库条目（仅管理员）
    """
    entry = update_knowledge_base_entry(db=db, entry_id=entry_id, entry_in=entry_in)
    
    return {
        "id": entry.id,
        "title": entry.title,
        "message": "知识库条目更新成功"
    }


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(
    entry_id: str,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
) -> None:
    """
    删除知识库条目（仅管理员）
    """
    delete_knowledge_base_entry(db=db, entry_id=entry_id)


@router.get("/search/{query}", response_model=List[dict])
def search_knowledge(
    query: str,
    limit: int = Query(3, ge=1, le=10),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    搜索知识库
    """
    # 直接从数据库搜索而不是使用向量数据库
    # 简单的基于关键字的模糊搜索
    entries = db.query(KnowledgeBase).filter(
        KnowledgeBase.content.ilike(f"%{query}%") | 
        KnowledgeBase.title.ilike(f"%{query}%")
    ).limit(limit).all()
    
    results = []
    for entry in entries:
        results.append({
            "id": entry.id,
            "title": entry.title,
            "content": entry.content,
            "score": 1.0  # 默认评分
        })
    
    return results 