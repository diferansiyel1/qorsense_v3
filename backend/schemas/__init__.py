"""
Pydantic Schemas Package.

This package contains all Pydantic schemas for request/response validation.

Modules:
- common: Pagination and shared schemas
- sensor: Sensor data ingestion schemas with strict validation
"""

from backend.schemas.common import PaginationParams, PaginatedResponse
from backend.schemas.sensor import (
    # Enumerations
    SourceType,
    SensorStatus,
    # Reading schemas
    SensorReadingBase,
    SensorReadingCreate,
    SensorReadingBulk,
    # Sensor management
    SensorCreate,
    SensorResponse,
    # CSV Import
    CSVImportConfig,
    CSVImportResult,
    CSVValidationError,
)

__all__ = [
    # Common
    "PaginationParams",
    "PaginatedResponse",
    # Enums
    "SourceType",
    "SensorStatus",
    # Readings
    "SensorReadingBase",
    "SensorReadingCreate",
    "SensorReadingBulk",
    # Sensors
    "SensorCreate",
    "SensorResponse",
    # CSV Import
    "CSVImportConfig",
    "CSVImportResult",
    "CSVValidationError",
]
