const { Pool } = require('pg');

const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

// Criar tabelas se não existirem
async function initDatabase() {
    const client = await pool.connect();
    try {
        await client.query(`
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                senha VARCHAR(255) NOT NULL,
                papel VARCHAR(50) DEFAULT 'usuario',
                ativo BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS receitas (
                id SERIAL PRIMARY KEY,
                data DATE NOT NULL,
                descricao TEXT NOT NULL,
                categoria VARCHAR(100),
                valor DECIMAL(15,2) NOT NULL,
                usuario_id INTEGER REFERENCES usuarios(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS despesas (
                id SERIAL PRIMARY KEY,
                data DATE NOT NULL,
                descricao TEXT NOT NULL,
                categoria VARCHAR(100),
                valor DECIMAL(15,2) NOT NULL,
                usuario_id INTEGER REFERENCES usuarios(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS precatorios (
                id SERIAL PRIMARY KEY,
                numero_processo VARCHAR(100) UNIQUE NOT NULL,
                tribunal VARCHAR(100) NOT NULL,
                ente_devedor VARCHAR(255) NOT NULL,
                natureza VARCHAR(50) NOT NULL,
                beneficiario VARCHAR(255) NOT NULL,
                cpf_cnpj VARCHAR(20) NOT NULL,
                valor_principal DECIMAL(15,2) NOT NULL,
                valor_corrigido DECIMAL(15,2) NOT NULL,
                data_base DATE NOT NULL,
                data_formacao DATE,
                status VARCHAR(50) DEFAULT 'em_formacao',
                observacoes TEXT,
                usuario_id INTEGER REFERENCES usuarios(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS oportunidades (
                id SERIAL PRIMARY KEY,
                numero_precatorio VARCHAR(100) NOT NULL,
                tribunal VARCHAR(100) NOT NULL,
                valor DECIMAL(15,2) NOT NULL,
                natureza VARCHAR(50),
                beneficiario VARCHAR(255),
                ano INTEGER,
                status VARCHAR(50) DEFAULT 'disponivel',
                deságio DECIMAL(5,2),
                rentabilidade DECIMAL(5,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        `);
        
        console.log('✅ Tabelas criadas/verificadas com sucesso');
    } catch (error) {
        console.error('❌ Erro ao criar tabelas:', error);
    } finally {
        client.release();
    }
}

module.exports = { pool, initDatabase };
