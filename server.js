const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 3000;

// Middlewares
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Rotas
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/dashboard-financeiro.html', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'dashboard-financeiro.html'));
});

app.get('/health', (req, res) => {
    res.json({ 
        status: 'OK', 
        service: 'Tax Master V3',
        features: ['Dashboard Financeiro', 'Gestão de Receitas', 'Gestão de Despesas', 'Relatórios']
    });
});

// Iniciar servidor
app.listen(PORT, '0.0.0.0', () => {
    console.log(`✅ Tax Master V3 rodando na porta ${PORT}`);
    console.log(`🌐 Funcionalidades: Dashboard Financeiro, Receitas, Despesas, Relatórios`);
});
