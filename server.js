require('dotenv').config();
const express = require('express');
const path = require('path');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { buscarProcessosESAJ } = require('./esajScraper');

const app = express();
const PORT = process.env.PORT || 3000;
const JWT_SECRET = 'taxmaster-secret-key-2024-v3';

app.use(express.json());
app.use(express.static('pages'));

const usuarios = [
    { id: 1, nome: 'Administrador', email: 'admin@taxmaster.com', senha: bcrypt.hashSync('admin123', 10), perfil: 'admin' }
];

let processos = [];

console.log('✅ Tax Master V3 - API CNJ DataJud');
console.log('🔍 Fonte: API CNJ DataJud (Oficial)');
console.log('⚠️ Delay de 2s entre requisições');

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'pages', 'login.html'));
});

app.get('/health', (req, res) => {
    res.json({ 
        status: 'ok', 
        processos: processos.length, 
        versao: '3.0.0-esaj-real', 
        fonte: 'ESAJ TJ-SP (Scraping Real)',
        timestamp: new Date().toISOString() 
    });
});

app.post('/api/auth/login', (req, res) => {
    const { email, senha } = req.body;
    const usuario = usuarios.find(u => u.email === email);
    
    if (!usuario || !bcrypt.compareSync(senha, usuario.senha)) {
        return res.status(401).json({ erro: 'Credenciais inválidas' });
    }
    
    const token = jwt.sign({ id: usuario.id, email: usuario.email, perfil: usuario.perfil }, JWT_SECRET, { expiresIn: '24h' });
    
    res.json({ token, usuario: { id: usuario.id, nome: usuario.nome, email: usuario.email, perfil: usuario.perfil } });
});

function autenticar(req, res, next) {
    const token = req.headers.authorization?.replace('Bearer ', '');
    if (!token) return res.status(401).json({ erro: 'Token não fornecido' });
    
    try {
        const decoded = jwt.verify(token, JWT_SECRET);
        req.usuario = decoded;
        next();
    } catch (error) {
        return res.status(401).json({ erro: 'Token inválido' });
    }
}

app.get('/api/buscar-processos-oficiais', autenticar, async (req, res) => {
    try {
        const { tribunal, valorMinimo, valorMaximo, natureza, anoLOA } = req.query;

        console.log('\n📥 Nova busca REAL no ESAJ:');
        console.log('   Valor:', valorMinimo || '0', '-', valorMaximo || '∞');
        console.log('   Natureza:', natureza || 'Todas');

        const resultado = await buscarProcessosESAJ({
            valorMin: valorMinimo ? Number(valorMinimo) : null,
            valorMax: valorMaximo ? Number(valorMaximo) : null,
            natureza,
            quantidade: 30 // Limitar para não demorar muito
        });

        let sugestoes = [];
        if (resultado.processos.length === 0) {
            sugestoes.push('💡 Nenhum processo encontrado com os filtros');
            sugestoes.push('💡 Tente relaxar os filtros ou aguarde nova busca');
        } else if (resultado.processos.length < 5) {
            sugestoes.push(`💡 Apenas ${resultado.processos.length} processos encontrados`);
            sugestoes.push('💡 Busca com mais processos pode demorar alguns minutos');
        }

        res.json({
            sucesso: true,
            total: resultado.processos.length,
            processos: resultado.processos,
            stats: resultado.stats,
            sugestoes: sugestoes,
            fonte: 'ESAJ TJ-SP (Scraping Real)',
            aviso: 'Dados REAIS extraídos do ESAJ - Delay de 2s entre requisições'
        });
    } catch (err) {
        console.error(err);
        res.status(500).json({ erro: 'Erro ao buscar processos', mensagem: err.message });
    }
});

app.get('/api/buscar-tjsp', autenticar, (req, res) => {
    req.url = '/api/buscar-processos-oficiais';
    app.handle(req, res);
});

app.post('/api/processos/importar', autenticar, (req, res) => {
    const processo = req.body;
    processo.id = processos.length + 1;
    processos.push(processo);
    res.json({ sucesso: true, mensagem: 'Processo importado', id: processo.id });
});

app.get('/api/processos', autenticar, (req, res) => {
    res.json(processos);
});

app.get('/processos', (req, res) => {
    res.sendFile(path.join(__dirname, 'pages', 'processos.html'));
});

app.get('/importar', (req, res) => {
    res.sendFile(path.join(__dirname, 'pages', 'importar.html'));
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 Servidor na porta ${PORT}`);
    console.log('✅ Sistema pronto com API CNJ DataJud!');
});


