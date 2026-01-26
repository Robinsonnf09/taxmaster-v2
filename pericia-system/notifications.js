const nodemailer = require('nodemailer');

class NotificationSystem {
    constructor() {
        // Configuração básica (pode ser ajustada depois)
        this.transporter = null;
        this.configurado = false;
    }

    configurar(emailUser, emailPass) {
        try {
            this.transporter = nodemailer.createTransporter({
                service: 'gmail',
                auth: {
                    user: emailUser,
                    pass: emailPass
                }
            });
            this.configurado = true;
            console.log('✓ Sistema de notificações configurado');
        } catch (error) {
            console.error('❌ Erro ao configurar notificações:', error.message);
        }
    }

    async enviarNotificacaoNovaOportunidade(oportunidade, usuarioEmail) {
        if (!this.configurado) {
            console.log('⚠️ Sistema de notificações não configurado. Configure em .env');
            return false;
        }

        const htmlContent = `
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
                    <h1 style="color: white;">Nova Oportunidade!</h1>
                </div>
                <div style="padding: 30px; background: #f9fafb;">
                    <h2>Detalhes:</h2>
                    <p><strong>Processo:</strong> ${oportunidade.numeroProcesso}</p>
                    <p><strong>Tribunal:</strong> ${oportunidade.tribunal}</p>
                    <p><strong>Honorarios:</strong> R$ ${oportunidade.honorariosEstimados}</p>
                    <a href="http://localhost:3000" style="background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 20px;">Acessar Dashboard</a>
                </div>
            </div>
        `;

        try {
            await this.transporter.sendMail({
                from: '"Tax Master" <noreply@taxmaster.com>',
                to: usuarioEmail,
                subject: `Nova Oportunidade: ${oportunidade.especialidade}`,
                html: htmlContent
            });
            console.log(`✓ Email enviado para ${usuarioEmail}`);
            return true;
        } catch (error) {
            console.error(`❌ Erro ao enviar email: ${error.message}`);
            return false;
        }
    }

    // Método para testar sem configuração
    testeDemo() {
        console.log('📧 Modo demo: Sistema de notificações disponível');
        console.log('💡 Configure EMAIL_USER e EMAIL_PASS no .env para ativar');
        return true;
    }
}

const notificationSystem = new NotificationSystem();

// Tentar configurar se variáveis de ambiente existirem
if (process.env.EMAIL_USER && process.env.EMAIL_PASS) {
    notificationSystem.configurar(process.env.EMAIL_USER, process.env.EMAIL_PASS);
} else {
    console.log('⚠️ Notificações em modo demo (configure .env para ativar)');
}

module.exports = notificationSystem;
