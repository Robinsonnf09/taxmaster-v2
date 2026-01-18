require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const { initDatabase } = require('./database/config');

const app = express();
const PORT = process.env.PORT || 3000;

// Middlewares
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

// Rotas API
app.use('/api/auth', require('./routes/auth'));
app.use('/api/precatorios', require('./routes/precatorios'));
app.use('/api/financeiro', require('./routes/financeiro'));
app.use('/api/oportunidades', require('./routes/oportunidades'));

// Rotas páginas
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/dashboard-financeiro.html', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'dashboard-financeiro.html'));
});

app.get('/login.html', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'login.html'));
});

app.get('/precatorios.html', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'precatorios.html'));
});

app.get('/oportunidades.html', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'oportunidades.html'));
});

app.get('/health', (req, res) => {
    res.json({ 
        status: 'OK', 
        service: 'Tax Master V3',
        version: '3.0.0',
        features: [
            'Dashboard Financeiro', 
            'Gestão de Precatórios',
            'Catálogo de Oportunidades',
            'Autenticação JWT',
            'PostgreSQL Database'
        ]
    });
});

// Iniciar servidor e banco
async function start() {
    try {
        await initDatabase();
        app.listen(PORT, '0.0.0.0', () => {
            console.log(`✅ Tax Master V3 rodando na porta ${PORT}`);
            console.log(`🗄️ Banco de dados: ${process.env.DATABASE_URL ? 'PostgreSQL Railway' : 'Configurar DATABASE_URL'}`);
            console.log(`🔐 Autenticação: JWT habilitado`);
            console.log(`🌐 Funcionalidades completas ativadas`);
        });
    } catch (error) {
        console.error('❌ Erro ao iniciar servidor:', error);
        process.exit(1);
    }
}

start();
