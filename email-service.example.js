// email-service.example.js - Tax Master V3
// INSTRUÇÕES:
// 1. Copie este arquivo para email-service.js
// 2. Configure as variáveis no arquivo .env
// 3. NUNCA commite o arquivo email-service.js

const nodemailer = require('nodemailer');

const transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST || 'smtp.gmail.com',
    port: parseInt(process.env.SMTP_PORT) || 587,
    secure: false,
    auth: {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASS
    }
});

transporter.verify((error, success) => {
    if (error) {
        console.error('❌ Erro SMTP:', error);
    } else {
        console.log('✅ SMTP pronto');
    }
});

module.exports = transporter;
