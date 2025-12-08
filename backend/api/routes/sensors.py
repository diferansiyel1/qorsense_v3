"""
Sensor Management Routes

Handles sensor CRUD operations, data ingestion, and history retrieval.
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, desc, func
from backend.database import get_db, AsyncSessionLocal
from backend.models_db import Sensor, SensorReading, AnalysisResultDB, SourceType
from backend.models import SensorCreate, SensorResponse, AnalysisResult, AnalysisMetrics
from backend.schemas.common import PaginationParams, PaginatedResponse
from datetime import datetime
import logging
import csv
import codecs
import uuid
import math

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sensors", tags=["Sensors"])


@router.get("", response_model=PaginatedResponse[SensorResponse])
async def get_sensors(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    List sensors with pagination.
    """
    # Count total
    count_stmt = select(func.count()).select_from(Sensor)
    total = await db.scalar(count_stmt)
    
    # Get items
    stmt = select(Sensor).offset((pagination.page - 1) * pagination.size).limit(pagination.size)
    result = await db.execute(stmt)
    sensors = result.scalars().all()
    
    sensor_responses = []
    for s in sensors:
        stmt = (
            select(AnalysisResultDB)
            .where(AnalysisResultDB.sensor_id == s.id)
            .order_by(desc(AnalysisResultDB.timestamp))
            .limit(1)
        )
        res = await db.execute(stmt)
        latest_analysis = res.scalar_one_or_none()
        
        response = SensorResponse(
            id=s.id,
            name=s.name,
            location=s.location,
            source_type=s.source_type,
            organization_id=s.org_id,
            latest_health_score=latest_analysis.health_score if latest_analysis else 100.0,
            latest_status=latest_analysis.status if latest_analysis else "Normal",
            latest_analysis_timestamp=latest_analysis.timestamp if latest_analysis else None
        )
        sensor_responses.append(response)
        
    return PaginatedResponse(
        items=sensor_responses,
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=math.ceil(total / pagination.size)
    )


@router.post("", response_model=SensorResponse)
async def create_sensor(sensor: SensorCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new sensor.
    """
    new_id = str(uuid.uuid4())[:8]
    
    db_sensor = Sensor(
        id=new_id,
        name=sensor.name,
        location=sensor.location,
        source_type=SourceType(sensor.source_type),
        org_id=sensor.organization_id
    )
    db.add(db_sensor)
    await db.commit()
    await db.refresh(db_sensor)
    
    logger.info(f"Created sensor: {new_id} - {sensor.name}")
    return SensorResponse(
        id=db_sensor.id,
        name=db_sensor.name,
        location=db_sensor.location,
        source_type=db_sensor.source_type,
        organization_id=db_sensor.org_id,
        latest_health_score=100.0,
        latest_status="Normal",
        latest_analysis_timestamp=None
    )


@router.get("/{sensor_id}/history", response_model=PaginatedResponse[AnalysisResult])
async def get_sensor_history(
    sensor_id: str,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated analysis history for a sensor.
    """
    # Count total
    count_stmt = (
        select(func.count())
        .select_from(AnalysisResultDB)
        .where(AnalysisResultDB.sensor_id == sensor_id)
    )
    total = await db.scalar(count_stmt)
    
    # Get items
    stmt = (
        select(AnalysisResultDB)
        .where(AnalysisResultDB.sensor_id == sensor_id)
        .order_by(desc(AnalysisResultDB.timestamp))
        .offset((pagination.page - 1) * pagination.size)
        .limit(pagination.size)
    )
    result = await db.execute(stmt)
    history_db = result.scalars().all()
    
    history_pydantic = []
    for item in history_db:
        try:
            metrics_obj = AnalysisMetrics(**item.metrics)
            
            res = AnalysisResult(
                sensor_id=item.sensor_id,
                timestamp=item.timestamp.isoformat(),
                health_score=item.health_score,
                status=item.status,
                diagnosis=item.diagnosis,
                metrics=metrics_obj,
                flags=[],
                recommendation=item.recommendation
            )
            history_pydantic.append(res)
        except Exception as e:
            logger.error(f"Error converting history item {item.id}: {e}")
            continue
            
    return PaginatedResponse(
        items=history_pydantic,
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=math.ceil(total / pagination.size) if total else 0
    )


@router.post("/upload-csv")
async def upload_csv(
    file: UploadFile = File(...), 
    sensor_id: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Import CSV data for a specific sensor.
    
    CSV formats supported:
    - sensor_id, timestamp, value
    - timestamp, value  
    - value only (will use current timestamp)
    
    Args:
        file: CSV file upload
        sensor_id: Target sensor ID
        db: Database session
        
    Returns:
        dict: Import status message
    """
    try:
        reader = csv.reader(codecs.iterdecode(file.file, 'utf-8'))
        header = next(reader, None)  # Skip header if exists
        
        readings_to_insert = []
        for row in reader:
            if not row:
                continue
            
            ts = datetime.now()
            val = 0.0
            
            try:
                if len(row) >= 3:
                    # Assume: sensor_id, timestamp, value
                    ts_str = row[1]
                    val = float(row[2])
                    try:
                        ts = datetime.fromisoformat(ts_str)
                    except (ValueError, TypeError):
                        pass
                elif len(row) == 2:
                    # Assume: timestamp, value
                    ts_str = row[0]
                    val = float(row[1])
                    try:
                        ts = datetime.fromisoformat(ts_str)
                    except (ValueError, TypeError):
                        pass
                else:
                    # Assume: value only
                    val = float(row[0])
                
                readings_to_insert.append({
                    "sensor_id": sensor_id,
                    "timestamp": ts,
                    "value": val
                })
            except ValueError:
                # Skip bad rows
                continue

        if readings_to_insert:
            await db.execute(insert(SensorReading), readings_to_insert)
            await db.commit()
            logger.info(f"Imported {len(readings_to_insert)} readings for sensor {sensor_id}")
              
        return {
            "message": f"Successfully imported {len(readings_to_insert)} readings for {sensor_id}",
            "count": len(readings_to_insert)
        }
    except Exception as e:
        logger.error(f"CSV upload error: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream-data")
async def stream_data(
    data: dict,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Stream a single data point and trigger analysis.
    
    Args:
        data: Dictionary with sensor_id, value, and optional timestamp
        background_tasks: FastAPI background tasks
        db: Database session
        
    Returns:
        dict: Reception status
    """
    if "sensor_id" not in data or "value" not in data:
        raise HTTPException(status_code=400, detail="Missing sensor_id or value")
    
    sensor_id = data["sensor_id"]
    value = float(data["value"])
    ts = datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now()
    
    # Insert reading
    reading = SensorReading(sensor_id=sensor_id, value=value, timestamp=ts)
    db.add(reading)
    await db.commit()
    
    # Trigger background analysis
    from backend.api.routes.analytics import run_background_analysis
    background_tasks.add_task(run_background_analysis, sensor_id, AsyncSessionLocal)
    
    logger.info(f"Received data point for sensor {sensor_id}")
    return {"status": "received", "sensor_id": sensor_id, "timestamp": ts.isoformat()}
