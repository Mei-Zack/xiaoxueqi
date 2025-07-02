from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request
from fastapi.responses import StreamingResponse
from typing import List, Dict, Optional, Any
from pydantic import BaseModel
import json
import asyncio

from app.api.deps import get_current_user
from app.ml.ollama_service import ollama_service
from app.models.user import User

router = APIRouter()

# 请求模型
class GenerateRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    system: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2000

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    model: Optional[str] = None
    system: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2000

class ModelRequest(BaseModel):
    model_name: str

# API路由
@router.get("/models", summary="获取可用模型列表")
async def list_models():
    """获取所有可用的模型列表"""
    try:
        models = await ollama_service.list_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models/{model_name}", summary="获取模型信息")
async def get_model_info(model_name: str):
    """获取指定模型的详细信息"""
    try:
        model_info = await ollama_service.get_model_info(model_name)
        return model_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate", summary="生成文本")
async def generate_text(request: GenerateRequest):
    """生成文本响应"""
    try:
        response = await ollama_service.generate(
            prompt=request.prompt,
            model=request.model,
            system=request.system,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/generate", summary="生成文本(GET方法)")
async def generate_text_get(
    prompt: Optional[str] = "你好，请介绍一下自己",
    model: Optional[str] = None,
    system: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2000
):
    """使用GET方法生成文本响应"""
    try:
        response = await ollama_service.generate(
            prompt=prompt,
            model=model,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", summary="聊天对话")
async def chat(request: ChatRequest):
    """多轮对话"""
    try:
        # 打印请求数据用于调试
        print(f"Ollama聊天请求: model={request.model}, messages数量={len(request.messages)}, system={request.system is not None}")
        
        response = await ollama_service.chat(
            messages=request.messages,
            model=request.model,
            system=request.system,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        # 打印响应数据用于调试
        print(f"Ollama聊天响应: {response}")
        
        return response
    except Exception as e:
        print(f"Ollama聊天异常: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat", summary="聊天对话(GET方法)")
async def chat_get(
    message: Optional[str] = "你好，请介绍一下自己",
    model: Optional[str] = None,
    system: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2000
):
    """使用GET方法进行单轮对话"""
    try:
        messages = [{"role": "user", "content": message}]
        response = await ollama_service.chat(
            messages=messages,
            model=model,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate/stream", summary="流式生成文本")
async def stream_generate(request: GenerateRequest):
    """流式生成文本响应"""
    try:
        async def generate():
            async for chunk in ollama_service.stream_generate(
                prompt=request.prompt,
                model=request.model,
                system=request.system,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            ):
                yield f"data: {json.dumps(chunk)}\n\n"
            yield "data: [DONE]\n\n"
            
        return StreamingResponse(generate(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", summary="检查Ollama服务健康状态")
async def health_check():
    """检查Ollama服务是否正常运行"""
    try:
        models = await ollama_service.list_models()
        return {"status": "ok", "models_count": len(models)}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Ollama服务不可用: {str(e)}") 