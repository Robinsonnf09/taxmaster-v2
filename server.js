const express = require('express');
const path = require('path');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { buscarDataJudReal, DATAJUD_CONFIG } = require('./busca-datajud-oficial');

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

console.log('✅ Tax Master V3 - Busca REAL CNJ iniciado');
console.log('🔗 API DataJud CNJ: https://api-publica.datajud.cnj.jus.br');
console.log('📋 Credenciais configuradas:', DATAJUD_CONFIG.auth.username ? 'SIM' : 'NÃO');

if (!DATAJUD_CONFIG.auth.username) {
    console.log('');
    console.log('⚠️⚠️⚠️ ATENÇÃO! ⚠️⚠️⚠️');
    console.log('Credenciais DataJud NÃO configuradas!');
    console.log('');
    console.log('COMO CONFIGURAR:');
    console.log('1. Acesse: https://www.cnj.jus.br/sistemas/datajud/api-publica/');
    console.log('2. Crie uma conta');
    console.log('3. Obtenha usuário e senha');
    console.log('4. Configure no Railway:');
    console.log('   - Variável: DATAJUD_USER');
    console.log('   - Variável: DATAJUD_PASS');
    console.log('');
}

// Rotas básicas
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'pages', 'login.html'));
});

app.get('/health', (req, res) => {
    res.json({ 
        status: 'ok', 
        processos: processos.length,
        versao: '3.0.0-datajud-oficial',
        api: 'DataJud CNJ (Documentação Oficial)',
        credenciaisConfiguradas: !!DATAJUD_CONFIG.auth.username,
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

// API de busca REAL oficial
app.get('/api/buscar-tjsp', autenticar, async (req, res) => {
    try {
        if (!DATAJUD_CONFIG.auth.username) {
            return res.json({
                sucesso: false,
                erro: 'credenciais_nao_configuradas',
                mensagem: 'Configure as credenciais DataJud CNJ. Acesse: https://www.cnj.jus.br/sistemas/datajud/api-publica/',
                processos: [],
                total: 0
            });
        }
        
        const filtros = {
            tribunal: req.query.tribunal || 'TJ-SP',
            valorMinimo: req.query.valorMinimo,
            valorMaximo: req.query.valorMaximo,
            natureza: req.query.natureza,
            anoLOA: req.query.anoLOA,
            status: req.query.status,
            quantidade: req.query.quantidade || 50
        };
        
        console.log('\n🔍 Nova busca recebida');
        
        const resultado = await buscarDataJudReal(filtros);
        
        if (resultado.erro === 'autenticacao') {
            return res.status(401).json({
                sucesso: false,
                erro: 'autenticacao',
                mensagem: resultado.mensagem,
                processos: [],
                total: 0
            });
        }
        
        res.json({
            sucesso: true,
            processos: resultado,
            total: resultado.length,
            fonte: 'DataJud CNJ (Oficial)',
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

app.listen(PORT, '0.0.0.0', () => {
    console.log(`\n🚀 Servidor rodando na porta ${PORT}`);
    console.log(`✅ Sistema pronto!`);
});
