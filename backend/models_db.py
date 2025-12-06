from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base
import enum
from datetime import datetime

# Enums
class SourceType(str, enum.Enum):
    CSV = "CSV"
    SCADA = "SCADA"

# Models

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    subscription_plan = Column(String, default="Free")

    sensors = relationship("Sensor", back_populates="organization")

class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(String, primary_key=True, index=True) # Hardware ID (e.g., 'pH-01')
    org_id = Column(Integer, ForeignKey("organizations.id"))
    name = Column(String)
    location = Column(String)
    source_type = Column(Enum(SourceType), default=SourceType.CSV)
    config = Column(JSON, nullable=True) # For SCADA IP/Protocol details

    organization = relationship("Organization", back_populates="sensors")
    readings = relationship("SensorReading", back_populates="sensor")
    analyses = relationship("AnalysisResultDB", back_populates="sensor")

class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sensor_id = Column(String, ForeignKey("sensors.id"), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    value = Column(Float, nullable=False)

    sensor = relationship("Sensor", back_populates="readings")

class AnalysisResultDB(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sensor_id = Column(String, ForeignKey("sensors.id"), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    health_score = Column(Float)
    metrics = Column(JSON) # Stores bias, slope, hysteresis curves, etc.
    diagnosis = Column(Text)
    recommendation = Column(Text)

    sensor = relationship("Sensor", back_populates="analyses")
