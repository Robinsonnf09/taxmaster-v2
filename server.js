const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

const app = express();
const PORT = process.env.PORT || 3000;
const JWT_SECRET = process.env.JWT_SECRET || 'taxmaster-secret-key-2024-v3';

app.use(express.json());
app.use(express.static('pages'));
app.use(express.static('public'));

// Inicializar banco de dados
const db = new sqlite3.Database('./taxmaster.db', (err) => {
    if (err) {
        console.error('❌ Erro ao conectar ao banco:', err);
    } else {
        console.log('✅ Banco de dados conectado');
        inicializarBanco();
    }
});

let processos = [];

function inicializarBanco() {
    // Criar tabela de processos
    db.run(`
        CREATE TABLE IF NOT EXISTS processos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT,
            tribunal TEXT,
            credor TEXT,
            valor REAL,
            status TEXT,
            dataDistribuicao TEXT,
            natureza TEXT,
            anoLOA INTEGER
        )
    `, () => {
        console.log('✅ Tabela processos OK');
    });
    
    // Criar tabela de usuários
    db.run(`
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            perfil TEXT DEFAULT 'visualizador',
            ativo INTEGER DEFAULT 1,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            ultimo_acesso DATETIME
        )
    `, () => {
        console.log('✅ Tabela usuarios OK');
        
        // Criar admin padrão
        const senhaHash = bcrypt.hashSync('admin123', 10);
        db.run(`
            INSERT OR IGNORE INTO usuarios (id, nome, email, senha, perfil)
            VALUES (1, 'Administrador', 'admin@taxmaster.com', ?, 'admin')
        `, [senhaHash], () => {
            console.log('✅ Usuário admin criado');
        });
    });
    
    // Carregar processos
    db.all('SELECT * FROM processos', (err, rows) => {
        if (!err && rows) {
            processos = rows;
            console.log(`✅ ${processos.length} processos carregados`);
        }
    });
}

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

// Middleware de autorização
function autorizarPerfil(...perfisPermitidos) {
    return (req, res, next) => {
        if (!perfisPermitidos.includes(req.usuario.perfil)) {
            return res.status(403).json({ erro: 'Acesso negado' });
        }
        next();
    };
}

// ==========================================
// ROTAS PÚBLICAS
// ==========================================

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'pages', 'login.html'));
});

app.get('/login', (req, res) => {
    res.sendFile(path.join(__dirname, 'pages', 'login.html'));
});

app.get('/health', (req, res) => {
    res.json({ 
        status: 'ok', 
        processos: processos.length,
        versao: '3.0.0',
        timestamp: new Date().toISOString()
    });
});

// Rota de login
app.post('/api/auth/login', (req, res) => {
    const { email, senha } = req.body;
    
    if (!email || !senha) {
        return res.status(400).json({ erro: 'Email e senha são obrigatórios' });
    }
    
    db.get('SELECT * FROM usuarios WHERE email = ? AND ativo = 1', [email], (err, usuario) => {
        if (err) {
            console.error('Erro ao buscar usuário:', err);
            return res.status(500).json({ erro: 'Erro interno' });
        }
        
        if (!usuario) {
            return res.status(401).json({ erro: 'Credenciais inválidas' });
        }
        
        const senhaValida = bcrypt.compareSync(senha, usuario.senha);
        
        if (!senhaValida) {
            return res.status(401).json({ erro: 'Credenciais inválidas' });
        }
        
        const token = jwt.sign(
            { id: usuario.id, email: usuario.email, perfil: usuario.perfil },
            JWT_SECRET,
            { expiresIn: '24h' }
        );
        
        db.run('UPDATE usuarios SET ultimo_acesso = CURRENT_TIMESTAMP WHERE id = ?', [usuario.id]);
        
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
});

// ==========================================
// ROTAS PROTEGIDAS
// ==========================================

app.get('/processos', (req, res) => {
    res.sendFile(path.join(__dirname, 'pages', 'processos.html'));
});

app.get('/dashboard', (req, res) => {
    res.sendFile(path.join(__dirname, 'pages', 'dashboard.html'));
});

app.get('/usuarios', autenticar, autorizarPerfil('admin'), (req, res) => {
    res.sendFile(path.join(__dirname, 'pages', 'usuarios.html'));
});

// API de processos
app.get('/api/processos', autenticar, (req, res) => {
    const { busca, tribunal, status, natureza, anoLOA, valorMinimo, valorMaximo } = req.query;
    let processosFiltrados = processos;
    
    if (busca) {
        processosFiltrados = processosFiltrados.filter(p => 
            p.numero && p.numero.includes(busca)
        );
    }
    
    if (tribunal && tribunal !== 'todos') {
        processosFiltrados = processosFiltrados.filter(p => p.tribunal === tribunal);
    }
    
    if (status && status !== 'todos') {
        processosFiltrados = processosFiltrados.filter(p => p.status === status);
    }
    
    if (natureza && natureza !== 'todos') {
        processosFiltrados = processosFiltrados.filter(p => p.natureza === natureza);
    }
    
    if (anoLOA && anoLOA !== 'todos') {
        processosFiltrados = processosFiltrados.filter(p => p.anoLOA && p.anoLOA.toString() === anoLOA);
    }
    
    if (valorMinimo) {
        processosFiltrados = processosFiltrados.filter(p => parseFloat(p.valor) >= parseFloat(valorMinimo));
    }
    
    if (valorMaximo) {
        processosFiltrados = processosFiltrados.filter(p => parseFloat(p.valor) <= parseFloat(valorMaximo));
    }
    
    res.json(processosFiltrados);
});

// API de usuários
app.get('/api/usuarios', autenticar, autorizarPerfil('admin'), (req, res) => {
    db.all('SELECT id, nome, email, perfil, ativo, criado_em, ultimo_acesso FROM usuarios', (err, usuarios) => {
        if (err) {
            console.error('Erro ao buscar usuários:', err);
            return res.status(500).json({ erro: 'Erro ao buscar usuários' });
        }
        res.json(usuarios);
    });
});

// ==========================================
// INICIAR SERVIDOR
// ==========================================

app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 Tax Master V3 rodando na porta ${PORT}`);
    console.log(`🔐 Sistema de autenticação: ATIVO`);
    console.log(`📊 Processos no banco: ${processos.length}`);
});

// Tratamento de erros
process.on('uncaughtException', (error) => {
    console.error('❌ Erro não capturado:', error);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('❌ Promise rejeitada:', reason);
});
// Última atualização: 01/16/2026 20:40:14
