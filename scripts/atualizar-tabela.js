require('dotenv').config();
const { Pool } = require('pg');

const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: { rejectUnauthorized: false }
});

async function atualizarTabela() {
    try {
        console.log('🔧 Conectando ao PostgreSQL...');
        await pool.query('SELECT NOW()');
        console.log('✅ Conexão estabelecida!');
        
        console.log('🔧 Adicionando coluna "tipo"...');
        await pool.query(`ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS tipo VARCHAR(50) DEFAULT 'usuario';`);
        console.log('✅ Coluna "tipo" adicionada!');
        
        await pool.end();
    } catch (err) {
        console.error('❌ Erro:', err.message);
        process.exit(1);
    }
}

atualizarTabela();
