const sqlite3 = require('sqlite3').verbose();
const fs = require('fs');

console.log('🔧 RECRIANDO BANCO DE DADOS...\n');

// Backup e deletar banco antigo
if (fs.existsSync('./taxmaster.db')) {
    fs.copyFileSync('./taxmaster.db', './taxmaster-OLD.db.backup');
    fs.unlinkSync('./taxmaster.db');
    console.log('✅ Banco antigo removido (backup: taxmaster-OLD.db.backup)\n');
}

// Criar novo banco
const db = new sqlite3.Database('./taxmaster.db', (err) => {
    if (err) {
        console.error('❌ Erro ao criar banco:', err);
        process.exit(1);
    }
    console.log('✅ Novo banco criado\n');
});

// Criar tabela com estrutura correta
const createTable = `
    CREATE TABLE processos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero TEXT NOT NULL,
        tribunal TEXT NOT NULL,
        credor TEXT NOT NULL,
        valor REAL NOT NULL,
        status TEXT NOT NULL,
        dataDistribuicao TEXT
    )
`;

db.run(createTable, (err) => {
    if (err) {
        console.error('❌ Erro ao criar tabela:', err);
        process.exit(1);
    }
    console.log('✅ Tabela processos criada\n');
    popularBanco();
});

function popularBanco() {
    console.log('🔧 Populando banco com 100 processos...\n');
    
    const tribunais = ['TJ-SP', 'TJ-MG', 'TJ-BA', 'TJ-RJ', 'TJ-RS', 'TJ-PR', 'TJ-SC', 'TJ-ES', 'TJ-PE', 'TJ-CE'];
    const statusList = ['Pendente', 'Em Análise', 'Aprovado', 'Rejeitado', 'Finalizado'];
    const nomes = [
        'João Silva Santos', 'Maria Costa Lima', 'José Oliveira Souza', 'Ana Paula Ferreira',
        'Carlos Eduardo Alves', 'Paula Regina Santos', 'Pedro Henrique Lima', 'Lucia Fernanda Costa',
        'Roberto Carlos Silva', 'Mariana Aparecida Souza', 'Fernando José Oliveira', 'Juliana Maria Santos',
        'Ricardo Luiz Costa', 'Patricia Helena Lima', 'Marcelo Antonio Souza', 'Camila Cristina Alves',
        'Alexandre Rodrigues', 'Beatriz Martins', 'Daniel Carvalho', 'Eduarda Pereira'
    ];
    
    const stmt = db.prepare(`
        INSERT INTO processos (numero, tribunal, credor, valor, status, dataDistribuicao)
        VALUES (?, ?, ?, ?, ?, ?)
    `);
    
    for (let i = 0; i < 100; i++) {
        const ano = 2021 + (i % 4);
        const mes = String(Math.floor(Math.random() * 12) + 1).padStart(2, '0');
        const dia = String(Math.floor(Math.random() * 28) + 1).padStart(2, '0');
        
        const numero = `${1000000 + i}-${String(Math.floor(Math.random() * 99) + 1).padStart(2, '0')}.${ano}.8.${String(Math.floor(Math.random() * 27) + 1).padStart(2, '0')}.${String(Math.floor(Math.random() * 9999) + 1).padStart(4, '0')}`;
        const tribunal = tribunais[i % tribunais.length];
        const credor = nomes[i % nomes.length] + (i >= nomes.length ? ` - Caso ${Math.floor(i / nomes.length) + 1}` : '');
        const valor = Math.round((Math.random() * 450000 + 50000) * 100) / 100;
        const status = statusList[i % statusList.length];
        const dataDistribuicao = `${ano}-${mes}-${dia}`;
        
        stmt.run(numero, tribunal, credor, valor, status, dataDistribuicao);
    }
    
    stmt.finalize((err) => {
        if (err) {
            console.error('❌ Erro ao finalizar:', err);
            db.close();
            return;
        }
        
        console.log('✅ 100 processos adicionados!\n');
        
        // Verificar resultado
        db.get('SELECT COUNT(*) as total, SUM(valor) as valorTotal FROM processos', (err, row) => {
            if (err) {
                console.error('❌ Erro ao verificar:', err);
                db.close();
                return;
            }
            
            console.log('╔════════════════════════════════════════╗');
            console.log('║       📊 RESULTADO FINAL 📊           ║');
            console.log('╚════════════════════════════════════════╝\n');
            console.log(`   ✅ Total: ${row.total} processos`);
            console.log(`   💰 Valor: R$ ${row.valorTotal.toLocaleString('pt-BR', {minimumFractionDigits: 2})}\n`);
            
            // Mostrar amostra
            db.all('SELECT * FROM processos LIMIT 5', (err, rows) => {
                if (!err && rows) {
                    console.log('📄 AMOSTRA DE PROCESSOS:\n');
                    rows.forEach((p, i) => {
                        console.log(`   ${i + 1}. ${p.numero}`);
                        console.log(`      Tribunal: ${p.tribunal}`);
                        console.log(`      Credor: ${p.credor}`);
                        console.log(`      Valor: R$ ${p.valor.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`);
                        console.log(`      Status: ${p.status}\n`);
                    });
                }
                
                db.close(() => {
                    console.log('✅ Banco de dados criado com sucesso!\n');
                });
            });
        });
    });
}
