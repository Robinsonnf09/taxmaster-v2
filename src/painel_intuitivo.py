"""
Módulo de Painel Intuitivo
Widgets e componentes interativos para o dashboard
"""

from database import SessionLocal
from models_atualizado import Processo, LogBuscaOficio
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta

class PainelIntuitivo:
    """Gerenciador do painel de controle"""
    
    @staticmethod
    def obter_metricas_principais():
        """Retorna métricas principais do sistema"""
        db = SessionLocal()
        
        try:
            hoje = datetime.now().date()
            mes_atual = hoje.replace(day=1)
            
            # Métricas gerais
            total_processos = db.query(Processo).count()
            total_valor = db.query(func.sum(Processo.valor_atualizado)).scalar() or 0
            com_oficio = db.query(Processo).filter(Processo.tem_oficio == True).count()
            pendentes = db.query(Processo).filter(Processo.possui_pendencia_pagamento == True).count()
            
            # Métricas do mês
            processos_mes = db.query(Processo).filter(
                Processo.data_cadastro >= mes_atual
            ).count()
            
            # Processos prioritários
            prioritarios = db.query(Processo).filter(
                or_(
                    Processo.credor_idoso == True,
                    Processo.credor_doenca_grave == True,
                    Processo.credor_deficiente == True
                )
            ).count()
            
            # Valor médio
            valor_medio = total_valor / total_processos if total_processos > 0 else 0
            
            return {
                "total_processos": total_processos,
                "total_valor": total_valor,
                "com_oficio": com_oficio,
                "pendentes": pendentes,
                "processos_mes": processos_mes,
                "prioritarios": prioritarios,
                "valor_medio": valor_medio,
                "percentual_com_oficio": (com_oficio / total_processos * 100) if total_processos > 0 else 0
            }
        finally:
            db.close()
    
    @staticmethod
    def obter_distribuicao_por_esfera():
        """Distribuição de processos por esfera"""
        db = SessionLocal()
        
        try:
            from models_atualizado import EsferaEnum
            
            distribuicao = db.query(
                Processo.esfera,
                func.count(Processo.id).label('total'),
                func.sum(Processo.valor_atualizado).label('valor_total')
            ).group_by(Processo.esfera).all()
            
            return [
                {
                    "esfera": item.esfera.value,
                    "total": item.total,
                    "valor": item.valor_total or 0
                }
                for item in distribuicao
            ]
        finally:
            db.close()
    
    @staticmethod
    def obter_top_processos(limite=10):
        """Top processos por valor"""
        db = SessionLocal()
        
        try:
            processos = db.query(Processo).order_by(
                Processo.valor_atualizado.desc()
            ).limit(limite).all()
            
            return processos
        finally:
            db.close()

# Instância global
painel = PainelIntuitivo()
