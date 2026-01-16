const sqlite3 = require('sqlite3').verbose();

const db = new sqlite3.Database('./taxmaster.db', (err) => {
    if (err) {
        console.error('❌ Erro:', err);
        process.exit(1);
    }
});

// Mostrar estrutura da tabela
db.get("SELECT sql FROM sqlite_master WHERE type='table' AND name='processos'", (err, row) => {
    if (err || !row) {
        console.log('⚠️ Tabela processos não existe!');
    } else {
        console.log('📊 ESTRUTURA ATUAL:\n');
        console.log(row.sql);
        console.log('\n');
    }
    
    // Mostrar colunas
    db.all("PRAGMA table_info(processos)", (err, rows) => {
        if (!err && rows) {
            console.log('📋 COLUNAS EXISTENTES:\n');
            rows.forEach(col => {
                console.log(`   • ${col.name} (${col.type})`);
            });
            console.log('\n');
        }
        db.close();
    });
});
