const sqlite3 = require('sqlite3').verbose();
const https = require('https');

console.log('🔍 BUSCA AMPLIADA TJ-SP - SEM RESTRIÇÕES DE VALOR\n');

function consultarAPI(query) {
    return new Promise((resolve, reject) => {
        const postData = JSON.stringify(query);
        
        const options = {
            hostname: 'api-publica.datajud.cnj.jus.br',
            port: 443,
            path: '/api_publica_tjsp/_search',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(postData),
                'Authorization': 'APIKey cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=='
            }
        };
        
        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', (chunk) => { data += chunk; });
            res.on('end', () => {
                try {
                    const parsed = JSON.parse(data);
                    resolve(parsed);
                } catch (e) {
                    reject(new Error('Erro ao processar: ' + e.message));
                }
            });
        });
        
        req.on('error', (error) => reject(error));
        req.write(postData);
        req.end();
    });
}

async function buscarProcessosGerais(limite = 100) {
    console.log('📡 Buscando processos gerais do TJ-SP (sem filtro de valor)...\n');
    
    // Query mais simples - apenas tribunal
    const query = {
        "query": {
            "match": {
                "tribunal": "TJSP"
            }
        },
        "size": limite,
        "_source": ["numeroProcesso", "tribunal", "valorCausa", "assunto", "classe", "orgaoJulgador", "dataAjuizamento", "movimentos"],
        "sort": [{ "dataAjuizamento": { "order": "desc" } }]
    };
    
    try {
        const response = await consultarAPI(query);
        
        console.log('📊 RESPOSTA DA API:');
        console.log(`   Total disponível: ${response.hits?.total?.value || 0}`);
        console.log(`   Retornados: ${response.hits?.hits?.length || 0}\n`);
        
        const processos = response.hits?.hits || [];
        
        if (processos.length > 0) {
            console.log('📄 AMOSTRA DE PROCESSOS:\n');
            processos.slice(0, 5).forEach((hit, i) => {
                const p = hit._source;
                console.log(`   ${i + 1}. ${p.numeroProcesso || 'N/A'}`);
                console.log(`      Valor: R$ ${(p.valorCausa || 0).toLocaleString('pt-BR', {minimumFractionDigits: 2})}`);
                console.log(`      Classe: ${p.classe?.nome || 'N/A'}`);
                console.log(`      Assunto: ${p.assunto?.nome || 'N/A'}\n`);
            });
        }
        
        return processos;
    } catch (error) {
        console.error(`❌ Erro: ${error.message}`);
        throw error;
    }
}

async function importarParaBanco(processos) {
    const db = new sqlite3.Database('./taxmaster.db');
    
    return new Promise((resolve, reject) => {
        db.run('DELETE FROM processos WHERE tribunal = "TJ-SP"', (err) => {
            const stmt = db.prepare('INSERT INTO processos (numero, tribunal, credor, valor, status, dataDistribuicao) VALUES (?, ?, ?, ?, ?, ?)');
            
            let importados = 0;
            let valorTotal = 0;
            
            processos.forEach((hit, i) => {
                const p = hit._source;
                const numero = p.numeroProcesso || `TJSP-${i + 1}`;
                const tribunal = 'TJ-SP';
                const credor = p.orgaoJulgador?.nome || p.classe?.nome || p.assunto?.nome || 'TJ-SP';
                const valor = p.valorCausa || 0;
                const status = 'Em Análise';
                const data = p.dataAjuizamento?.substring(0, 10) || null;
                
                stmt.run(numero, tribunal, credor, valor, status, data);
                importados++;
                valorTotal += valor;
            });
            
            stmt.finalize((err) => {
                if (err) reject(err);
                else {
                    console.log(`\n✅ ${importados} processos importados!`);
                    console.log(`💰 Valor total: R$ ${valorTotal.toLocaleString('pt-BR', {minimumFractionDigits: 2})}\n`);
                    db.close();
                    resolve({ importados, valorTotal });
                }
            });
        });
    });
}

const limite = parseInt(process.argv[2]) || 50;

buscarProcessosGerais(limite)
    .then(processos => {
        if (processos.length === 0) {
            console.log('⚠️ API não retornou processos. Verifique:\n');
            console.log('   1. Conectividade com internet');
            console.log('   2. API Key válida');
            console.log('   3. Disponibilidade da API DataJud\n');
            process.exit(1);
        }
        return importarParaBanco(processos);
    })
    .then(() => process.exit(0))
    .catch(err => {
        console.error('Falha:', err.message);
        process.exit(1);
    });
