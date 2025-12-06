import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, desc
from backend.database import get_db, engine
from backend.models_db import Sensor, SensorReading, AnalysisResultDB, Organization, SourceType
from backend.models import SensorDataInput, AnalysisResult, AnalysisMetrics, SyntheticRequest, ReportRequest
from backend.analysis import SensorAnalyzer
import numpy as np
import logging
import csv
import codecs
from datetime import datetime
from contextlib import asynccontextmanager

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("backend.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Lifespan Manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up QorSense Backend...")
    yield
    # Shutdown
    logger.info("Shutting down...")
    await engine.dispose()

app = FastAPI(title="QorSense v1 API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

analyzer = SensorAnalyzer()

# --- Helper Functions ---
async def save_analysis_result(db: AsyncSession, sensor_id: str, result: AnalysisResult):
    """Save analysis result to database asynchronously."""
    try:
        db_result = AnalysisResultDB(
            sensor_id=sensor_id,
            timestamp=datetime.fromisoformat(result.timestamp),
            health_score=result.health_score,
            metrics=result.metrics.dict(),
            diagnosis=result.diagnosis,
            recommendation=result.recommendation
        )
        db.add(db_result)
        await db.commit()
    except Exception as e:
        logger.error(f"Failed to save analysis result: {e}")

async def run_background_analysis(sensor_id: str, db_session_factory):
    """Background task to run analysis on recent data."""
    async with db_session_factory() as db:
        logger.info(f"Running background analysis for {sensor_id}")
        # Fetch last 100 readings
        stmt = select(SensorReading).where(SensorReading.sensor_id == sensor_id).order_by(desc(SensorReading.timestamp)).limit(100)
        result = await db.execute(stmt)
        readings = result.scalars().all()
        
        if len(readings) < 10:
            logger.info("Not enough data for analysis")
            return

        # Prepare values (reverse order to be chronological)
        values = [r.value for r in reversed(readings)]
        
        # Analyze
        try:
            # We construct a synthetic input object to reuse existing logic
            # Note: This duplicates some logic from /analyze endpoint, could be refactored further
            clean_data = analyzer.preprocessing(values)
            bias = analyzer.calc_bias(clean_data)
            slope = analyzer.calc_slope(clean_data)
            noise_std = float(np.std(clean_data))
            snr_db = analyzer.calc_snr_db(clean_data)
            hysteresis, hyst_x, hyst_y = analyzer.calc_hysteresis(clean_data)
            hurst, hurst_r2, dfa_scales, dfa_flucts = analyzer.calc_dfa(clean_data)
            
            metrics_dict = {
                "bias": bias, "slope": slope, "noise_std": noise_std, "snr_db": snr_db,
                "hysteresis": hysteresis, "hysteresis_x": hyst_x, "hysteresis_y": hyst_y,
                "hurst": hurst, "hurst_r2": hurst_r2, "dfa_scales": dfa_scales, "dfa_fluctuations": dfa_flucts
            }
            health = analyzer.get_health_score(metrics_dict)
            rul = analyzer.calc_rul(clean_data, slope)
            
            analysis_result = AnalysisResult(
                sensor_id=sensor_id,
                timestamp=datetime.now().isoformat(),
                health_score=health["score"],
                status=health["status"],
                diagnosis=health["diagnosis"],
                metrics=AnalysisMetrics(**metrics_dict),
                flags=health["flags"],
                recommendation=health["recommendation"],
                prediction=rul
            )
            
            await save_analysis_result(db, sensor_id, analysis_result)
            logger.info(f"Background analysis completed for {sensor_id}")
            
        except Exception as e:
            logger.error(f"Background analysis error: {e}")

# --- Endpoints ---

@app.post("/upload-csv")
async def upload_csv(
    file: UploadFile = File(...), 
    sensor_id: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Import CSV data for a specific sensor."""
    try:
        reader = csv.reader(codecs.iterdecode(file.file, 'utf-8'))
        header = next(reader, None) # Skip header if exists
        
        readings_to_insert = []
        for row in reader:
            if not row: continue
            
            # Simple heuristic parsing
            ts = datetime.now()
            val = 0.0
            
            try:
                if len(row) >= 3:
                     # Assume: sensor_id, timestamp, value
                     # We ignore row[0] sensor_id and use the Form param to be safe, or cross-check
                     ts_str = row[1]
                     val = float(row[2])
                     try:
                        ts = datetime.fromisoformat(ts_str)
                     except:
                        pass
                elif len(row) == 2:
                    # Assume: timestamp, value
                    ts_str = row[0]
                    val = float(row[1])
                    try:
                        ts = datetime.fromisoformat(ts_str)
                    except:
                        pass
                else:
                    # Assume: value
                    val = float(row[0])
                
                readings_to_insert.append({"sensor_id": sensor_id, "timestamp": ts, "value": val})
            except ValueError:
                continue # Skip bad rows

        if readings_to_insert:
             await db.execute(insert(SensorReading), readings_to_insert)
             await db.commit()
             
        return {"message": f"Successfully imported {len(readings_to_insert)} readings for {sensor_id}"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stream-data")
async def stream_data(
    data: dict, # Expected {sensor_id: str, value: float, timestamp: str (opt)}
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Stream a single data point and trigger analysis."""
    if "sensor_id" not in data or "value" not in data:
         raise HTTPException(status_code=400, detail="Missing sensor_id or value")
    
    sensor_id = data["sensor_id"]
    value = float(data["value"])
    ts = datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now()
    
    # Insert Reading
    reading = SensorReading(sensor_id=sensor_id, value=value, timestamp=ts)
    db.add(reading)
    await db.commit()
    
    # Trigger Analysis
    from backend.database import AsyncSessionLocal # Need factory for background task
    background_tasks.add_task(run_background_analysis, sensor_id, AsyncSessionLocal)
    
    return {"status": "received", "sensor_id": sensor_id}

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_sensor(data: SensorDataInput, db: AsyncSession = Depends(get_db)):
    """Analyze sensor data. Supports ad-hoc (values) or DB-fetch (sensor_id)."""
    logger.info(f"Analysis request for {data.sensor_id}")
    
    values = data.values
    
    # If no values provided, try to fetch from DB
    if not values or len(values) == 0:
        window_size = 100
        if data.config:
            # Check if it's a dict or object (Pydantic model)
            if isinstance(data.config, dict):
                window_size = data.config.get("window_size", 100)
            else:
                window_size = getattr(data.config, "window_size", 100) or 100

        stmt = select(SensorReading).where(SensorReading.sensor_id == data.sensor_id).order_by(desc(SensorReading.timestamp)).limit(window_size)
        result = await db.execute(stmt)
        readings = result.scalars().all()
        values = [r.value for r in reversed(readings)]
        
        if len(values) < 5:
             # Fallback to empty/mock or error? 
             # If completely empty, maybe user wants synthetic? But user is asking for DB.
             # Return error if no data found in DB and no data provided.
             raise HTTPException(status_code=404, detail="No data found for this sensor in database and no values provided.")

    current_analyzer = SensorAnalyzer(config=data.config) if data.config else analyzer
    
    try:
        # Preprocessing
        clean_data = current_analyzer.preprocessing(values)
        
        # Calculate Metrics
        bias = current_analyzer.calc_bias(clean_data)
        slope = current_analyzer.calc_slope(clean_data)
        noise_std = float(np.std(clean_data))
        snr_db = current_analyzer.calc_snr_db(clean_data)
        hysteresis, hyst_x, hyst_y = current_analyzer.calc_hysteresis(clean_data)
        hurst, hurst_r2, dfa_scales, dfa_flucts = current_analyzer.calc_dfa(clean_data)
        
        metrics_dict = {
            "bias": bias, "slope": slope, "noise_std": noise_std, "snr_db": snr_db,
            "hysteresis": hysteresis, "hysteresis_x": hyst_x, "hysteresis_y": hyst_y,
            "hurst": hurst, "hurst_r2": hurst_r2, "dfa_scales": dfa_scales, "dfa_fluctuations": dfa_flucts
        }
        
        health = current_analyzer.get_health_score(metrics_dict)
        rul_prediction = current_analyzer.calc_rul(clean_data, slope)
        
        result_obj = AnalysisResult(
            sensor_id=data.sensor_id,
            timestamp=datetime.now().isoformat(),
            health_score=health["score"],
            status=health["status"],
            diagnosis=health["diagnosis"],
            metrics=AnalysisMetrics(**metrics_dict),
            flags=health["flags"],
            recommendation=health["recommendation"],
            prediction=rul_prediction
        )
        
        # Save result to DB only if we fetched from DB? Or always?
        # Let's save it if it's not a simulation (length > 0)
        # Assuming if we're calling analyze explicitly, we might want to save it.
        await save_analysis_result(db, data.sensor_id, result_obj)
        
        return result_obj

    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-synthetic")
async def generate_synthetic(request: SyntheticRequest):
    t = np.linspace(0, 10, request.length)
    base_signal = np.sin(t) * 10 
    
    if request.type == "Normal":
        noise = np.random.normal(0, 0.5, request.length)
        data = base_signal + noise
        
    elif request.type == "Drifting":
        noise = np.random.normal(0, 0.5, request.length)
        drift = np.linspace(0, 5, request.length)
        data = base_signal + noise + drift
        
    elif request.type == "Noisy":
        noise = np.random.normal(0, 3.0, request.length)
        data = base_signal + noise
        
    elif request.type == "Oscillation":
        oscillation = np.sin(t * 10) * 5
        noise = np.random.normal(0, 0.2, request.length)
        data = base_signal + oscillation + noise
    else:
        raise HTTPException(status_code=400, detail="Invalid type")
        
    return {"data": data.tolist(), "timestamps": t.tolist()}

@app.get("/")
async def root():
    return {"message": "QorSense v1 Backend Running (SaaS Database Enabled)"}

@app.post("/report")
async def generate_report(request: ReportRequest):
    try:
        from backend.report_gen import create_pdf, generate_chart_image
        from fastapi.responses import FileResponse
        
        chart_path = None
        if request.data:
            chart_path = generate_chart_image(request.data)
        
        metrics_data = request.metrics.dict()
        metrics_data["sensor_id"] = request.sensor_id
        metrics_data["flags"] = request.flags
        metrics_data["recommendation"] = request.recommendation
        
        pdf_path = create_pdf(
            metrics=metrics_data,
            diagnosis=request.diagnosis,
            health_score=request.health_score,
            chart_image_path=chart_path
        )
        
        return FileResponse(pdf_path, media_type='application/pdf', filename=f"report_{request.sensor_id}.pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

