# 导入所有模型，确保它们被SQLAlchemy注册
from app.db.base_class import Base
from app.db.models import User, GlucoseRecord, DietRecord, HealthRecord, WeightRecord
from app.db.models import BloodPressureRecord, ExerciseRecord, MedicationRecord
from app.db.models import Conversation, Message, KnowledgeBase 