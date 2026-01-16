const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const nodemailer = require('nodemailer');
const cron = require('node-cron');
const { enviarEmail, notificarNovoProcesso, enviarRelatorioSemanal } = require('./email-service');
const { autenticar, autorizarPerfil, JWT_SECRET } = require('./middleware-auth');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static('pages'));
app.use(express.static('public'));

const db = new sqlite3.Database('./taxmaster.db');

let processos = [];

// Carregar processos do banco
db.all('SELECT * FROM processos', (err, rows) => {
    if (!err) processos = rows;
    console.log(`✅ ${processos.length} processos carregados`);
});

// ==========================================
// ROTAS DE AUTENTICAÇÃO
// ==========================================

app.post('/api/auth/login', (req, res) => {
    const { email, senha } = req.body;
    
    db.get('SELECT * FROM usuarios WHERE email = ? AND ativo = 1', [email], (err, usuario) => {
        if (err || !usuario) {
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
        
        // Atualizar último acesso
        db.run('UPDATE usuarios SET ultimo_acesso = CURRENT_TIMESTAMP WHERE id = ?', [usuario.id]);
        
        // Registrar log
        db.run('INSERT INTO logs_auditoria (usuario_id, acao) VALUES (?, ?)', [usuario.id, 'LOGIN']);
        
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

// Rota para dashboard BI (Admin e Gerente)
app.get('/api/bi/estatisticas', autenticar, autorizarPerfil('admin', 'gerente'), (req, res) => {
    const stats = {
        totalProcessos: processos.length,
        valorTotal: processos.reduce((sum, p) => sum + parseFloat(p.valor || 0), 0),
        porTribunal: {},
        porStatus: {},
        porNatureza: {},
        porAno: {}
    };
    
    processos.forEach(p => {
        stats.porTribunal[p.tribunal] = (stats.porTribunal[p.tribunal] || 0) + 1;
        stats.porStatus[p.status] = (stats.porStatus[p.status] || 0) + 1;
        if (p.natureza) stats.porNatureza[p.natureza] = (stats.porNatureza[p.natureza] || 0) + 1;
        if (p.anoLOA) stats.porAno[p.anoLOA] = (stats.porAno[p.anoLOA] || 0) + 1;
    });
    
    res.json(stats);
});

// Rota para usuários (Admin apenas)
app.get('/api/usuarios', autenticar, autorizarPerfil('admin'), (req, res) => {
    db.all('SELECT id, nome, email, perfil, ativo, criado_em, ultimo_acesso FROM usuarios', (err, usuarios) => {
        if (err) return res.status(500).json({ erro: 'Erro ao buscar usuários' });
        res.json(usuarios);
    });
});

// ==========================================
// AUTOMAÇÃO DIÁRIA
// ==========================================

cron.schedule('0 8 * * *', () => {
    console.log('🤖 Executando busca automatizada diária...');
    // Aqui você pode chamar o script de busca TJ-SP
    const { exec } = require('child_process');
    exec('node buscar-tjsp-ampliado.js 50', (error, stdout) => {
        if (error) {
            console.error('❌ Erro na busca automatizada:', error);
        } else {
            console.log('✅ Busca automatizada concluída!');
            console.log(stdout);
        }
    });
});

// ==========================================
// ROTAS DE PÁGINAS
// ==========================================

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'pages', 'login.html'));
});

app.get('/login', (req, res) => {
    res.sendFile(path.join(__dirname, 'pages', 'login.html'));
});

app.get('/processos', (req, res) => {
    res.sendFile(path.join(__dirname, 'pages', 'processos.html'));
});

app.get('/dashboard', (req, res) => {
    res.sendFile(path.join(__dirname, 'pages', 'dashboard.html'));
});

app.get('/health', (req, res) => {
    res.json({ 
        status: 'ok', 
        processos: processos.length,
        versao: '3.0.0'
    });
});


app.get('/usuarios', autenticar, autorizarPerfil('admin'), (req, res) => {
    res.sendFile(path.join(__dirname, 'pages', 'usuarios.html'));
});

// Relatório semanal automatizado (toda segunda às 8h)
cron.schedule('0 8 * * 1', () => {
    console.log('📧 Enviando relatórios semanais...');
    db.all('SELECT * FROM usuarios WHERE ativo = 1 AND perfil IN ("admin", "gerente")', (err, usuarios) => {
        if (!err && usuarios) {
            const stats = {
                total: processos.length,
                novos: processos.filter(p => {
                    const data = new Date(p.dataDistribuicao);
                    const semanaAtras = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
                    return data >= semanaAtras;
                }).length,
                valorTotal: processos.reduce((sum, p) => sum + parseFloat(p.valor || 0), 0)
            };
            
            usuarios.forEach(usuario => {
                enviarRelatorioSemanal(usuario, stats);
            });
        }
    });
});

app.listen(PORT, () => {
    console.log(`🚀 Tax Master V3 rodando na porta ${PORT}`);
    console.log(`🔐 Sistema de autenticação: ATIVO`);
    console.log(`🤖 Automação diária: ATIVA (8h da manhã)`);
});

