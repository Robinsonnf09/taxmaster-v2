import requests
import sys

try:
    print("🔍 Testando API da Caixa...")
    response = requests.get(
        "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/",
        headers={'User-Agent': 'Mozilla/5.0'},
        timeout=10
    )
    
    if response.status_code == 200:
        dados = response.json()
        print(f"✅ Conexão OK! Último concurso: {dados.get('numero')}")
        sys.exit(0)
    else:
        print(f"⚠️ Status: {response.status_code}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Erro: {e}")
    sys.exit(1)