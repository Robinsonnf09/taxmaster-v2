import schedule
import time
import subprocess
import os
from datetime import datetime

def executar_scraper():
    """Executa o scraper real"""
    print(f"\n🕐 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Executando scraper...")
    try:
        result = subprocess.run(
            ["python", "scrapers/scraper_real.py"],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print("✅ Scraper executado com sucesso!")
            print(result.stdout)
        else:
            print("❌ Erro ao executar scraper:")
            print(result.stderr)
    
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

def iniciar_agendador():
    """Inicia o agendamento automático"""
    print("=" * 60)
    print("📅 AGENDADOR DE SCRAPER INICIADO")
    print("=" * 60)
    print("\n⏰ Configuração:")
    print("  • Execução: A cada 6 horas")
    print("  • Horários: 00:00, 06:00, 12:00, 18:00")
    print("  • Tribunais: TJ-SP, TJ-RJ, TRF3")
    print("\n💡 Pressione Ctrl+C para parar\n")
    
    # Agendar para executar a cada 6 horas
    schedule.every(6).hours.do(executar_scraper)
    
    # Executar imediatamente na inicialização
    executar_scraper()
    
    # Loop de execução
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verificar a cada minuto
    except KeyboardInterrupt:
        print("\n\n⚠️ Agendador interrompido pelo usuário")
        print("=" * 60)

if __name__ == "__main__":
    iniciar_agendador()
