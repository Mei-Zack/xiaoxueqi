from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from typing import List

from app.api import router as api_router
from app.core.config import settings
from app.ml.llm_service import llm_service
from app.core.scheduler import glucose_scheduler

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="糖尿病智能健康助理API",
    description="基于大模型的糖尿病智能健康助理系统API",
    version="0.1.0",
)

# 配置CORS - 明确列出所有允许的来源，因为withCredentials要求不能使用通配符
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost",
        "http://127.0.0.1"
    ],
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头信息
    expose_headers=["Content-Disposition"],
    max_age=3600,  # 预检请求的缓存时间
)

# 注册路由
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "糖尿病智能健康助理API服务",
        "docs_url": "/docs",
        "status": "running"
    }

@app.on_event("startup")
async def startup_event():
    """应用启动时执行的操作"""
    logger.info("正在初始化应用...")
    
    # 禁用向量数据库初始化
    logger.info("向量数据库初始化已禁用，以提高启动速度")
    
    # 禁用模型预加载
    logger.info("模型预加载已禁用，将在首次使用时按需加载")
    
    # 启动血糖监测调度器
    logger.info("正在启动血糖监测调度器...")
    glucose_scheduler.start()
    logger.info("血糖监测调度器已启动")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行的操作"""
    logger.info("应用正在关闭...")
    
    # 停止血糖监测调度器
    logger.info("正在停止血糖监测调度器...")
    glucose_scheduler.stop()
    logger.info("血糖监测调度器已停止")

if __name__ == "__main__":
    import asyncio
    
    async def start_app():
        config = uvicorn.Config("main:app", host="0.0.0.0", port=8000, reload=True)
        server = uvicorn.Server(config)
        await server.serve()
        
    asyncio.run(start_app()) 