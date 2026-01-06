"""
Módulo de Segurança
Sistema de auditoria, logs e proteção de dados
"""

import hashlib
from datetime import datetime
from database import SessionLocal

class SistemaSeguranca:
    """Sistema de segurança e auditoria"""
    
    @staticmethod
    def gerar_hash_arquivo(caminho_arquivo):
        """Gera hash SHA-256 de um arquivo"""
        sha256_hash = hashlib.sha256()
        
        try:
            with open(caminho_arquivo, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception:
            return None
    
    @staticmethod
    def validar_integridade_oficio(processo):
        """Valida integridade de ofício requisitório"""
        if not processo.caminho_oficio:
            return False
        
        hash_atual = SistemaSeguranca.gerar_hash_arquivo(processo.caminho_oficio)
        
        if not hash_atual:
            return False
        
        # Se não tem hash armazenado, armazena o atual
        if not processo.hash_oficio:
            processo.hash_oficio = hash_atual
            return True
        
        # Compara hashes
        return hash_atual == processo.hash_oficio
    
    @staticmethod
    def obter_estatisticas_seguranca():
        """Estatísticas de segurança"""
        db = SessionLocal()
        
        try:
            from models_atualizado import Processo
            
            total_oficios = db.query(Processo).filter(Processo.tem_oficio == True).count()
            oficios_com_hash = db.query(Processo).filter(Processo.hash_oficio != None).count()
            
            return {
                "total_oficios": total_oficios,
                "oficios_protegidos": oficios_com_hash,
                "taxa_protecao": (oficios_com_hash / total_oficios * 100) if total_oficios > 0 else 0,
                "criptografia": "SHA-256",
                "backup_automatico": True,
                "auditoria_ativa": True
            }
        finally:
            db.close()

# Instância global
seguranca = SistemaSeguranca()
