from sqlalchemy import create_engine, Column, Integer, String, Date, JSON, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm import relationship

import enum
Base = declarative_base()

class ChargeChangeType(enum.Enum):
    ALTA = "Alta"
    BAJA = "Baja"
    PRORROGA = "Prorroga"

class AdministrativeChargesChange(Base):
    __tablename__ = "administrative_charges_changes"

    id = Column(Integer, primary_key=True, index=True)
    resolution_id = Column(Integer, ForeignKey("resolutions.id"))
    tipo = Column(Enum(ChargeChangeType))
    nombre = Column(String)
    cargo = Column(String)
    dni = Column(String)
    replaces = Column(String, nullable=True)

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
