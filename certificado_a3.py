"""
Módulo de gerenciamento de Certificado Digital A3
Suporta leitura e autenticação
"""

import os
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from OpenSSL import crypto
import base64

class CertificadoA3Manager:
    def __init__(self, cert_path=None, password=None):
        self.cert_path = cert_path
        self.password = password
        self.certificate = None
        self.private_key = None
        
    def carregar_certificado_pfx(self, pfx_path, password):
        """Carrega certificado .pfx/.p12"""
        try:
            with open(pfx_path, 'rb') as f:
                pfx_data = f.read()
            
            # Carregar usando pyOpenSSL
            p12 = crypto.load_pkcs12(pfx_data, password.encode())
            
            self.certificate = p12.get_certificate()
            self.private_key = p12.get_privatekey()
            
            return {
                'sucesso': True,
                'mensagem': 'Certificado carregado com sucesso',
                'dados': self.extrair_dados_certificado()
            }
            
        except Exception as e:
            return {
                'sucesso': False,
                'erro': f'Erro ao carregar certificado: {str(e)}'
            }
    
    def extrair_dados_certificado(self):
        """Extrai informações do certificado"""
        if not self.certificate:
            return {}
        
        subject = self.certificate.get_subject()
        issuer = self.certificate.get_issuer()
        
        return {
            'nome': subject.CN if hasattr(subject, 'CN') else 'N/A',
            'cpf_cnpj': self.extrair_cpf_cnpj(subject),
            'emissor': issuer.CN if hasattr(issuer, 'CN') else 'N/A',
            'validade_inicio': self.certificate.get_notBefore().decode(),
            'validade_fim': self.certificate.get_notAfter().decode(),
            'serial': self.certificate.get_serial_number()
        }
    
    def extrair_cpf_cnpj(self, subject):
        """Extrai CPF/CNPJ do certificado"""
        # Certificados A3 ICP-Brasil armazenam CPF/CNPJ no campo serialNumber
        if hasattr(subject, 'serialNumber'):
            return subject.serialNumber
        return 'N/A'
    
    def validar_certificado(self):
        """Valida se certificado está dentro da validade"""
        if not self.certificate:
            return False
        
        # Verificar se está dentro da validade
        return not self.certificate.has_expired()
    
    def assinar_dados(self, dados):
        """Assina dados com a chave privada"""
        if not self.private_key:
            return None
        
        try:
            assinatura = crypto.sign(self.private_key, dados.encode(), 'sha256')
            return base64.b64encode(assinatura).decode()
        except Exception as e:
            print(f"Erro ao assinar: {e}")
            return None

# Singleton global
certificado_manager = CertificadoA3Manager()
