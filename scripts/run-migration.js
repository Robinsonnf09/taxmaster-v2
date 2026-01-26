require('dotenv').config();
const { Pool } = require('pg');
const fs = require('fs');
const path = require('path');

const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: { rejectUnauthorized: false }
});

async function runMigration() {
    try {
        console.log('\n═══════════════════════════════════════════════════════════════');
        console.log('  🚀 INICIANDO MIGRAÇÃO DO BANCO DE DADOS');
        console.log('═══════════════════════════════════════════════════════════════\n');
        
        // Testar conexão
        console.log('🔌 Conectando ao PostgreSQL Railway...');
        await pool.query('SELECT NOW()');
        console.log('✅ Conexão estabelecida!\n');
        
        // Ler arquivo SQL
        console.log('📖 Lendo arquivo de migração...');
        const sqlPath = path.join(__dirname, '..', 'migrations', '001_create_processos_complete.sql');
        const sql = fs.readFileSync(sqlPath, 'utf8');
        console.log('✅ Arquivo carregado!\n');
        
        // Executar migração
        console.log('⚙️  Executando migração...');
        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
        
        await pool.query(sql);
        
        console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        console.log('✅ Migração executada com sucesso!\n');
        
        // Verificar estrutura criada
        console.log('📊 VERIFICANDO ESTRUTURA CRIADA:\n');
        
        // Colunas da tabela processos
        const columns = await pool.query(`
            SELECT column_name, data_type, character_maximum_length, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'processos' 
            ORDER BY ordinal_position;
        `);
        
        console.log(`📋 TABELA PROCESSOS (${columns.rows.length} colunas):`);
        columns.rows.forEach((col, idx) => {
            const type = col.character_maximum_length 
                ? `${col.data_type}(${col.character_maximum_length})`
                : col.data_type;
            console.log(`  ${idx + 1}. ${col.column_name.padEnd(20)} | ${type.padEnd(20)} | Nullable: ${col.is_nullable}`);
        });
        
        // Índices
        console.log('\n📑 ÍNDICES CRIADOS:');
        const indexes = await pool.query(`
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'processos';
        `);
        indexes.rows.forEach((idx, i) => {
            console.log(`  ${i + 1}. ${idx.indexname}`);
        });
        
        // Triggers
        console.log('\n⚡ TRIGGERS CRIADOS:');
        const triggers = await pool.query(`
            SELECT trigger_name, event_manipulation, action_statement
            FROM information_schema.triggers
            WHERE event_object_table = 'processos';
        `);
        triggers.rows.forEach((trg, i) => {
            console.log(`  ${i + 1}. ${trg.trigger_name} (${trg.event_manipulation})`);
        });
        
        // Views
        console.log('\n👁️  VIEWS CRIADAS:');
        const views = await pool.query(`
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = 'public' AND table_name LIKE 'vw_processos%';
        `);
        views.rows.forEach((vw, i) => {
            console.log(`  ${i + 1}. ${vw.table_name}`);
        });
        
        console.log('\n═══════════════════════════════════════════════════════════════');
        console.log('  ✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!');
        console.log('═══════════════════════════════════════════════════════════════\n');
        
        await pool.end();
    } catch (err) {
        console.error('\n❌ ERRO NA MIGRAÇÃO:', err.message);
        console.error(err.stack);
        process.exit(1);
    }
}

runMigration();
