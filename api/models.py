# models.py

import enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Date, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from typing import Generator, List, Optional
from pydantic import BaseModel
from datetime import date

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./boletinoficial.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class ChargeChangeType(enum.Enum):
    ALTA = "Alta"
    BAJA = "Baja"
    PRORROGA = "Prorroga"

class Resolution(Base):
    __tablename__ = "resolutions"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, index=True)
    titulo = Column(String, index=True)
    url = Column(String)
    tipo = Column(String, index=True)
    organismo = Column(String, index=True)
    area = Column(String, index=True)
    texto_completo = Column(String)
    archivos = Column(JSON)
    administrative_changes = relationship("AdministrativeChargesChange", back_populates="resolution")

class AdministrativeChargesChange(Base):
    __tablename__ = "administrative_charges_changes"

    id = Column(Integer, primary_key=True, index=True)
    resolution_id = Column(Integer, ForeignKey("resolutions.id"))
    tipo = Column(Enum(ChargeChangeType))
    nombre = Column(String)
    cargo = Column(String)
    dni = Column(String, nullable=True)
    replaces = Column(String, nullable=True)
    resolution = relationship("Resolution", back_populates="administrative_changes")

# Database initialization function
def init_db() -> None:
    Base.metadata.create_all(bind=engine)

# Database session dependency
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models for API responses
class AdministrativeChargesChangeModel(BaseModel):
    tipo: ChargeChangeType
    nombre: str
    cargo: str
    dni: Optional[str] = None
    replaces: Optional[str] = None

    class Config:
        orm_mode = True

class ResolutionModel(BaseModel):
    id: int
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