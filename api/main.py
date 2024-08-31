# main.py
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel
from datetime import date
from typing import List, Optional
from sqlalchemy import  func
from sqlalchemy.orm import sessionmaker, Session
from models import get_db, init_db, Resolution, ResolutionModel, AdministrativeChargesChange, ChargeChangeType
from scraper import scrape_boletin_oficial
import asyncio

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    init_db()

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


@app.get("/publish")
def publish_todays_changes(db: Session = Depends(get_db)):
    # Get today's date
    today = date.today()
    
    # Query for today's resolutions and their administrative changes
    resolutions = db.query(Resolution).filter(func.date(Resolution.fecha) == today).all()
    
    # Process the resolutions and changes
    data = process_resolutions(resolutions)
    
    return {"data": data}

def process_resolutions(resolutions: List[Resolution]):
    data = {"ministerios": {}}
    
    for resolution in resolutions:
        area = resolution.area
        if area not in data["ministerios"]:
            data["ministerios"][area] = {"bajas": [], "altas": [], "prorrogas": []}
        
        for change in resolution.administrative_changes:
            change_data = {
                "link_resolucion": resolution.url,
                "nombre": change.nombre,
                "dni": change.dni,
                "cargo": change.cargo
            }
            
            if change.tipo == ChargeChangeType.ALTA:
                data["ministerios"][area]["altas"].append(change_data)
            elif change.tipo == ChargeChangeType.BAJA:
                data["ministerios"][area]["bajas"].append(change_data)
            elif change.tipo == ChargeChangeType.PRORROGA:
                data["ministerios"][area]["prorrogas"].append(change_data)
    
    # Remove ministries with no changes
    data["ministerios"] = {
        area: changes
        for area, changes in data["ministerios"].items()
        if any(changes.values())
    }

    return data

# main.py
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# ... (previous code remains the same)
@app.get("/render_changes", response_class=HTMLResponse)
async def render_changes(request: Request, db: Session = Depends(get_db)):
    # Call the publish endpoint to get the data
    publish_data = publish_todays_changes(db)
    print(publish_data)

    # Render the template with the data
    return templates.TemplateResponse("changes_template.html", {
        "request": request,
        "ministerios": publish_data["data"]["ministerios"]
    })

# ... (rest of the code remains the same)

# Run the FastAPI application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)