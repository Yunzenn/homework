from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, validator, Field


class WaterQualityRecord(BaseModel):
    """水质记录数据模型（不映射到数据库，用于数据验证）"""
    record_id: Optional[int] = None
    point_id: str = Field(..., description="监测点ID")
    date: str = Field(..., description="日期，格式：YYYY-MM-DD")
    time: str = Field(..., description="时间，格式：HH:MM")
    chlorine: float = Field(..., ge=0, description="余氯 (mg/L)")
    conductivity: float = Field(..., ge=0, description="电导率 (µS/cm)")
    ph: float = Field(..., ge=0, le=14, description="pH值")
    orp: float = Field(..., description="氧化还原电位 (mV)")
    turbidity: float = Field(..., ge=0, description="浊度 (NTU)")
    create_time: Optional[str] = None
    
    @validator('point_id')
    def validate_point_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('监测点ID不能为空')
        return v.strip()
    
    @validator('date')
    def validate_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('日期格式错误，应为YYYY-MM-DD')
    
    @validator('time')
    def validate_time(cls, v):
        try:
            datetime.strptime(v, '%H:%M')
            return v
        except ValueError:
            raise ValueError('时间格式错误，应为HH:MM')
    
    @validator('ph')
    def validate_ph(cls, v):
        if not (0 <= v <= 14):
            raise ValueError('pH值必须在0-14之间')
        return round(v, 2)
    
    @validator('chlorine', 'conductivity', 'turbidity')
    def validate_positive(cls, v):
        if v < 0:
            raise ValueError('数值不能为负数')
        return round(v, 2)
    
    @validator('orp')
    def validate_orp(cls, v):
        return round(v, 2)
    
    class Config:
        schema_extra = {
            "example": {
                "point_id": "监测点001",
                "date": "2024-01-15",
                "time": "09:30",
                "chlorine": 2.5,
                "conductivity": 450.0,
                "ph": 7.2,
                "orp": 650.0,
                "turbidity": 1.8
            }
        }


class AlertThreshold(BaseModel):
    """报警阈值配置"""
    chlorine: Dict[str, float] = {"min": 0.5, "max": 4.0}
    conductivity: Dict[str, float] = {"max": 1000}
    ph: Dict[str, float] = {"min": 6.5, "max": 8.5}
    orp: Dict[str, float] = {"min": 400}
    turbidity: Dict[str, float] = {"max": 5.0}
