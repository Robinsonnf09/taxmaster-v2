const express = require('express');
const path = require('path');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

const app = express();
const PORT = process.env.PORT || 3000;
const JWT_SECRET = 'taxmaster-secret-key-2024-v3';

app.use(express.json());
app.use(express.static('pages'));

// Dados em memória (temporário)
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
    { id: 1, numero: '0001234-56.2024.8.26.0100', tribunal: 'TJ-SP', valor: 150000, status: 'Em Análise' },
    { id: 2, numero: '0007890-12.2024.8.26.0100', tribunal: 'TJ-SP', valor: 250000, status: 'Aprovado' },
    { id: 3, numero: '0003456-78.2024.8.26.0100', tribunal: 'TJ-RJ', valor: 180000, status: 'Pendente' }
];

console.log('✅ Sistema iniciado');
console.log(`📊 ${processos.length} processos em memória`);

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
        versao: '3.0.0-minimal',
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

app.get('/api/processos', (req, res) => {
    res.json(processos);
});

app.get('/processos', (req, res) => {
    res.sendFile(path.join(__dirname, 'pages', 'processos.html'));
});

// ==========================================
// INICIAR
// ==========================================

app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 Tax Master V3 rodando na porta ${PORT}`);
    console.log(`✅ Sistema MINIMALISTA ativo`);
});
