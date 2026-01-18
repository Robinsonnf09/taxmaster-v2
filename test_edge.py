from selenium import webdriver
from selenium.webdriver.edge.service import Service

EDGE_DRIVER_PATH = r"C:\TAX_MASTER_DEV\drivers\msedgedriver.exe"

options = webdriver.EdgeOptions()
options.add_argument("--headless")

service = Service(EDGE_DRIVER_PATH)
driver = webdriver.Edge(service=service, options=options)

driver.get("https://www.stf.jus.br")
print("Título da página:", driver.title)

driver.quit()
