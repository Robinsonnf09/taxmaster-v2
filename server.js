const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname)));

// Conectar ao banco SQLite
const db = new sqlite3.Database('./taxmaster.db', (err) => {
    if (err) {
        console.error('❌ Erro ao conectar banco:', err);
    } else {
        console.log('✅ Conectado ao taxmaster.db');
    }
});

// Contar processos no banco
db.get('SELECT COUNT(*) as total FROM processos', (err, row) => {
    if (err) {
        console.error('❌ Erro ao contar processos:', err);
    } else {
        console.log(`✅ ${row.total} processos reais carregados do banco!`);
    }
});

// Rotas
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.get('/processos', (req, res) => {
    res.sendFile(path.join(__dirname, 'pages', 'processos.html'), (err) => {
        if (err) res.sendFile(path.join(__dirname, 'index.html'));
    });
});

// API: Buscar processos REAIS do banco
app.get('/api/processos', (req, res) => {
    let query = 'SELECT * FROM processos WHERE 1=1';
    const params = [];
    
    // Filtros
    if (req.query.tribunal) {
        query += ' AND tribunal = ?';
        params.push(req.query.tribunal);
    }
    
    if (req.query.status) {
        query += ' AND status = ?';
        params.push(req.query.status);
    }
    
    if (req.query.busca) {
        query += ' AND (numero LIKE ? OR credor LIKE ?)';
        const termo = `%${req.query.busca}%`;
        params.push(termo, termo);
    }
    
    db.all(query, params, (err, rows) => {
        if (err) {
            console.error('❌ Erro ao buscar processos:', err);
            res.status(500).json({ error: err.message });
        } else {
            res.json(rows);
        }
    });
});

// API: Estatísticas
app.get('/api/estatisticas', (req, res) => {
    db.get('SELECT COUNT(*) as total, SUM(valor) as valorTotal FROM processos', (err, row) => {
        if (err) {
            res.status(500).json({ error: err.message });
        } else {
            res.json({
                total: row.total,
                valorTotal: row.valorTotal || 0
            });
        }
    });
});

// Health check
app.get('/health', (req, res) => {
    db.get('SELECT COUNT(*) as total FROM processos', (err, row) => {
        if (err) {
            res.status(500).json({ status: 'ERROR', error: err.message });
        } else {
            res.json({
                status: 'OK',
                timestamp: new Date().toISOString(),
                processos: row.total,
                fonte: 'taxmaster.db (DADOS REAIS)'
            });
        }
    });
});

// Iniciar servidor
app.listen(PORT, '0.0.0.0', () => {
    console.log(`✅ Tax Master na porta ${PORT}`);
    console.log(`📊 Usando banco de dados REAL: taxmaster.db`);
});
