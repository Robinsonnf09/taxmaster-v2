const express = require('express');
const path = require('path');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { buscarProcessosReais } = require('./busca-real');

const app = express();
const PORT = process.env.PORT || 3000;
const JWT_SECRET = 'taxmaster-secret-key-2024-v3';

app.use(express.json());
app.use(express.static('pages'));

const usuarios = [
    {
        id: 1,
        nome: 'Administrador',
        email: 'admin@taxmaster.com',
        senha: bcrypt.hashSync('admin123', 10),
        perfil: 'admin'
    }
];

let processos = [];

console.log('✅ Tax Master V3 iniciado');
console.log('🔥 Sistema de busca REAL ativo');
console.log('   • Puppeteer (Scraping TJ-SP)');
console.log('   • API DataJud CNJ');
console.log('   • Cache inteligente');
console.log('   • Retry automático');

// ==========================================
// ROTAS BÁSICAS
// ==========================================

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'pages', 'login.html'));
});

app.get('/health', (req, res) => {
    res.json({ 
        status: 'ok', 
        processos: processos.length,
        versao: '3.0.0-real-search',
        features: [
            'Busca Real TJ-SP',
            'API DataJud CNJ',
            'Scraping Robusto',
            'Cache 1h',
            'Retry Logic'
        ],
        timestamp: new Date().toISOString()
    });
});

app.post('/api/auth/login', (req, res) => {
    const { email, senha } = req.body;
    const usuario = usuarios.find(u => u.email === email);
    
    if (!usuario || !bcrypt.compareSync(senha, usuario.senha)) {
        return res.status(401).json({ erro: 'Credenciais inválidas' });
    }
    
    const token = jwt.sign(
        { id: usuario.id, email: usuario.email, perfil: usuario.perfil },
        JWT_SECRET,
        { expiresIn: '24h' }
    );
    
    res.json({
        token,
        usuario: {
            id: usuario.id,
            nome: usuario.nome,
            email: usuario.email,
            perfil: usuario.perfil
        }
    });
});

function autenticar(req, res, next) {
    const token = req.headers.authorization?.replace('Bearer ', '');
    
    if (!token) {
        return res.status(401).json({ erro: 'Token não fornecido' });
    }
    
    try {
        const decoded = jwt.verify(token, JWT_SECRET);
        req.usuario = decoded;
        next();
    } catch (error) {
        return res.status(401).json({ erro: 'Token inválido' });
    }
}

// ==========================================
// API DE BUSCA REAL
// ==========================================

app.get('/api/buscar-tjsp', autenticar, async (req, res) => {
    try {
        const filtros = {
            tribunal: req.query.tribunal || 'TJ-SP',
            valorMinimo: req.query.valorMinimo,
            valorMaximo: req.query.valorMaximo,
            natureza: req.query.natureza,
            anoLOA: req.query.anoLOA,
            status: req.query.status,
            quantidade: req.query.quantidade || 50
        };
        
        console.log('\n🔍 Nova busca recebida:', filtros);
        
        const resultado = await buscarProcessosReais(filtros);
        
        res.json({
            sucesso: true,
            processos: resultado.processos,
            total: resultado.processos.length,
            fonte: resultado.fonte,
            mensagem: resultado.mensagem,
            tribunal: filtros.tribunal
        });
        
    } catch (error) {
        console.error('❌ Erro na busca:', error);
        res.status(500).json({ 
            erro: 'Erro ao buscar processos',
            mensagem: error.message 
        });
    }
});

app.post('/api/processos/importar', autenticar, (req, res) => {
    const processo = req.body;
    processo.id = processos.length + 1;
    processos.push(processo);
    
    console.log(`📥 Processo importado: ${processo.numero}`);
    
    res.json({
        sucesso: true,
        mensagem: 'Processo importado com sucesso',
        id: processo.id
    });
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

// ==========================================
// INICIAR SERVIDOR
// ==========================================

app.listen(PORT, '0.0.0.0', () => {
    console.log(`\n🚀 Tax Master V3 rodando na porta ${PORT}`);
    console.log(`🔥 Sistema de busca REAL em produção`);
    console.log(`✅ Pronto para uso!`);
});
