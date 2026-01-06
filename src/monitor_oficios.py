"""
Módulo de Monitoramento de Ofícios Requisitórios
Sistema avançado de rastreamento e análise de ofícios
"""

from datetime import datetime, timedelta
from database import SessionLocal
from models_atualizado import Processo, LogBuscaOficio
from sqlalchemy import func, and_, or_
import re

class MonitorOficiosRequisitorios:
    """Sistema de monitoramento de ofícios requisitórios"""
    
    # Termos técnicos que indicam fases do ofício
    TERMOS_EXPEDICAO = [
        "expedido ofício requisitório",
        "expedição de ofício",
        "ofício requisitório expedido",
        "expedir ofício",
        "emitido ofício"
    ]
    
    TERMOS_CONFERENCIA = [
        "conferência do ofício",
        "em conferência",
        "aguardando conferência",
        "ofício em análise"
    ]
    
    TERMOS_ASSINATURA = [
        "assinado ofício",
        "aguardando assinatura",
        "para assinatura",
        "assinatura do ofício"
    ]
    
    TERMOS_ENVIO = [
        "enviado ao tribunal",
        "remetido ao",
        "encaminhado para",
        "enviado à presidência"
    ]
    
    TERMOS_REGISTRO = [
        "registrado precatório",
        "incluído na lista",
        "inscrito no orçamento",
        "precatório nº"
    ]
    
    TERMOS_RETIFICACAO = [
        "retificação do ofício",
        "ofício retificado",
        "correção de valores",
        "ajuste do ofício"
    ]
    
    TERMOS_RPV = [
        "requisição de pequeno valor",
        "RPV",
        "expedido RPV",
        "convertido em RPV"
    ]
    
    TERMOS_PAGAMENTO = [
        "incluído em lista de pagamento",
        "ordem cronológica",
        "previsão de pagamento",
        "liberado para pagamento"
    ]
    
    def __init__(self):
        self.db = SessionLocal()
    
    def identificar_fase_oficio(self, movimentacoes_texto):
        """
        Identifica a fase exata do ofício requisitório
        
        Args:
            movimentacoes_texto: Texto das movimentações processuais
            
        Returns:
            dict: Fase identificada e detalhes
        """
        texto_lower = movimentacoes_texto.lower()
        
        resultado = {
            "fase": "DESCONHECIDA",
            "subfase": None,
            "data_identificada": None,
            "detalhes": [],
            "tipo_credito": None,
            "numero_oficio": None,
            "numero_precatorio": None,
            "valor_identificado": None
        }
        
        # Verificar RPV primeiro (prioridade)
        if any(termo in texto_lower for termo in self.TERMOS_RPV):
            resultado["fase"] = "RPV_EXPEDIDO"
            resultado["tipo_credito"] = "RPV"
            resultado["detalhes"].append("Requisição de Pequeno Valor identificada")
        
        # Verificar registro/precatório
        elif any(termo in texto_lower for termo in self.TERMOS_REGISTRO):
            resultado["fase"] = "PRECATORIO_REGISTRADO"
            resultado["tipo_credito"] = "PRECATORIO"
            
            # Tentar extrair número do precatório
            match_precatorio = re.search(r'precatório\s+n[ºo°]?\s*(\d+[-/]\d+)', texto_lower)
            if match_precatorio:
                resultado["numero_precatorio"] = match_precatorio.group(1)
                resultado["detalhes"].append(f"Precatório nº {resultado['numero_precatorio']}")
        
        # Verificar pagamento
        elif any(termo in texto_lower for termo in self.TERMOS_PAGAMENTO):
            resultado["fase"] = "EM_LISTA_PAGAMENTO"
            resultado["detalhes"].append("Incluído em lista de pagamento")
        
        # Verificar envio
        elif any(termo in texto_lower for termo in self.TERMOS_ENVIO):
            resultado["fase"] = "OFICIO_ENVIADO"
            resultado["subfase"] = "TRAMITACAO"
            resultado["detalhes"].append("Ofício enviado ao tribunal")
        
        # Verificar assinatura
        elif any(termo in texto_lower for termo in self.TERMOS_ASSINATURA):
            resultado["fase"] = "AGUARDANDO_ASSINATURA"
            resultado["detalhes"].append("Ofício aguardando assinatura")
        
        # Verificar conferência
        elif any(termo in texto_lower for termo in self.TERMOS_CONFERENCIA):
            resultado["fase"] = "EM_CONFERENCIA"
            resultado["detalhes"].append("Ofício em conferência")
        
        # Verificar expedição
        elif any(termo in texto_lower for termo in self.TERMOS_EXPEDICAO):
            resultado["fase"] = "OFICIO_EXPEDIDO"
            
            # Tentar extrair número do ofício
            match_oficio = re.search(r'of[íi]cio\s+(?:requisit[óo]rio\s+)?n[ºo°]?\s*([\d./-]+)', texto_lower)
            if match_oficio:
                resultado["numero_oficio"] = match_oficio.group(1)
                resultado["detalhes"].append(f"Ofício nº {resultado['numero_oficio']}")
        
        # Verificar retificação
        if any(termo in texto_lower for termo in self.TERMOS_RETIFICACAO):
            resultado["detalhes"].append("ATENÇÃO: Ofício retificado - verificar valores")
        
        # Tentar extrair valor
        match_valor = re.search(r'R\$\s*([\d.,]+)', texto_lower)
        if match_valor:
            valor_str = match_valor.group(1).replace('.', '').replace(',', '.')
            try:
                resultado["valor_identificado"] = float(valor_str)
            except:
                pass
        
        return resultado
    
    def calcular_tempo_estimado_liquidacao(self, fase, ano_precatorio=None, ente_devedor=None):
        """
        Calcula tempo estimado até liquidação
        
        Args:
            fase: Fase atual do ofício
            ano_precatorio: Ano do precatório (se já registrado)
            ente_devedor: Ente devedor
            
        Returns:
            dict: Estimativa de tempo
        """
        hoje = datetime.now().date()
        
        # Tempos médios por fase (em dias)
        TEMPOS_FASE = {
            "OFICIO_EXPEDIDO": 180,  # 6 meses até registro
            "EM_CONFERENCIA": 150,
            "AGUARDANDO_ASSINATURA": 120,
            "OFICIO_ENVIADO": 90,
            "PRECATORIO_REGISTRADO": 730,  # 2 anos (média)
            "EM_LISTA_PAGAMENTO": 180,  # 6 meses
            "RPV_EXPEDIDO": 60  # 2 meses (RPV é mais rápido)
        }
        
        # Ajuste por ente devedor
        FATOR_ENTE = {
            "UNIAO": 1.5,  # União demora mais
            "ESTADO_SP": 1.2,
            "ESTADO_RJ": 1.3,
            "PREFEITURA_SP": 1.1,
            "INSS": 1.4
        }
        
        dias_base = TEMPOS_FASE.get(fase, 365)
        
        # Aplicar fator do ente
        if ente_devedor:
            fator = FATOR_ENTE.get(ente_devedor, 1.0)
            dias_base = int(dias_base * fator)
        
        # Se já é precatório registrado, calcular pela ordem cronológica
        if fase == "PRECATORIO_REGISTRADO" and ano_precatorio:
            anos_espera = hoje.year - ano_precatorio
            dias_base = max(365, (5 - anos_espera) * 365)  # Máximo 5 anos
        
        data_estimada = hoje + timedelta(days=dias_base)
        
        return {
            "dias_estimados": dias_base,
            "meses_estimados": round(dias_base / 30),
            "anos_estimados": round(dias_base / 365, 1),
            "data_estimada": data_estimada,
            "confiabilidade": "ALTA" if fase in ["RPV_EXPEDIDO", "EM_LISTA_PAGAMENTO"] else "MEDIA"
        }
    
    def classificar_maturidade(self, processo):
        """
        Classifica maturidade do ativo
        
        Returns:
            str: IMEDIATA, CURTO_PRAZO, MEDIO_PRAZO, LONGO_PRAZO
        """
        if not processo.data_expedicao_oficio:
            return "LONGO_PRAZO"
        
        dias_desde_expedicao = (datetime.now().date() - processo.data_expedicao_oficio).days
        
        if processo.tem_oficio and dias_desde_expedicao > 730:  # 2 anos
            return "IMEDIATA"
        elif dias_desde_expedicao > 365:  # 1 ano
            return "CURTO_PRAZO"
        elif dias_desde_expedicao > 180:  # 6 meses
            return "MEDIO_PRAZO"
        else:
            return "LONGO_PRAZO"
    
    def calcular_score_oportunidade(self, processo):
        """
        Calcula score de atratividade da oportunidade (0-100)
        
        Critérios:
        - Valor (30 pontos)
        - Maturidade (25 pontos)
        - Ente devedor (20 pontos)
        - Natureza (15 pontos)
        - Prioridade legal (10 pontos)
        """
        score = 0
        detalhes = []
        
        # 1. Valor (30 pontos)
        if processo.valor_atualizado >= 5000000:
            score += 30
            detalhes.append("Valor muito alto (+30)")
        elif processo.valor_atualizado >= 1000000:
            score += 25
            detalhes.append("Valor alto (+25)")
        elif processo.valor_atualizado >= 500000:
            score += 20
            detalhes.append("Valor médio-alto (+20)")
        elif processo.valor_atualizado >= 100000:
            score += 15
            detalhes.append("Valor médio (+15)")
        else:
            score += 10
            detalhes.append("Valor baixo (+10)")
        
        # 2. Maturidade (25 pontos)
        maturidade = self.classificar_maturidade(processo)
        if maturidade == "IMEDIATA":
            score += 25
            detalhes.append("Maturidade imediata (+25)")
        elif maturidade == "CURTO_PRAZO":
            score += 20
            detalhes.append("Curto prazo (+20)")
        elif maturidade == "MEDIO_PRAZO":
            score += 15
            detalhes.append("Médio prazo (+15)")
        else:
            score += 10
            detalhes.append("Longo prazo (+10)")
        
        # 3. Ente devedor (20 pontos)
        if processo.ente_pagador:
            ente_nome = processo.ente_pagador.name
            if "UNIAO" in ente_nome or "INSS" in ente_nome:
                score += 20
                detalhes.append("Ente federal (+20)")
            elif "ESTADO" in ente_nome:
                score += 15
                detalhes.append("Ente estadual (+15)")
            else:
                score += 10
                detalhes.append("Ente municipal (+10)")
        
        # 4. Natureza (15 pontos)
        if processo.natureza:
            if processo.natureza.name == "ALIMENTAR":
                score += 15
                detalhes.append("Natureza alimentar - prioridade (+15)")
            elif processo.natureza.name == "TRIBUTARIO":
                score += 12
                detalhes.append("Natureza tributária (+12)")
            else:
                score += 10
                detalhes.append("Natureza comum (+10)")
        
        # 5. Prioridade legal (10 pontos)
        if processo.credor_idoso and processo.credor_doenca_grave:
            score += 10
            detalhes.append("Super prioritário (+10)")
        elif processo.credor_idoso or processo.credor_doenca_grave or processo.credor_deficiente:
            score += 7
            detalhes.append("Prioritário (+7)")
        else:
            score += 5
            detalhes.append("Comum (+5)")
        
        return {
            "score": min(score, 100),
            "classificacao": self._classificar_score(score),
            "detalhes": detalhes
        }
    
    def _classificar_score(self, score):
        """Classifica score em categorias"""
        if score >= 85:
            return "EXCELENTE"
        elif score >= 70:
            return "MUITO_BOM"
        elif score >= 55:
            return "BOM"
        elif score >= 40:
            return "REGULAR"
        else:
            return "BAIXO"
    
    def gerar_relatorio_inteligencia(self, filtros=None):
        """
        Gera relatório de inteligência com oportunidades priorizadas
        
        Args:
            filtros: Dicionário com filtros (valor_min, ente, natureza, etc)
            
        Returns:
            dict: Relatório completo
        """
        query = self.db.query(Processo).filter(Processo.tem_oficio == True)
        
        # Aplicar filtros
        if filtros:
            if filtros.get('valor_min'):
                query = query.filter(Processo.valor_atualizado >= filtros['valor_min'])
            
            if filtros.get('ente_pagador'):
                from models_atualizado import EntePagadorEnum
                query = query.filter(Processo.ente_pagador == EntePagadorEnum[filtros['ente_pagador']])
            
            if filtros.get('natureza'):
                from models_atualizado import NaturezaEnum
                query = query.filter(Processo.natureza == NaturezaEnum[filtros['natureza']])
            
            if filtros.get('maturidade_min_dias'):
                data_limite = datetime.now().date() - timedelta(days=filtros['maturidade_min_dias'])
                query = query.filter(Processo.data_expedicao_oficio <= data_limite)
        
        processos = query.all()
        
        # Calcular scores e classificar
        oportunidades = []
        for processo in processos:
            score_info = self.calcular_score_oportunidade(processo)
            maturidade = self.classificar_maturidade(processo)
            tempo_estimado = self.calcular_tempo_estimado_liquidacao(
                "PRECATORIO_REGISTRADO" if processo.ano_precatorio else "OFICIO_EXPEDIDO",
                processo.ano_precatorio,
                processo.ente_pagador.name if processo.ente_pagador else None
            )
            
            oportunidades.append({
                "processo": processo,
                "score": score_info["score"],
                "classificacao": score_info["classificacao"],
                "maturidade": maturidade,
                "tempo_estimado_meses": tempo_estimado["meses_estimados"],
                "detalhes_score": score_info["detalhes"]
            })
        
        # Ordenar por score
        oportunidades.sort(key=lambda x: x["score"], reverse=True)
        
        # Estatísticas
        total_valor = sum(op["processo"].valor_atualizado for op in oportunidades)
        valor_excelente = sum(op["processo"].valor_atualizado for op in oportunidades if op["classificacao"] == "EXCELENTE")
        
        return {
            "total_oportunidades": len(oportunidades),
            "valor_total": total_valor,
            "valor_oportunidades_excelentes": valor_excelente,
            "oportunidades": oportunidades[:50],  # Top 50
            "distribuicao_scores": {
                "EXCELENTE": len([o for o in oportunidades if o["classificacao"] == "EXCELENTE"]),
                "MUITO_BOM": len([o for o in oportunidades if o["classificacao"] == "MUITO_BOM"]),
                "BOM": len([o for o in oportunidades if o["classificacao"] == "BOM"]),
                "REGULAR": len([o for o in oportunidades if o["classificacao"] == "REGULAR"]),
                "BAIXO": len([o for o in oportunidades if o["classificacao"] == "BAIXO"])
            },
            "data_geracao": datetime.now()
        }
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()

# Instância global
monitor_oficios = MonitorOficiosRequisitorios()
