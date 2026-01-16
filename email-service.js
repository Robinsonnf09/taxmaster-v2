const nodemailer = require('nodemailer');

// Configuração do transporter para comercial@taxmaster.com.br
const transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST || 'smtp.gmail.com',
    port: process.env.SMTP_PORT || 587,
    secure: false,
    auth: {
        user: process.env.EMAIL_USER || 'comercial@taxmaster.com.br',
        pass: process.env.EMAIL_PASS || 'sua-senha-aqui'
    }
});

async function enviarEmail(destinatario, assunto, corpo) {
    try {
        const info = await transporter.sendMail({
            from: '"Tax Master V3" <comercial@taxmaster.com.br>',
            to: destinatario,
            subject: assunto,
            html: corpo
        });
        
        console.log('✅ Email enviado para:', destinatario);
        console.log('   Message ID:', info.messageId);
        return { sucesso: true, messageId: info.messageId };
    } catch (error) {
        console.error('❌ Erro ao enviar email:', error.message);
        return { sucesso: false, erro: error.message };
    }
}

async function notificarNovoProcesso(usuario, processo) {
    const corpo = `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                         color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
                .content { background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; }
                .processo-info { background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }
                .processo-info p { margin: 10px 0; }
                .button { display: inline-block; background: #667eea; color: white; padding: 12px 30px; 
                         text-decoration: none; border-radius: 5px; margin-top: 20px; }
                .footer { text-align: center; padding: 20px; color: #999; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔔 Novo Processo Detectado</h1>
                    <p>Tax Master V3 - Sistema de Gestão de Precatórios</p>
                </div>
                <div class="content">
                    <p>Olá <strong>${usuario.nome}</strong>,</p>
                    <p>Um novo processo foi detectado e adicionado ao sistema:</p>
                    
                    <div class="processo-info">
                        <p><strong>📋 Número:</strong> ${processo.numero}</p>
                        <p><strong>🏛️ Tribunal:</strong> ${processo.tribunal}</p>
                        <p><strong>💰 Valor:</strong> R$ ${parseFloat(processo.valor).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</p>
                        <p><strong>📊 Status:</strong> ${processo.status}</p>
                        <p><strong>📅 Data:</strong> ${processo.dataDistribuicao || 'N/A'}</p>
                        ${processo.natureza ? `<p><strong>📑 Natureza:</strong> ${processo.natureza}</p>` : ''}
                        ${processo.anoLOA ? `<p><strong>📆 ANO LOA:</strong> ${processo.anoLOA}</p>` : ''}
                    </div>
                    
                    <p>Acesse o sistema para mais detalhes:</p>
                    <a href="https://web-production-ad84.up.railway.app/processos" class="button">
                        Ver no Sistema →
                    </a>
                </div>
                <div class="footer">
                    <p>Este é um email automático do Tax Master V3</p>
                    <p>comercial@taxmaster.com.br</p>
                </div>
            </div>
        </body>
        </html>
    `;
    
    return await enviarEmail(usuario.email, `🔔 Novo Processo: ${processo.numero}`, corpo);
}

async function enviarRelatorioSemanal(usuario, estatisticas) {
    const corpo = `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                         color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
                .content { background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; }
                .stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0; }
                .stat-card { background: #f5f5f5; padding: 20px; border-radius: 8px; text-align: center; }
                .stat-number { font-size: 32px; font-weight: bold; color: #667eea; }
                .stat-label { font-size: 14px; color: #666; margin-top: 5px; }
                .button { display: inline-block; background: #667eea; color: white; padding: 12px 30px; 
                         text-decoration: none; border-radius: 5px; margin-top: 20px; }
                .footer { text-align: center; padding: 20px; color: #999; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Relatório Semanal</h1>
                    <p>Tax Master V3 - Resumo da Semana</p>
                </div>
                <div class="content">
                    <p>Olá <strong>${usuario.nome}</strong>,</p>
                    <p>Aqui está o resumo semanal do Tax Master V3:</p>
                    
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number">${estatisticas.total}</div>
                            <div class="stat-label">Total de Processos</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${estatisticas.novos}</div>
                            <div class="stat-label">Novos esta Semana</div>
                        </div>
                    </div>
                    
                    <div class="stat-card" style="margin: 20px 0;">
                        <div class="stat-number">R$ ${estatisticas.valorTotal.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</div>
                        <div class="stat-label">Valor Total em Processos</div>
                    </div>
                    
                    <p>Acesse o dashboard para análise completa:</p>
                    <a href="https://web-production-ad84.up.railway.app/dashboard" class="button">
                        Ver Dashboard Completo →
                    </a>
                </div>
                <div class="footer">
                    <p>Relatório gerado automaticamente toda segunda-feira às 8h</p>
                    <p>comercial@taxmaster.com.br</p>
                </div>
            </div>
        </body>
        </html>
    `;
    
    return await enviarEmail(usuario.email, '📊 Relatório Semanal - Tax Master V3', corpo);
}

async function enviarBoasVindas(usuario, senhaTemporaria) {
    const corpo = `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                         color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
                .content { background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; }
                .credentials { background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }
                .button { display: inline-block; background: #667eea; color: white; padding: 12px 30px; 
                         text-decoration: none; border-radius: 5px; margin-top: 20px; }
                .footer { text-align: center; padding: 20px; color: #999; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Bem-vindo ao Tax Master V3!</h1>
                    <p>Sistema Empresarial de Gestão de Precatórios</p>
                </div>
                <div class="content">
                    <p>Olá <strong>${usuario.nome}</strong>,</p>
                    <p>Sua conta foi criada com sucesso no Tax Master V3!</p>
                    
                    <div class="credentials">
                        <h3>🔑 Suas Credenciais de Acesso:</h3>
                        <p><strong>Email:</strong> ${usuario.email}</p>
                        <p><strong>Senha:</strong> ${senhaTemporaria}</p>
                        <p><strong>Perfil:</strong> ${usuario.perfil.toUpperCase()}</p>
                    </div>
                    
                    <p><strong>⚠️ Importante:</strong> Por segurança, altere sua senha no primeiro acesso.</p>
                    
                    <a href="https://web-production-ad84.up.railway.app/" class="button">
                        Acessar o Sistema →
                    </a>
                </div>
                <div class="footer">
                    <p>Tax Master V3 - Sistema Empresarial</p>
                    <p>comercial@taxmaster.com.br</p>
                </div>
            </div>
        </body>
        </html>
    `;
    
    return await enviarEmail(usuario.email, '🎉 Bem-vindo ao Tax Master V3', corpo);
}

// Teste de email ao iniciar
async function testarConexao() {
    try {
        await transporter.verify();
        console.log('✅ Servidor de email conectado: comercial@taxmaster.com.br');
        return true;
    } catch (error) {
        console.error('❌ Erro na conexão de email:', error.message);
        console.log('⚠️ Configure as variáveis de ambiente: EMAIL_USER e EMAIL_PASS');
        return false;
    }
}

testarConexao();

module.exports = { 
    enviarEmail, 
    notificarNovoProcesso, 
    enviarRelatorioSemanal, 
    enviarBoasVindas,
    testarConexao 
};
