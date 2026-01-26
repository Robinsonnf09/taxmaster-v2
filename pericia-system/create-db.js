const { Client } = require('pg');

async function createDatabase() {
    const client = new Client({
        host: 'localhost',
        port: 5432,
        user: 'postgres',
        password: 'Rnf1e3a3j4r5$',
        database: 'postgres'
    });
    
    try {
        await client.connect();
        console.log('✓ Conectado ao PostgreSQL');
        
        const res = await client.query(
            "SELECT 1 FROM pg_database WHERE datname = 'pericia_db'"
        );
        
        if (res.rows.length === 0) {
            await client.query('CREATE DATABASE pericia_db');
            console.log('✓ Banco de dados "pericia_db" criado!');
        } else {
            console.log('✓ Banco de dados "pericia_db" já existe!');
        }
        
        await client.end();
        process.exit(0);
    } catch (error) {
        console.error('❌ Erro:', error.message);
        process.exit(1);
    }
}

createDatabase();
