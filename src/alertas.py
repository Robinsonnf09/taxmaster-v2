import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger("Alertas")

class SistemaAlertas:
    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        
    def enviar_email(self, destinatario, assunto, corpo, remetente, senha):
        """Envia email de alerta"""
        try:
            msg = MIMEMultipart()
            msg["From"] = remetente
            msg["To"] = destinatario
            msg["Subject"] = assunto
            
            msg.attach(MIMEText(corpo, "html"))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(remetente, senha)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email enviado para {destinatario}")
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar email: {str(e)}")
            return False
    
    def alerta_nova_oportunidade(self, processo_data, destinatarios):
        """Envia alerta de nova oportunidade detectada"""
        assunto = f"Nova Oportunidade: {processo_data['numero_processo']}"
        
        corpo = f"""
        <html>
        <body>
            <h2>Nova Oportunidade Detectada!</h2>
            <p><strong>Processo:</strong> {processo_data['numero_processo']}</p>
            <p><strong>Tribunal:</strong> {processo_data['tribunal']}</p>
            <p><strong>Valor:</strong> R$ {processo_data['valor_atualizado']:,.2f}</p>
            <p><strong>Score:</strong> {processo_data['score_oportunidade']}/10</p>
            <p><strong>Fase:</strong> {processo_data['fase']}</p>
            <hr>
            <p><em>TaxMaster CRM - Sistema Automatizado</em></p>
        </body>
        </html>
        """
        
        for dest in destinatarios:
            self.enviar_email(dest, assunto, corpo, "sistema@taxmaster.com", "senha_aqui")

alertas = SistemaAlertas()
