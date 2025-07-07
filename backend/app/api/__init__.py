from fastapi import APIRouter
from app.api.endpoints import users, health, glucose, diet, assistant, knowledge, ollama, glucose_monitor

router = APIRouter()

router.include_router(users.router, prefix="/users", tags=["用户"])
router.include_router(health.router, prefix="/health", tags=["健康记录"])
router.include_router(glucose.router, prefix="/glucose", tags=["血糖记录"])
router.include_router(diet.router, prefix="/diet", tags=["饮食记录"])
router.include_router(assistant.router, prefix="/assistant", tags=["智能助手"])
router.include_router(knowledge.router, prefix="/knowledge", tags=["知识库"])
router.include_router(ollama.router, prefix="/ollama", tags=["Ollama大模型"])
router.include_router(glucose_monitor.router, prefix="/glucose-monitor", tags=["血糖监测"]) 