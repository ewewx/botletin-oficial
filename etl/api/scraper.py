# scraper.py
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy.orm import Session
from models import Resolution, AdministrativeChargesChange, ChargeChangeType  # Import the Resolution model
import prompt
from typing import Dict, Any

async def today_urls():
    """
    Returns a list of ids that correspond
    to that day's publications.
    """
    base_url = 'https://www.boletinoficial.gob.ar'
    articles_url = base_url + '/seccion/primera'
    
    async with httpx.AsyncClient() as client:
        response = await client.get(articles_url)
    status = response.status_code
    
    soup = BeautifulSoup(response.content, "html.parser")
    body = soup.find(id='avisosSeccionDiv')
    
    all_urls = [
        base_url + a['href']
        for a in body.find_all("a", href=True)
    ]
    
    urls = [u for u in all_urls if "?" not in u]
    
    return urls, status

async def scrape_article(article_url, db: Session):
    """
    Scrapes article from Boletin Oficial.
    Returns Type, Content and Date.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(article_url)
    status = response.status_code
    
    soup = BeautifulSoup(response.content, "html.parser")
    
    title_element = soup.find(id="tituloDetalleAviso")
    title = title_element.find("h2").text if title_element and title_element.find("h2") else ""
    
    area_element = soup.find(id="tituloDetalleAviso")
    area = area_element.find("h1").text if area_element and area_element.find("h1") else ""
    
    type_element = soup.find(class_="puntero first-section")
    type = type_element.text if type_element else ""
    
    content_element = soup.find(id="cuerpoDetalleAviso")
    content = content_element.text if content_element else ""
    
    # Create and save the Resolution object
    resolution = Resolution(
        fecha=datetime.today(),
        titulo=title,
        url=article_url,
        tipo=type,
        organismo="FALTA",
        area=area,
        texto_completo=content,
        archivos=[]
    )

    analysis_result = prompt.analyze(content)
    process_analysis_result(resolution, analysis_result)
    
    db.add(resolution)
    
    return resolution

def process_analysis_result(resolution: Resolution, analysis_result: Dict[str, Any]):
    for designation in analysis_result.get("designaciones", []):
        create_administrative_change(resolution, designation, ChargeChangeType.ALTA)
    
    for resignation in analysis_result.get("renuncias", []):
        create_administrative_change(resolution, resignation, ChargeChangeType.BAJA)
    
    for extension in analysis_result.get("prorrogas", []):
        create_administrative_change(resolution, extension, ChargeChangeType.PRORROGA)

def create_administrative_change(resolution: Resolution, data: Dict[str, Any], change_type: ChargeChangeType):
    admin_change = AdministrativeChargesChange(
        tipo=change_type,
        nombre=data["nombre"],
        cargo=data["cargo"],
        dni=data["dni"]
        #replaces=data.get("actas")  # Using 'actas' as 'replaces' for now
    )
    resolution.administrative_changes.append(admin_change)

async def scrape_boletin_oficial(db: Session):
    urls, _ = await today_urls()
    print(f"{len(urls)} Publications found.")
    print('***************')
    
    for i, url in enumerate(urls):
        print(f"Publication {i+1} of {len(urls)}")
        resolution = await scrape_article(url, db)
        print(f"Processed resolution: {resolution.titulo}")
        print(f"Administrative changes: {len(resolution.administrative_changes)}")
    
    print('Completed Scraping')
    db.commit()