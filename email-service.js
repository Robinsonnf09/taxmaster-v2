const nodemailer = require('nodemailer');

// Configuração do transporter (use suas credenciais reais)
const transporter = nodemailer.createTransport({
    host: 'smtp.gmail.com',
    port: 587,
    secure: false,
    auth: {
        user: process.env.EMAIL_USER || 'seu-email@gmail.com',
        pass: process.env.EMAIL_PASS || 'sua-senha-app'
    }
});

async function enviarEmail(destinatario, assunto, corpo) {
    try {
        const info = await transporter.sendMail({
            from: '"Tax Master V3" <taxmaster@sistema.com>',
            to: destinatario,
            subject: assunto,
            html: corpo
        });
        
        console.log('✅ Email enviado:', info.messageId);
        return { sucesso: true, messageId: info.messageId };
    } catch (error) {
        console.error('❌ Erro ao enviar email:', error);
        return { sucesso: false, erro: error.message };
    }
}

async function notificarNovoProcesso(usuario, processo) {
    const corpo = `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #667eea;">🔔 Novo Processo Detectado</h2>
            <div style="background: #f5f5f5; padding: 20px; border-radius: 10px;">
                <p><strong>Número:</strong> ${processo.numero}</p>
                <p><strong>Tribunal:</strong> ${processo.tribunal}</p>
                <p><strong>Valor:</strong> R$ ${parseFloat(processo.valor).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</p>
                <p><strong>Status:</strong> ${processo.status}</p>
            </div>
            <p style="margin-top: 20px;">
                <a href="https://web-production-ad84.up.railway.app/processos" 
                   style="background: #667eea; color: white; padding: 12px 24px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    Ver no Sistema
                </a>
            </p>
        </div>
    `;
    
    return await enviarEmail(usuario.email, 'Novo Processo - Tax Master V3', corpo);
}

async function enviarRelatorioSemanal(usuario, estatisticas) {
    const corpo = `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #667eea;">📊 Relatório Semanal</h2>
            <div style="background: #f5f5f5; padding: 20px; border-radius: 10px;">
                <h3>Resumo da Semana</h3>
                <p><strong>Total de Processos:</strong> ${estatisticas.total}</p>
                <p><strong>Novos esta semana:</strong> ${estatisticas.novos}</p>
                <p><strong>Valor Total:</strong> R$ ${estatisticas.valorTotal.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</p>
            </div>
            <p style="margin-top: 20px;">
                <a href="https://web-production-ad84.up.railway.app/dashboard" 
                   style="background: #667eea; color: white; padding: 12px 24px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    Ver Dashboard Completo
                </a>
            </p>
        </div>
    `;
    
    return await enviarEmail(usuario.email, 'Relatório Semanal - Tax Master V3', corpo);
}

module.exports = { enviarEmail, notificarNovoProcesso, enviarRelatorioSemanal };
