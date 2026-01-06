from fastapi import FastAPI
from pydantic import BaseModel
import os, hashlib, requests
from datetime import datetime

# Selenium + Edge manual
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By

app = FastAPI(title="Robô de Ofícios", version="0.7.0")

STORAGE_DIR = "storage"
os.makedirs(STORAGE_DIR, exist_ok=True)

# Caminho manual para o msedgedriver.exe
EDGE_DRIVER_PATH = r"C:\TAX_MASTER_DEV\drivers\msedgedriver.exe"

class FetchRequest(BaseModel):
    pdf_url: str

class CrawlRequest(BaseModel):
    page_url: str

@app.get("/")
def read_root():
    return {
        "message": "Robô de Ofícios rodando com sucesso!",
        "endpoints": ["/fetch", "/documents", "/crawl"]
    }

@app.post("/fetch")
def fetch_pdf(request: FetchRequest):
    pdf_url = request.pdf_url
    try:
        response = requests.get(pdf_url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return {"error": f"Falha ao baixar PDF: {str(e)}"}

    filename = pdf_url.split("/")[-1]
    filepath = os.path.join(STORAGE_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(response.content)

    file_hash = hashlib.sha256(response.content).hexdigest()

    return {
        "filename": filename,
        "path": filepath,
        "hash": file_hash,
        "size": len(response.content),
        "downloaded_at": datetime.now().isoformat()
    }

@app.get("/documents")
def list_documents():
    files = []
    for fname in os.listdir(STORAGE_DIR):
        fpath = os.path.join(STORAGE_DIR, fname)
        size = os.path.getsize(fpath)
        files.append({
            "filename": fname,
            "path": fpath,
            "size": size
        })
    return files

@app.post("/crawl")
def crawl_pdfs(request: CrawlRequest):
    page_url = request.page_url

    options = webdriver.EdgeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = None
    try:
        # Inicializa Edge com driver manual
        service = Service(EDGE_DRIVER_PATH)
        driver = webdriver.Edge(service=service, options=options)

        driver.get(page_url)
        links = driver.find_elements(By.TAG_NAME, "a")

        pdf_links = []
        for link in links:
            href = link.get_attribute("href")
            if href and href.lower().endswith(".pdf"):
                pdf_links.append(href)

        return {
            "source": page_url,
            "pdf_count": len(pdf_links),
            "pdf_links": pdf_links
        }

    except Exception as e:
        # Captura qualquer erro e retorna JSON em vez de 500
        return {"error": f"Falha ao iniciar EdgeDriver ou acessar página: {str(e)}"}

    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

