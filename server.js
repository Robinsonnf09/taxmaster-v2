require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Middlewares
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Rotas páginas
app.get('/', (req, res) => res.sendFile(path.join(__dirname, 'public', 'index.html')));
app.get('/dashboard-financeiro.html', (req, res) => res.sendFile(path.join(__dirname, 'public', 'dashboard-financeiro.html')));
app.get('/login.html', (req, res) => res.sendFile(path.join(__dirname, 'public', 'login.html')));
app.get('/precatorios.html', (req, res) => res.sendFile(path.join(__dirname, 'public', 'precatorios.html')));

app.get('/health', (req, res) => {
    res.json({ status: 'OK', message: 'Sistema rodando. Configure DATABASE_URL para ativar funcionalidades completas.' });
});

// Iniciar servidor
app.listen(PORT, '0.0.0.0', () => {
    console.log(`✅ Tax Master V3 rodando na porta ${PORT}`);
    console.log(`⚠️ PostgreSQL não configurado. Adicione DATABASE_URL nas variáveis do Railway.`);
});
