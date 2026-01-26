const nodemailer = require('nodemailer');

class EmailService {
    constructor() {
        this.transporter = nodemailer.createTransport({
            host: process.env.SMTP_HOST || 'smtp.gmail.com',
            port: process.env.SMTP_PORT || 587,
            secure: false,
            auth: {
                user: process.env.SMTP_USER,
                pass: process.env.SMTP_PASS
            }
        });
    }
    
    async enviarNovaOportunidade(email, oportunidade) {
        const mailOptions = {
            from: process.env.SMTP_USER,
            to: email,
            subject: `🎯 Nova Oportunidade: ${oportunidade.tribunal}`,
            html: `
                <h2>Nova Oportunidade Detectada!</h2>
                <p><strong>Tribunal:</strong> ${oportunidade.tribunal}</p>
                <p><strong>Processo:</strong> ${oportunidade.processo}</p>
                <p><strong>Especialidade:</strong> ${oportunidade.especialidade}</p>
                <p><strong>Valor da Causa:</strong> R$ ${oportunidade.valorCausa.toLocaleString('pt-BR')}</p>
                <p><strong>Honorários Estimados:</strong> R$ ${oportunidade.honorariosEstimados.toLocaleString('pt-BR')}</p>
                <p><strong>Prazo:</strong> ${new Date(oportunidade.prazo).toLocaleDateString('pt-BR')}</p>
                <p><strong>Score:</strong> ${oportunidade.score}/100</p>
                <br>
                <a href="http://localhost:3000" style="background: #00d4ff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Ver no Sistema</a>
            `
        };
        
        try {
            await this.transporter.sendMail(mailOptions);
            console.log(`✓ Email enviado para ${email}`);
            return true;
        } catch (error) {
            console.error('Erro ao enviar email:', error);
            return false;
        }
    }
    
    async enviarBemVindo(email, nome) {
        const mailOptions = {
            from: process.env.SMTP_USER,
            to: email,
            subject: '🎉 Bem-vindo ao Sistema de Perícia Judicial',
            html: `
                <h2>Olá ${nome}!</h2>
                <p>Bem-vindo ao Sistema de Perícia Judicial da Tax Master.</p>
                <p>Agora você receberá notificações sobre novas oportunidades de perícia.</p>
                <br>
                <a href="http://localhost:3000" style="background: #00d4ff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Acessar Sistema</a>
            `
        };
        
        await this.transporter.sendMail(mailOptions);
    }
}

module.exports = new EmailService();
