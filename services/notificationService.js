// services/notificationService.js - Sistema de Notificações
const nodemailer = require('nodemailer');
const logger = require('../config/logger');

class NotificationService {
  constructor() {
    this.transporter = null;
    this.initializeTransporter();
  }

  initializeTransporter() {
    if (process.env.EMAIL_USER && process.env.EMAIL_PASS) {
      this.transporter = nodemailer.createTransport({
        host: process.env.EMAIL_HOST || 'smtp.gmail.com',
        port: process.env.EMAIL_PORT || 587,
        secure: false,
        auth: {
          user: process.env.EMAIL_USER,
          pass: process.env.EMAIL_PASS
        }
      });
      logger.info('✅ Serviço de email configurado');
    } else {
      logger.warn('⚠️ Credenciais de email não configuradas');
    }
  }

  async enviarEmail(destinatario, assunto, html) {
    if (!this.transporter) {
      logger.warn('Email não enviado: transporter não configurado');
      return false;
    }

    try {
      const info = await this.transporter.sendMail({
        from: `"Tax Master V3" <${process.env.EMAIL_USER}>`,
        to: destinatario,
        subject: assunto,
        html: html
      });

      logger.info(`✅ Email enviado: ${info.messageId}`);
      return true;
    } catch (error) {
      logger.error(`❌ Erro ao enviar email: ${error.message}`);
      return false;
    }
  }

  async notificarNovosProcessos(usuario, processos) {
    const html = `
      <h2>🔔 Novos Processos Encontrados</h2>
      <p>Olá, foram encontrados ${processos.length} novos processos que correspondem aos seus critérios:</p>
      <ul>
        ${processos.slice(0, 5).map(p => `
          <li>
            <strong>${p.numero}</strong><br>
            Credor: ${p.credor}<br>
            Valor: R$ ${(p.valor || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
          </li>
        `).join('')}
      </ul>
      ${processos.length > 5 ? `<p>... e mais ${processos.length - 5} processos.</p>` : ''}
      <p>Acesse o sistema para ver todos os detalhes.</p>
    `;

    return await this.enviarEmail(
      usuario.email,
      'Tax Master V3 - Novos Processos',
      html
    );
  }

  criarNotificacaoInterna(usuarioId, tipo, mensagem, dados = {}) {
    // Armazenar notificação para exibir no sistema
    const notificacao = {
      id: Date.now(),
      usuarioId,
      tipo,
      mensagem,
      dados,
      lida: false,
      criadaEm: new Date()
    };

    logger.info(`🔔 Notificação criada: ${tipo} para usuário ${usuarioId}`);
    return notificacao;
  }
}

module.exports = new NotificationService();
