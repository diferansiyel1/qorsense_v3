from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, JSON, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base
import enum
from datetime import datetime

# Enums
class SourceType(str, enum.Enum):
    CSV = "CSV"
    SCADA = "SCADA"
    IoT = "IoT"


class UserRole(str, enum.Enum):
    """User role enumeration."""
    VIEWER = "viewer"
    OPERATOR = "operator"
    ENGINEER = "engineer"
    ADMIN = "admin"


# Models

class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    subscription_plan = Column(String, default="Free")

    sensors = relationship("Sensor", back_populates="organization")
    users = relationship("User", back_populates="organization")

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
    status = Column(String) # 'Normal', 'Warning', 'Critical', 'Unknown'
    metrics = Column(JSON) # Stores bias, slope, hysteresis curves, etc.
    diagnosis = Column(Text)
    recommendation = Column(Text)

    sensor = relationship("Sensor", back_populates="analyses")
