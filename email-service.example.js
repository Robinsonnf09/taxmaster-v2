// email-service.example.js
// COPIE PARA email-service.js E CONFIGURE COM SUAS CREDENCIAIS REAIS

const nodemailer = require('nodemailer');

const transporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST || 'smtp.gmail.com',
  port: process.env.SMTP_PORT || 587,
  secure: false,
  auth: {
    user: process.env.SMTP_USER || 'seu-email@example.com',
    pass: process.env.SMTP_PASS || 'sua-senha-aqui'
  }
});

module.exports = transporter;
