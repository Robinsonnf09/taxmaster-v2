require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const { Pool } = require('pg');

const app = express();
const PORT = process.env.PORT || 8080;

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
                valor DECIMAL(15,2),
                status VARCHAR(50),
                created_at TIMESTAMP DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                senha VARCHAR(255) NOT NULL,
                nome VARCHAR(255),
                created_at TIMESTAMP DEFAULT NOW()
            );
        `);
        console.log('✅ Banco de dados: PostgreSQL Railway');
        console.log('✅ Tabelas criadas/verificadas');
    } catch (err) {
        console.error('❌ Erro no banco:', err.message);
    }
}

// Middlewares
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Rotas
app.get('/', (req, res) => res.sendFile(path.join(__dirname, 'public', 'index.html')));
app.get('/dashboard-financeiro.html', (req, res) => res.sendFile(path.join(__dirname, 'public', 'dashboard-financeiro.html')));
app.get('/login.html', (req, res) => res.sendFile(path.join(__dirname, 'public', 'login.html')));
app.get('/precatorios.html', (req, res) => res.sendFile(path.join(__dirname, 'public', 'precatorios.html')));

app.get('/health', (req, res) => res.json({ status: 'OK', database: 'PostgreSQL' }));

app.get('/api/processos', async (req, res) => {
    try {
        const result = await pool.query('SELECT * FROM processos ORDER BY created_at DESC');
        res.json(result.rows);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.post('/api/processos', async (req, res) => {
    const { numero, tribunal, valor, status } = req.body;
    try {
        const result = await pool.query(
            'INSERT INTO processos (numero, tribunal, valor, status) VALUES ($1, $2, $3, $4) RETURNING *',
            [numero, tribunal, valor, status]
        );
        res.json(result.rows[0]);
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
