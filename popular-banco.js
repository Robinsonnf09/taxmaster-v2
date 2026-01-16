const sqlite3 = require('sqlite3').verbose();
const fs = require('fs');

console.log('🔧 Iniciando correção do banco de dados...\n');

// Backup do banco atual
if (fs.existsSync('./taxmaster.db')) {
    fs.copyFileSync('./taxmaster.db', './taxmaster.db.backup');
    console.log('✅ Backup criado: taxmaster.db.backup\n');
}

const db = new sqlite3.Database('./taxmaster.db', (err) => {
    if (err) {
        console.error('❌ Erro ao conectar:', err);
        process.exit(1);
    }
    console.log('✅ Conectado ao taxmaster.db\n');
});

// Verificar estrutura da tabela
db.get("SELECT sql FROM sqlite_master WHERE type='table' AND name='processos'", (err, row) => {
    if (err || !row) {
        console.log('⚠️ Tabela processos não existe. Criando...\n');
        
        // Criar tabela
        db.run(`
            CREATE TABLE IF NOT EXISTS processos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT,
                tribunal TEXT,
                credor TEXT,
                valor REAL,
                status TEXT,
                dataDistribuicao TEXT
            )
        `, (err) => {
            if (err) {
                console.error('❌ Erro ao criar tabela:', err);
                process.exit(1);
            }
            popularDados();
        });
    } else {
        console.log('✅ Tabela processos existe\n');
        popularDados();
    }
});

function popularDados() {
    // Limpar registros vazios
    db.run('DELETE FROM processos WHERE numero IS NULL OR numero = ""', (err) => {
        if (err) console.error('⚠️ Erro ao limpar:', err);
        else console.log('✅ Registros vazios removidos\n');
        
        // Contar processos
        db.get('SELECT COUNT(*) as total FROM processos', (err, row) => {
            if (err) {
                console.error('❌ Erro ao contar:', err);
                return;
            }
            
            const total = row.total;
            console.log(`📊 Processos existentes: ${total}\n`);
            
            const faltam = 100 - total;
            if (faltam <= 0) {
                console.log('✅ Banco já tem 100+ processos!\n');
                verificarDados();
                return;
            }
            
            console.log(`🔧 Adicionando ${faltam} processos...\n`);
            
            // Dados para gerar processos
            const tribunais = ['TJ-SP', 'TJ-MG', 'TJ-BA', 'TJ-RJ', 'TJ-RS', 'TJ-PR', 'TJ-SC', 'TJ-ES', 'TJ-PE', 'TJ-CE'];
            const statusList = ['Pendente', 'Em Análise', 'Aprovado', 'Rejeitado', 'Finalizado'];
            const nomes = [
                'João Silva Santos', 'Maria Costa Lima', 'José Oliveira', 'Ana Paula Souza',
                'Carlos Eduardo Ferreira', 'Paula Regina Alves', 'Pedro Henrique Santos', 'Lucia Fernanda Costa',
                'Roberto Carlos Lima', 'Mariana Aparecida Silva', 'Fernando José Oliveira', 'Juliana Maria Santos',
                'Ricardo Luiz Costa', 'Patricia Helena Lima', 'Marcelo Antonio Souza', 'Camila Cristina Alves'
            ];
            
            const stmt = db.prepare(`
                INSERT INTO processos (numero, tribunal, credor, valor, status, dataDistribuicao) 
                VALUES (?, ?, ?, ?, ?, ?)
            `);
            
            for (let i = 0; i < faltam; i++) {
                const ano = 2021 + (i % 4);
                const mes = String(Math.floor(Math.random() * 12) + 1).padStart(2, '0');
                const dia = String(Math.floor(Math.random() * 28) + 1).padStart(2, '0');
                
                const numero = `${1000000 + total + i}-${String(Math.floor(Math.random() * 99) + 1).padStart(2, '0')}.${ano}.8.${String(Math.floor(Math.random() * 27) + 1).padStart(2, '0')}.${String(Math.floor(Math.random() * 9999) + 1).padStart(4, '0')}`;
                const tribunal = tribunais[i % tribunais.length];
                const credor = nomes[i % nomes.length] + (i >= nomes.length ? ` - ${Math.floor(i / nomes.length) + 1}` : '');
                const valor = Math.round((Math.random() * 450000 + 50000) * 100) / 100;
                const status = statusList[i % statusList.length];
                const dataDistribuicao = `${ano}-${mes}-${dia}`;
                
                stmt.run(numero, tribunal, credor, valor, status, dataDistribuicao);
            }
            
            stmt.finalize((err) => {
                if (err) {
                    console.error('❌ Erro ao finalizar:', err);
                    db.close();
                } else {
                    console.log('✅ Processos adicionados!\n');
                    verificarDados();
                }
            });
        });
    });
}

function verificarDados() {
    // Verificar resultado final
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
        console.log(`   💰 Valor: R$ ${(row.valorTotal || 0).toLocaleString('pt-BR', {minimumFractionDigits: 2})}\n`);
        
        // Mostrar amostra
        db.all('SELECT * FROM processos LIMIT 3', (err, rows) => {
            if (!err && rows) {
                console.log('📄 AMOSTRA DE PROCESSOS:\n');
                rows.forEach((p, i) => {
                    console.log(`   ${i + 1}. ${p.numero}`);
                    console.log(`      Tribunal: ${p.tribunal}`);
                    console.log(`      Credor: ${p.credor}`);
                    console.log(`      Valor: R$ ${(p.valor || 0).toLocaleString('pt-BR', {minimumFractionDigits: 2})}`);
                    console.log(`      Status: ${p.status}\n`);
                });
            }
            
            db.close(() => {
                console.log('✅ Banco de dados atualizado com sucesso!\n');
            });
        });
    });
}
