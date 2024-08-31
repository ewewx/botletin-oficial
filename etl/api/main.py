# main.py
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from datetime import date
from typing import List, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from models import Resolution, AdministrativeChargesChange, ChargeChangeType
from scraper import scrape_boletin_oficial
import asyncio

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./boletinoficial.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

AdministrativeChargesChange.resolution = relationship("Resolution", back_populates="administrative_changes")

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models for API
class AdministrativeChargesChangeModel(BaseModel):
    tipo: ChargeChangeType
    nombre: str
    dni: str
    cargo: str
    replaces: Optional[str] = None

class ResolutionModel(BaseModel):
    fecha: date
    titulo: str
    url: str
    tipo: str
    organismo: str
    area: str
    texto_completo: str
    archivos: List[str]
    administrative_changes: List[AdministrativeChargesChangeModel]

    class Config:
        orm_mode = True

app = FastAPI()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Background task function
def run_scraper_sync(db: Session):
    asyncio.run(scrape_boletin_oficial(db))

# API endpoints
@app.post("/scrape/")
def scrape_website(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    background_tasks.add_task(run_scraper_sync, db)
    return {"message": "Scraping task has been scheduled"}

@app.get("/resolutions/", response_model=List[ResolutionModel])
def get_resolutions(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    fecha: Optional[date] = None,
    tipo: Optional[str] = None,
    organismo: Optional[str] = None,
    area: Optional[str] = None
):
    query = db.query(Resolution)
    if fecha:
        query = query.filter(Resolution.fecha == fecha)
    if tipo:
        query = query.filter(Resolution.tipo == tipo)
    if organismo:
        query = query.filter(Resolution.organismo == organismo)
    if area:
        query = query.filter(Resolution.area == area)
    
    resolutions = query.offset(skip).limit(limit).all()
    return resolutions

@app.get("/resolutions/{resolution_id}", response_model=ResolutionModel)
def get_resolution(resolution_id: int, db: Session = Depends(get_db)):
    resolution = db.query(Resolution).filter(Resolution.id == resolution_id).first()
    if resolution is None:
        raise HTTPException(status_code=404, detail="Resolution not found")
    return resolution

# Run the FastAPI application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)