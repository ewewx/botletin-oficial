from sqlalchemy import create_engine, Column, Integer, String, Date, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./boletinoficial.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy model
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

# Create tables
Base.metadata.create_all(bind=engine)