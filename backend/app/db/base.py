from sqlalchemy import Column, String, Boolean, DateTime, Float, Enum, ForeignKey, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    gender = Column(Enum("male", "female", "other", name="gender_enum"), nullable=True)
    birth_date = Column(DateTime, nullable=True)
    diabetes_type = Column(
        Enum("type1", "type2", "gestational", "prediabetes", "other", name="diabetes_type_enum"),
        nullable=True
    )
    diagnosis_date = Column(DateTime, nullable=True)
    height = Column(Float, nullable=True)  # 身高，单位cm
    weight = Column(Float, nullable=True)  # 体重，单位kg
    phone = Column(String(20), nullable=True)
    avatar = Column(String(255), nullable=True)
    target_glucose_min = Column(Float, nullable=True)  # 目标血糖下限，单位mmol/L
    target_glucose_max = Column(Float, nullable=True)  # 目标血糖上限，单位mmol/L
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联
    glucose_records = relationship("GlucoseRecord", back_populates="user")
    diet_records = relationship("DietRecord", back_populates="user")
    health_records = relationship("HealthRecord", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="user")


class GlucoseRecord(Base):
    __tablename__ = "glucose_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    value = Column(Float, nullable=False)  # 血糖值，单位mmol/L
    measured_at = Column(DateTime, nullable=False, default=func.now())
    measurement_type = Column(
        Enum("fasting", "before_meal", "after_meal", "before_sleep", "other", name="measurement_type_enum"),
        nullable=False
    )
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联
    user = relationship("User", back_populates="glucose_records")


class DietRecord(Base):
    __tablename__ = "diet_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    meal_type = Column(
        Enum("breakfast", "lunch", "dinner", "snack", name="meal_type_enum"),
        nullable=False
    )
    food_name = Column(String(255), nullable=False)
    carbs = Column(Float, nullable=True)  # 碳水化合物，单位g
    protein = Column(Float, nullable=True)  # 蛋白质，单位g
    fat = Column(Float, nullable=True)  # 脂肪，单位g
    calories = Column(Float, nullable=True)  # 卡路里，单位kcal
    glycemic_index = Column(Float, nullable=True)  # 血糖指数
    portion = Column(Float, nullable=True)  # 份量，单位g
    eaten_at = Column(DateTime, nullable=False, default=func.now())
    notes = Column(Text, nullable=True)
    image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联
    user = relationship("User", back_populates="diet_records")


class HealthRecord(Base):
    __tablename__ = "health_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    record_type = Column(
        Enum("weight", "blood_pressure", "exercise", "medication", "sleep", "other", name="health_record_type_enum"),
        nullable=False
    )
    value = Column(Float, nullable=True)  # 数值，如体重kg、运动时长min等
    value2 = Column(Float, nullable=True)  # 辅助数值，如血压的舒张压
    text_value = Column(Text, nullable=True)  # 文本值，如药物名称
    recorded_at = Column(DateTime, nullable=False, default=func.now())
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联
    user = relationship("User", back_populates="health_records")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    role = Column(Enum("user", "assistant", name="message_role_enum"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())

    # 关联
    user = relationship("User", back_populates="chat_messages")


class KnowledgeArticle(Base):
    __tablename__ = "knowledge_articles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    tags = Column(String(255), nullable=True)  # 以逗号分隔的标签
    author = Column(String(100), nullable=True)
    source = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now()) 