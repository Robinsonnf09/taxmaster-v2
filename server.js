const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.static(__dirname));

// ============================================
// DADOS MOCK EMBUTIDOS (100 processos)
// ============================================
const processos = [];
const tribunais = [
    { sigla: 'TJ-BA', codigo: '8.05' },
    { sigla: 'TJ-SP', codigo: '8.26' },
    { sigla: 'TJ-RJ', codigo: '8.19' },
    { sigla: 'TJ-MG', codigo: '8.13' },
    { sigla: 'TJ-RS', codigo: '8.21' }
];

for (let i = 0; i < 100; i++) {
    const trib = tribunais[Math.floor(Math.random() * 5)];
    const ano = 2020 + Math.floor(Math.random() * 5);
    const seq = (1000000 + i).toString().padStart(7, '0');
    const num = `${seq}-${String(Math.floor(Math.random()*100)).padStart(2,'0')}.${ano}.${trib.codigo}.${String(Math.floor(Math.random()*9999)).padStart(4,'0')}`;
    
    processos.push({
        id: i + 1,
        numero: num,
        tribunal: trib.sigla,
        credor: ['João Silva Santos','Maria Costa','José Lima','Ana Ferreira','Carlos Souza'][i % 5],
        valor: Math.round((30000 + Math.random() * 500000) * 100) / 100,
        status: ['Pendente','Em Análise','Aprovado','Aguardando Pagamento','Quitado'][i % 5],
        dataDistribuicao: new Date(ano, Math.floor(Math.random()*12), Math.floor(Math.random()*28)+1).toISOString().split('T')[0]
    });
}

console.log(`✅ ${processos.length} processos carregados!`);

// ROTAS
app.get('/', (req, res) => res.sendFile(path.join(__dirname, 'index.html')));

app.get('/processos', (req, res) => {
    const file = path.join(__dirname, 'pages', 'processos.html');
    res.sendFile(file, err => { if(err) res.sendFile(path.join(__dirname, 'index.html')); });
});

app.get('/api/processos', (req, res) => {
    let result = [...processos];
    if (req.query.tribunal) result = result.filter(p => p.tribunal === req.query.tribunal);
    if (req.query.status) result = result.filter(p => p.status === req.query.status);
    if (req.query.busca) {
        const t = req.query.busca.toLowerCase();
        result = result.filter(p => p.numero.toLowerCase().includes(t) || p.credor.toLowerCase().includes(t));
    }
    res.json(result);
});

app.get('/api/estatisticas', (req, res) => {
    res.json({ 
        total: processos.length, 
        valorTotal: processos.reduce((sum, p) => sum + p.valor, 0) 
    });
});

app.get('/health', (req, res) => {
    res.json({ status: 'OK', timestamp: new Date().toISOString(), processos: processos.length });
});

// CRÍTICO: Bind para 0.0.0.0 (Railway precisa disso!)
app.listen(PORT, '0.0.0.0', () => {
    console.log(`✅ Tax Master na porta ${PORT} | ${processos.length} processos`);
});

module.exports = app;
