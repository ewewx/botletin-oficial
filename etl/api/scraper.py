# scraper.py
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy.orm import Session
from models import Resolution  # Import the Resolution model

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
    db.add(resolution)
    
    return type, area, content, title, status

async def scrape_boletin_oficial(db: Session):
    urls, _ = await today_urls()
    print(f"{len(urls)} Publications found.")
    print('***************')
    
    for i, url in enumerate(urls):
        print(f"Publication {i+1} of {len(urls)}")
        type, area, content, title, _ = await scrape_article(url, db)
    
    print('Completed Scraping')
    db.commit()