"""
Módulo de Inteligência e Análise de Risco
Sistema avançado de scoring e classificação de ativos
"""

from datetime import datetime
from database import SessionLocal
from models_atualizado import Processo
import statistics

class InteligenciaRisco:
    """Sistema de inteligência e análise de risco"""
    
    # Histórico de pagamento por ente (simulado - em produção viria de base real)
    HISTORICO_PAGAMENTO = {
        "UNIAO": {"taxa_cumprimento": 0.95, "atraso_medio_dias": 180},
        "ESTADO_SP": {"taxa_cumprimento": 0.88, "atraso_medio_dias": 240},
        "ESTADO_RJ": {"taxa_cumprimento": 0.75, "atraso_medio_dias": 365},
        "ESTADO_MG": {"taxa_cumprimento": 0.82, "atraso_medio_dias": 300},
        "PREFEITURA_SP": {"taxa_cumprimento": 0.85, "atraso_medio_dias": 210},
        "PREFEITURA_RJ": {"taxa_cumprimento": 0.70, "atraso_medio_dias": 400},
        "INSS": {"taxa_cumprimento": 0.92, "atraso_medio_dias": 150}
    }
    
    def __init__(self):
        self.db = SessionLocal()
    
    def analisar_risco_ente(self, ente_pagador):
        """
        Analisa risco do ente pagador
        
        Returns:
            dict: Análise de risco
        """
        if not ente_pagador:
            return {"risco": "ALTO", "confiabilidade": 0.5}
        
        ente_nome = ente_pagador.name
        historico = self.HISTORICO_PAGAMENTO.get(ente_nome, {
            "taxa_cumprimento": 0.70,
            "atraso_medio_dias": 365
        })
        
        # Classificar risco
        taxa = historico["taxa_cumprimento"]
        if taxa >= 0.90:
            risco = "BAIXO"
        elif taxa >= 0.80:
            risco = "MEDIO"
        elif taxa >= 0.70:
            risco = "ALTO"
        else:
            risco = "MUITO_ALTO"
        
        return {
            "risco": risco,
            "taxa_cumprimento": taxa * 100,
            "atraso_medio_dias": historico["atraso_medio_dias"],
            "atraso_medio_meses": round(historico["atraso_medio_dias"] / 30),
            "confiabilidade": taxa
        }
    
    def calcular_roi_estimado(self, processo, taxa_desconto=0.15):
        """
        Calcula ROI estimado considerando desconto e tempo
        
        Args:
            processo: Objeto Processo
            taxa_desconto: Taxa de desconto anual (padrão 15%)
            
        Returns:
            dict: Análise de ROI
        """
        from monitor_oficios import monitor_oficios
        
        # Calcular tempo estimado
        tempo_est = monitor_oficios.calcular_tempo_estimado_liquidacao(
            "PRECATORIO_REGISTRADO" if processo.ano_precatorio else "OFICIO_EXPEDIDO",
            processo.ano_precatorio,
            processo.ente_pagador.name if processo.ente_pagador else None
        )
        
        anos_espera = tempo_est["anos_estimados"]
        
        # Valor de face
        valor_face = processo.valor_atualizado
        
        # Valor com desconto típico do mercado (30-50% para precatórios)
        desconto_mercado = 0.35  # 35% de desconto médio
        valor_compra_estimado = valor_face * (1 - desconto_mercado)
        
        # ROI bruto
        roi_bruto = ((valor_face - valor_compra_estimado) / valor_compra_estimado) * 100
        
        # ROI anualizado
        roi_anualizado = roi_bruto / max(anos_espera, 0.5)
        
        # Ajustar por risco do ente
        analise_risco = self.analisar_risco_ente(processo.ente_pagador)
        fator_risco = analise_risco["confiabilidade"]
        roi_ajustado = roi_anualizado * fator_risco
        
        return {
            "valor_face": valor_face,
            "valor_compra_estimado": valor_compra_estimado,
            "desconto_percentual": desconto_mercado * 100,
            "roi_bruto_percentual": roi_bruto,
            "roi_anualizado_percentual": roi_anualizado,
            "roi_ajustado_risco_percentual": roi_ajustado,
            "anos_espera": anos_espera,
            "atratividade": self._classificar_roi(roi_ajustado)
        }
    
    def _classificar_roi(self, roi):
        """Classifica atratividade do ROI"""
        if roi >= 25:
            return "EXCELENTE"
        elif roi >= 18:
            return "MUITO_BOM"
        elif roi >= 12:
            return "BOM"
        elif roi >= 8:
            return "REGULAR"
        else:
            return "BAIXO"
    
    def gerar_analise_portfolio(self, processos_ids):
        """
        Gera análise de portfólio para múltiplos processos
        
        Args:
            processos_ids: Lista de IDs de processos
            
        Returns:
            dict: Análise consolidada
        """
        processos = self.db.query(Processo).filter(Processo.id.in_(processos_ids)).all()
        
        if not processos:
            return None
        
        analises = []
        for processo in processos:
            roi_info = self.calcular_roi_estimado(processo)
            risco_info = self.analisar_risco_ente(processo.ente_pagador)
            
            analises.append({
                "processo_id": processo.id,
                "numero_processo": processo.numero_processo,
                "valor_face": roi_info["valor_face"],
                "valor_compra": roi_info["valor_compra_estimado"],
                "roi_ajustado": roi_info["roi_ajustado_risco_percentual"],
                "risco": risco_info["risco"],
                "tempo_anos": roi_info["anos_espera"]
            })
        
        # Estatísticas do portfólio
        valor_total_face = sum(a["valor_face"] for a in analises)
        valor_total_compra = sum(a["valor_compra"] for a in analises)
        roi_medio = statistics.mean([a["roi_ajustado"] for a in analises])
        tempo_medio = statistics.mean([a["tempo_anos"] for a in analises])
        
        # Distribuição de risco
        distribuicao_risco = {}
        for analise in analises:
            risco = analise["risco"]
            distribuicao_risco[risco] = distribuicao_risco.get(risco, 0) + 1
        
        return {
            "total_ativos": len(analises),
            "valor_total_face": valor_total_face,
            "valor_total_investimento": valor_total_compra,
            "roi_medio_percentual": roi_medio,
            "tempo_medio_anos": tempo_medio,
            "distribuicao_risco": distribuicao_risco,
            "analises_individuais": analises,
            "recomendacao": self._gerar_recomendacao_portfolio(roi_medio, distribuicao_risco)
        }
    
    def _gerar_recomendacao_portfolio(self, roi_medio, distribuicao_risco):
        """Gera recomendação para o portfólio"""
        riscos_altos = distribuicao_risco.get("ALTO", 0) + distribuicao_risco.get("MUITO_ALTO", 0)
        total = sum(distribuicao_risco.values())
        percentual_risco_alto = (riscos_altos / total * 100) if total > 0 else 0
        
        if roi_medio >= 20 and percentual_risco_alto < 30:
            return "EXCELENTE - Portfólio balanceado com alto retorno"
        elif roi_medio >= 15 and percentual_risco_alto < 40:
            return "BOM - Retorno adequado com risco controlado"
        elif percentual_risco_alto > 50:
            return "ATENÇÃO - Concentração elevada em ativos de alto risco"
        else:
            return "REGULAR - Considerar diversificação"
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()

# Instância global
inteligencia_risco = InteligenciaRisco()
