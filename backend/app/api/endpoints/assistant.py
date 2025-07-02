from typing import Any, List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.deps import get_current_user, get_db
from app.db.models import User, Conversation, Message
from app.models.assistant import (
    ConversationCreate, ConversationUpdate, Conversation as ConversationSchema,
    MessageCreate, Message as MessageSchema, MessageRoleEnum,
    AssistantResponse
)
from app.services.assistant import (
    create_conversation, get_conversation, get_user_conversations,
    update_conversation, delete_conversation, create_message,
    get_conversation_messages, generate_assistant_response
)

router = APIRouter()


@router.post("/conversations", response_model=ConversationSchema)
def create_new_conversation(
    conv_in: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    创建新对话
    """
    # 确保只能为自己创建对话
    if conv_in.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能为自己创建对话"
        )
    
    return create_conversation(db=db, conv_in=conv_in)


@router.get("/conversations", response_model=List[ConversationSchema])
def read_conversations(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取当前用户的所有对话
    """
    return get_user_conversations(db=db, user_id=current_user.id, skip=skip, limit=limit)


@router.get("/conversations/{conversation_id}", response_model=ConversationSchema)
def read_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取单个对话
    """
    conversation = get_conversation(db=db, conversation_id=conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )
    
    # 确保只能查看自己的对话
    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此对话"
        )
    
    return conversation


@router.put("/conversations/{conversation_id}", response_model=ConversationSchema)
def update_conversation_title(
    conversation_id: str,
    conv_in: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    更新对话标题
    """
    conversation = get_conversation(db=db, conversation_id=conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )
    
    # 确保只能更新自己的对话
    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权更新此对话"
        )
    
    return update_conversation(db=db, conversation_id=conversation_id, conv_in=conv_in)


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation_endpoint(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """
    删除对话
    """
    conversation = get_conversation(db=db, conversation_id=conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )
    
    # 确保只能删除自己的对话
    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此对话"
        )
    
    delete_conversation(db=db, conversation_id=conversation_id)


@router.post("/messages", response_model=MessageSchema)
def create_new_message(
    message_in: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    创建新消息
    """
    # 检查对话是否存在
    conversation = get_conversation(db=db, conversation_id=message_in.conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )
    
    # 确保只能在自己的对话中发送消息
    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权在此对话中发送消息"
        )
    
    # 创建消息并获取助手回复
    return create_message(db=db, message_in=message_in)


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageSchema])
def read_messages(
    conversation_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取对话的所有消息
    """
    # 检查对话是否存在
    conversation = get_conversation(db=db, conversation_id=conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )
    
    # 确保只能查看自己的对话消息
    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此对话的消息"
        )
    
    return get_conversation_messages(db=db, conversation_id=conversation_id, skip=skip, limit=limit)


# 添加简化的聊天API端点
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    message_id: str
    conversation_id: str
    sources: Optional[List[Dict[str, Any]]] = None

@router.post("/chat", response_model=ChatResponse)
def chat_with_assistant(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    与助手聊天的简化API
    """
    conversation_id = request.conversation_id
    
    # 如果没有提供对话ID，创建新对话
    if not conversation_id:
        # 使用消息的前20个字符作为对话标题
        title = request.message[:20] + "..." if len(request.message) > 20 else request.message
        conv_in = ConversationCreate(user_id=current_user.id, title=title)
        conversation = create_conversation(db=db, conv_in=conv_in)
        conversation_id = conversation.id
    else:
        # 验证对话存在且属于当前用户
        conversation = get_conversation(db=db, conversation_id=conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="对话不存在"
            )
        if conversation.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此对话"
            )
    
    # 创建用户消息
    message_in = MessageCreate(
        conversation_id=conversation_id,
        content=request.message,
        role=MessageRoleEnum.USER
    )
    
    # 保存用户消息并获取助手回复
    assistant_message = create_message(db=db, message_in=message_in)
    
    # 返回响应
    sources = None
    if assistant_message.message_metadata and "sources" in assistant_message.message_metadata:
        sources = assistant_message.message_metadata["sources"]
    
    return ChatResponse(
        message=assistant_message.content,
        message_id=assistant_message.id,
        conversation_id=conversation_id,
        sources=sources
    )


@router.get("/history", response_model=List[MessageSchema])
def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取最近的聊天历史
    """
    # 获取用户最近的对话
    conversations = get_user_conversations(db=db, user_id=current_user.id, skip=0, limit=1)
    
    if not conversations:
        return []
    
    # 获取最近对话的消息
    return get_conversation_messages(db=db, conversation_id=conversations[0].id, skip=0, limit=50)


@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
def clear_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """
    清空聊天历史
    """
    # 获取用户所有对话
    conversations = get_user_conversations(db=db, user_id=current_user.id)
    
    # 删除所有对话
    for conversation in conversations:
        delete_conversation(db=db, conversation_id=conversation.id) 