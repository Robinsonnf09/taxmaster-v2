"""
Módulo de Enriquecimento de Leads
Sistema de gestão e enriquecimento de contatos
"""

from database import SessionLocal
from models_atualizado import Processo, Contato
from datetime import datetime

class EnriquecimentoLeads:
    """Sistema de enriquecimento de leads"""
    
    @staticmethod
    def extrair_leads_de_processos():
        """Extrai leads (credores e advogados) dos processos"""
        db = SessionLocal()
        
        try:
            processos = db.query(Processo).all()
            leads_criados = 0
            
            for processo in processos:
                # Criar lead do credor
                if processo.credor_nome and not db.query(Contato).filter(
                    Contato.processo_id == processo.id,
                    Contato.tipo == "CREDOR"
                ).first():
                    
                    lead_credor = Contato(
                        processo_id=processo.id,
                        nome=processo.credor_nome,
                        tipo="CREDOR",
                        email_principal=processo.credor_email,
                        telefone_principal=processo.credor_telefone
                    )
                    db.add(lead_credor)
                    leads_criados += 1
                
                # Criar lead do advogado
                if processo.advogado_nome and not db.query(Contato).filter(
                    Contato.processo_id == processo.id,
                    Contato.tipo == "ADVOGADO"
                ).first():
                    
                    lead_advogado = Contato(
                        processo_id=processo.id,
                        nome=processo.advogado_nome,
                        tipo="ADVOGADO",
                        email_principal=processo.advogado_email,
                        telefone_principal=processo.advogado_telefone
                    )
                    db.add(lead_advogado)
                    leads_criados += 1
            
            db.commit()
            
            return {
                "leads_criados": leads_criados,
                "total_processos": len(processos)
            }
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    @staticmethod
    def obter_estatisticas_leads():
        """Estatísticas de leads"""
        db = SessionLocal()
        
        try:
            total_leads = db.query(Contato).count()
            leads_com_email = db.query(Contato).filter(Contato.email_principal != None).count()
            leads_com_telefone = db.query(Contato).filter(Contato.telefone_principal != None).count()
            
            # Leads por tipo
            credores = db.query(Contato).filter(Contato.tipo == "CREDOR").count()
            advogados = db.query(Contato).filter(Contato.tipo == "ADVOGADO").count()
            
            return {
                "total_leads": total_leads,
                "leads_com_email": leads_com_email,
                "leads_com_telefone": leads_com_telefone,
                "credores": credores,
                "advogados": advogados,
                "taxa_enriquecimento": (leads_com_email / total_leads * 100) if total_leads > 0 else 0
            }
        finally:
            db.close()

# Instância global
enriquecimento = EnriquecimentoLeads()
