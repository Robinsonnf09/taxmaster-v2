const express = require('express');
const path = require('path');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

const app = express();
const PORT = process.env.PORT || 3000;
const JWT_SECRET = 'taxmaster-secret-key-2024-v3';

app.use(express.json());
app.use(express.static('pages'));

// Dados completos em memória
const usuarios = [
    {
        id: 1,
        nome: 'Administrador',
        email: 'admin@taxmaster.com',
        senha: bcrypt.hashSync('admin123', 10),
        perfil: 'admin'
    }
];

const processos = [
    { 
        id: 1, 
        numero: '0001234-56.2024.8.26.0100', 
        tribunal: 'TJ-SP', 
        credor: 'João Silva Santos',
        valor: 150000, 
        status: 'Em Análise',
        natureza: 'Alimentar',
        anoLOA: 2025,
        dataDistribuicao: '15/03/2024'
    },
    { 
        id: 2, 
        numero: '0007890-12.2024.8.26.0100', 
        tribunal: 'TJ-SP', 
        credor: 'Maria Oliveira Costa',
        valor: 250000, 
        status: 'Aprovado',
        natureza: 'Comum',
        anoLOA: 2025,
        dataDistribuicao: '20/05/2024'
    },
    { 
        id: 3, 
        numero: '0003456-78.2024.8.19.0001', 
        tribunal: 'TJ-RJ', 
        credor: 'Pedro Almeida Souza',
        valor: 180000, 
        status: 'Pendente',
        natureza: 'Tributária',
        anoLOA: 2026,
        dataDistribuicao: '10/07/2024'
    },
    { 
        id: 4, 
        numero: '0009876-54.2024.8.26.0100', 
        tribunal: 'TJ-SP', 
        credor: 'Ana Paula Ferreira',
        valor: 320000, 
        status: 'Aprovado',
        natureza: 'Previdenciária',
        anoLOA: 2025,
        dataDistribuicao: '25/08/2024'
    },
    { 
        id: 5, 
        numero: '0005432-10.2024.8.13.0024', 
        tribunal: 'TJ-MG', 
        credor: 'Carlos Eduardo Lima',
        valor: 195000, 
        status: 'Em Análise',
        natureza: 'Trabalhista',
        anoLOA: 2026,
        dataDistribuicao: '05/09/2024'
    }
];

console.log('✅ Sistema iniciado');
console.log(`📊 ${processos.length} processos em memória`);
console.log(`👥 ${usuarios.length} usuário(s) cadastrado(s)`);

// ==========================================
// ROTAS
// ==========================================

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'pages', 'login.html'));
});

app.get('/health', (req, res) => {
    res.json({ 
        status: 'ok', 
        processos: processos.length,
        usuarios: usuarios.length,
        versao: '3.0.0-completo',
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

// Middleware de autenticação
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

app.get('/api/processos', autenticar, (req, res) => {
    const { busca, tribunal, status, natureza, anoLOA } = req.query;
    let resultado = processos;
    
    if (busca) {
        resultado = resultado.filter(p => p.numero.includes(busca));
    }
    
    if (tribunal && tribunal !== 'todos') {
        resultado = resultado.filter(p => p.tribunal === tribunal);
    }
    
    if (status && status !== 'todos') {
        resultado = resultado.filter(p => p.status === status);
    }
    
    if (natureza && natureza !== 'todos') {
        resultado = resultado.filter(p => p.natureza === natureza);
    }
    
    if (anoLOA && anoLOA !== 'todos') {
        resultado = resultado.filter(p => p.anoLOA && p.anoLOA.toString() === anoLOA);
    }
    
    res.json(resultado);
});

app.get('/processos', (req, res) => {
    res.sendFile(path.join(__dirname, 'pages', 'processos.html'));
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 Tax Master V3 rodando na porta ${PORT}`);
    console.log(`✅ Sistema COMPLETO com todos os campos`);
});
