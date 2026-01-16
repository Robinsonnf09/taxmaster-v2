const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcryptjs');

console.log('🔐 Criando sistema de autenticação...\n');

const db = new sqlite3.Database('./taxmaster.db');

// Criar tabela de usuários
db.run(`
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        perfil TEXT NOT NULL DEFAULT 'visualizador',
        ativo INTEGER DEFAULT 1,
        criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
        ultimo_acesso DATETIME
    )
`, (err) => {
    if (err) console.error('❌ Erro ao criar tabela usuarios:', err);
    else console.log('✅ Tabela usuarios criada!\n');
});

// Criar tabela de logs de auditoria
db.run(`
    CREATE TABLE IF NOT EXISTS logs_auditoria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        acao TEXT NOT NULL,
        detalhes TEXT,
        ip TEXT,
        data DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    )
`, (err) => {
    if (err) console.error('❌ Erro ao criar tabela logs:', err);
    else console.log('✅ Tabela logs_auditoria criada!\n');
});

// Criar tabela de notificações
db.run(`
    CREATE TABLE IF NOT EXISTS notificacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        titulo TEXT NOT NULL,
        mensagem TEXT NOT NULL,
        tipo TEXT DEFAULT 'info',
        lida INTEGER DEFAULT 0,
        criada_em DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    )
`, (err) => {
    if (err) console.error('❌ Erro ao criar tabela notificacoes:', err);
    else console.log('✅ Tabela notificacoes criada!\n');
});

// Criar usuário admin padrão
setTimeout(() => {
    const senhaHash = bcrypt.hashSync('admin123', 10);
    
    db.run(`
        INSERT OR IGNORE INTO usuarios (nome, email, senha, perfil)
        VALUES (?, ?, ?, ?)
    `, ['Administrador', 'admin@taxmaster.com', senhaHash, 'admin'], (err) => {
        if (err) console.error('❌ Erro ao criar admin:', err);
        else {
            console.log('✅ Usuário admin criado!\n');
            console.log('📧 Email: admin@taxmaster.com');
            console.log('🔑 Senha: admin123\n');
        }
        db.close();
    });
}, 1000);
