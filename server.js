require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const { Pool } = require('pg');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');

const app = express();
const PORT = process.env.PORT || 8080;
const JWT_SECRET = process.env.JWT_SECRET || 'taxmaster_secret_2026';

// PostgreSQL
const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

// Criar tabelas
async function initDB() {
    try {
        await pool.query(`
            CREATE TABLE IF NOT EXISTS processos (
                id SERIAL PRIMARY KEY,
                numero VARCHAR(50) UNIQUE NOT NULL,
                tribunal VARCHAR(100),
                tipo VARCHAR(100),
                natureza VARCHAR(50),
                valor_principal DECIMAL(15,2),
                juros DECIMAL(15,2),
                valor_total DECIMAL(15,2),
                status VARCHAR(50),
                data_expedicao DATE,
                beneficiario VARCHAR(255),
                cpf_cnpj VARCHAR(20),
                advogado VARCHAR(255),
                oab VARCHAR(20),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                senha VARCHAR(255) NOT NULL,
                nome VARCHAR(255),
                tipo VARCHAR(50) DEFAULT 'usuario',
                created_at TIMESTAMP DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS movimentacoes (
                id SERIAL PRIMARY KEY,
                processo_id INTEGER REFERENCES processos(id),
                tipo VARCHAR(50),
                descricao TEXT,
                valor DECIMAL(15,2),
                data DATE,
                created_at TIMESTAMP DEFAULT NOW()
            );
        `);
        console.log('✅ Banco de dados: PostgreSQL Railway');
        console.log('✅ Tabelas criadas/verificadas');
    } catch (err) {
        console.error('❌ Erro no banco:', err.message);
    }
}

// Middleware de autenticação
function authMiddleware(req, res, next) {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) return res.status(401).json({ error: 'Token não fornecido' });
    
    try {
        const decoded = jwt.verify(token, JWT_SECRET);
        req.userId = decoded.id;
        next();
    } catch (err) {
        res.status(401).json({ error: 'Token inválido' });
    }
}

// Middlewares
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Rotas públicas
app.get('/', (req, res) => res.sendFile(path.join(__dirname, 'public', 'index.html')));
app.get('/login.html', (req, res) => res.sendFile(path.join(__dirname, 'public', 'login.html')));
app.get('/dashboard-financeiro.html', (req, res) => res.sendFile(path.join(__dirname, 'public', 'dashboard-financeiro.html')));
app.get('/precatorios.html', (req, res) => res.sendFile(path.join(__dirname, 'public', 'precatorios.html')));

app.get('/health', (req, res) => res.json({ status: 'OK', database: 'PostgreSQL' }));

// Autenticação
app.post('/api/auth/register', async (req, res) => {
    const { email, senha, nome } = req.body;
    try {
        const hashedPassword = await bcrypt.hash(senha, 10);
        const result = await pool.query(
            'INSERT INTO usuarios (email, senha, nome) VALUES ($1, $2, $3) RETURNING id, email, nome',
            [email, hashedPassword, nome]
        );
        res.json(result.rows[0]);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.post('/api/auth/login', async (req, res) => {
    const { email, senha } = req.body;
    try {
        const result = await pool.query('SELECT * FROM usuarios WHERE email = $1', [email]);
        if (result.rows.length === 0) {
            return res.status(401).json({ error: 'Credenciais inválidas' });
        }
        
        const user = result.rows[0];
        const validPassword = await bcrypt.compare(senha, user.senha);
        
        if (!validPassword) {
            return res.status(401).json({ error: 'Credenciais inválidas' });
        }
        
        const token = jwt.sign({ id: user.id, email: user.email }, JWT_SECRET, { expiresIn: '24h' });
        res.json({ token, user: { id: user.id, email: user.email, nome: user.nome } });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Processos - CRUD completo
app.get('/api/processos', async (req, res) => {
    try {
        const { status, tribunal, search, limit = 100 } = req.query;
        let query = 'SELECT * FROM processos WHERE 1=1';
        const params = [];
        
        if (status) {
            params.push(status);
            query += ` AND status = $${params.length}`;
        }
        if (tribunal) {
            params.push(tribunal);
            query += ` AND tribunal ILIKE $${params.length}`;
        }
        if (search) {
            params.push(`%${search}%`);
            query += ` AND (numero ILIKE $${params.length} OR beneficiario ILIKE $${params.length})`;
        }
        
        query += ` ORDER BY created_at DESC LIMIT ${limit}`;
        
        const result = await pool.query(query, params);
        res.json(result.rows);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.get('/api/processos/:id', async (req, res) => {
    try {
        const result = await pool.query('SELECT * FROM processos WHERE id = $1', [req.params.id]);
        if (result.rows.length === 0) {
            return res.status(404).json({ error: 'Processo não encontrado' });
        }
        res.json(result.rows[0]);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.post('/api/processos', async (req, res) => {
    const { numero, tribunal, tipo, natureza, valor_principal, juros, valor_total, status, data_expedicao, beneficiario, cpf_cnpj, advogado, oab } = req.body;
    try {
        const result = await pool.query(
            `INSERT INTO processos (numero, tribunal, tipo, natureza, valor_principal, juros, valor_total, status, data_expedicao, beneficiario, cpf_cnpj, advogado, oab) 
             VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13) RETURNING *`,
            [numero, tribunal, tipo, natureza, valor_principal, juros, valor_total, status, data_expedicao, beneficiario, cpf_cnpj, advogado, oab]
        );
        res.json(result.rows[0]);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.put('/api/processos/:id', async (req, res) => {
    const { numero, tribunal, tipo, natureza, valor_principal, juros, valor_total, status, data_expedicao, beneficiario, cpf_cnpj, advogado, oab } = req.body;
    try {
        const result = await pool.query(
            `UPDATE processos SET numero=$1, tribunal=$2, tipo=$3, natureza=$4, valor_principal=$5, juros=$6, valor_total=$7, 
             status=$8, data_expedicao=$9, beneficiario=$10, cpf_cnpj=$11, advogado=$12, oab=$13, updated_at=NOW() 
             WHERE id=$14 RETURNING *`,
            [numero, tribunal, tipo, natureza, valor_principal, juros, valor_total, status, data_expedicao, beneficiario, cpf_cnpj, advogado, oab, req.params.id]
        );
        res.json(result.rows[0]);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.delete('/api/processos/:id', async (req, res) => {
    try {
        await pool.query('DELETE FROM processos WHERE id = $1', [req.params.id]);
        res.json({ message: 'Processo deletado com sucesso' });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Estatísticas
app.get('/api/stats', async (req, res) => {
    try {
        const totalProcessos = await pool.query('SELECT COUNT(*) FROM processos');
        const valorTotal = await pool.query('SELECT SUM(valor_total) FROM processos');
        const porStatus = await pool.query('SELECT status, COUNT(*), SUM(valor_total) FROM processos GROUP BY status');
        const porTribunal = await pool.query('SELECT tribunal, COUNT(*) FROM processos GROUP BY tribunal');
        
        res.json({
            total_processos: parseInt(totalProcessos.rows[0].count),
            valor_total: parseFloat(valorTotal.rows[0].sum || 0),
            por_status: porStatus.rows,
            por_tribunal: porTribunal.rows
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Iniciar
app.listen(PORT, '0.0.0.0', async () => {
    console.log(`✅ Tax Master V3 rodando na porta ${PORT}`);
    await initDB();
    console.log('✅ Autenticação: JWT habilitado');
});
