from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class MeasurementTimeEnum(str, Enum):
    BEFORE_BREAKFAST = "before_breakfast"
    AFTER_BREAKFAST = "after_breakfast"
    BEFORE_LUNCH = "before_lunch"
    AFTER_LUNCH = "after_lunch"
    BEFORE_DINNER = "before_dinner"
    AFTER_DINNER = "after_dinner"
    BEFORE_SLEEP = "before_sleep"
    MIDNIGHT = "midnight"
    OTHER = "other"


class MeasurementMethodEnum(str, Enum):
    FINGER_STICK = "finger_stick"
    CONTINUOUS_MONITOR = "continuous_monitor"
    LAB_TEST = "lab_test"
    OTHER = "other"


class GlucoseBase(BaseModel):
    user_id: str
    value: float = Field(..., description="血糖值，单位mmol/L")
    measurement_time: MeasurementTimeEnum
    measurement_method: MeasurementMethodEnum = MeasurementMethodEnum.FINGER_STICK
    measured_at: datetime = Field(default_factory=datetime.now)
    notes: Optional[str] = None


class GlucoseCreate(GlucoseBase):
    pass


class GlucoseUpdate(BaseModel):
    value: Optional[float] = None
    measurement_time: Optional[MeasurementTimeEnum] = None
    measurement_method: Optional[MeasurementMethodEnum] = None
    measured_at: Optional[datetime] = None
    notes: Optional[str] = None


class Glucose(GlucoseBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class GlucoseStatistics(BaseModel):
    average: float
    max: float
    min: float
    count: int
    in_range_percentage: float
    high_percentage: float
    low_percentage: float
    period: str  # 统计周期，如"day", "week", "month" 