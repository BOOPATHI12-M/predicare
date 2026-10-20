from datetime import datetime, timezone
from enum import Enum
import math
import os
import random
from typing import Generator

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import Boolean, DateTime, Float, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


DATABASE_URL = os.getenv("PREDICARE_DATABASE_URL", "sqlite:///./predicare.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Risk(str, Enum):
    NORMAL = "NORMAL"
    ATTENTION = "ATTENTION"
    HIGH_RISK = "HIGH_RISK"


class Measurement(Base):
    __tablename__ = "measurements"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    heart_rate: Mapped[float] = mapped_column(Float)
    spo2: Mapped[float] = mapped_column(Float)
    temperature: Mapped[float] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(20), default="simulation")
    risk: Mapped[str] = mapped_column(String(20), default=Risk.NORMAL.value)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Baseline(Base):
    __tablename__ = "baselines"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    heart_rate: Mapped[float] = mapped_column(Float)
    spo2: Mapped[float] = mapped_column(Float)
    temperature: Mapped[float] = mapped_column(Float)
    measurement_count: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    severity: Mapped[str] = mapped_column(String(20))
    message: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)


class MeasurementIn(BaseModel):
    heart_rate: float = Field(gt=20, lt=250)
    spo2: float = Field(ge=50, le=100)
    temperature: float = Field(gt=20, lt=45)
    source: str = Field(default="device", pattern="^(device|simulation)$")


class BaselineOut(BaseModel):
    id: int
    heart_rate: float
    spo2: float
    temperature: float
    measurement_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class MeasurementOut(BaseModel):
    id: int
    heart_rate: float
    spo2: float
    temperature: float
    source: str
    risk: str
    recorded_at: datetime

    model_config = {"from_attributes": True}


class AlertOut(BaseModel):
    id: int
    severity: str
    message: str
    created_at: datetime
    acknowledged: bool

    model_config = {"from_attributes": True}


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as db:
        yield db


def assess(reading: MeasurementIn, baseline: Baseline | None) -> Risk:
    if reading.spo2 < 92 or reading.heart_rate > 130 or reading.heart_rate < 45 or reading.temperature > 39:
        return Risk.HIGH_RISK
    if baseline and (
        abs(reading.heart_rate - baseline.heart_rate) > 20
        or baseline.spo2 - reading.spo2 > 3
        or abs(reading.temperature - baseline.temperature) > 1.5
    ):
        return Risk.ATTENTION
    return Risk.NORMAL


def generate_reading() -> MeasurementIn:
    return MeasurementIn(
        heart_rate=round(72 + random.uniform(-8, 8), 1),
        spo2=round(98 + random.uniform(-1, 0.5), 1),
        temperature=round(36.6 + random.uniform(-0.4, 0.4), 1),
        source="simulation",
    )


app = FastAPI(title="PrediCare API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("PREDICARE_CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(engine)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "predicare-api"}


@app.get("/api/dashboard")
def dashboard(db: Session = Depends(get_db)) -> dict:
    latest = db.scalar(select(Measurement).order_by(Measurement.recorded_at.desc()))
    baseline = db.scalar(select(Baseline).order_by(Baseline.created_at.desc()))
    alerts = db.scalars(select(Alert).order_by(Alert.created_at.desc()).limit(5)).all()
    return {
        "latest": latest,
        "baseline": baseline,
        "alerts": alerts,
        "device": {"connected": latest is not None and latest.source == "device", "simulation": latest is None or latest.source == "simulation"},
    }


@app.get("/api/measurements", response_model=list[MeasurementOut])
def measurements(limit: int = Query(default=30, ge=1, le=500), db: Session = Depends(get_db)) -> list[Measurement]:
    return list(db.scalars(select(Measurement).order_by(Measurement.recorded_at.desc()).limit(limit)).all())[::-1]


@app.post("/api/measurements", response_model=MeasurementOut)
def create_measurement(payload: MeasurementIn, db: Session = Depends(get_db)) -> Measurement:
    baseline = db.scalar(select(Baseline).order_by(Baseline.created_at.desc()))
    risk = assess(payload, baseline)
    item = Measurement(**payload.model_dump(), risk=risk.value)
    db.add(item)
    if risk != Risk.NORMAL:
        db.add(Alert(severity=risk.value, message=f"Measurement requires {risk.value.lower().replace('_', ' ')} review"))
    db.commit()
    db.refresh(item)
    return item


@app.post("/api/measurements/simulate", response_model=MeasurementOut)
def simulate_measurement(db: Session = Depends(get_db)) -> Measurement:
    return create_measurement(generate_reading(), db)


@app.get("/api/baseline", response_model=BaselineOut | None)
def get_baseline(db: Session = Depends(get_db)) -> Baseline | None:
    return db.scalar(select(Baseline).order_by(Baseline.created_at.desc()))


@app.post("/api/baseline", response_model=BaselineOut)
def create_baseline(db: Session = Depends(get_db)) -> Baseline:
    readings = db.scalars(select(Measurement).order_by(Measurement.recorded_at.desc()).limit(10)).all()
    if not readings:
        raise HTTPException(status_code=400, detail="At least one measurement is required")
    baseline = Baseline(
        heart_rate=sum(x.heart_rate for x in readings) / len(readings),
        spo2=sum(x.spo2 for x in readings) / len(readings),
        temperature=sum(x.temperature for x in readings) / len(readings),
        measurement_count=len(readings),
    )
    db.add(baseline)
    db.commit()
    db.refresh(baseline)
    return baseline


@app.get("/api/alerts", response_model=list[AlertOut])
def alerts(db: Session = Depends(get_db)) -> list[Alert]:
    return list(db.scalars(select(Alert).order_by(Alert.created_at.desc()).limit(100)).all())


@app.post("/api/demo/seed")
def seed_demo(db: Session = Depends(get_db)) -> dict[str, int]:
    for _ in range(12):
        reading = generate_reading()
        create_measurement(reading, db)
    return {"created": 12}
