const sqlite3 = require('sqlite3').verbose();
const https = require('https');

console.log('🔥 BUSCA AUTOMATIZADA TJ-SP VIA API DATAJUD/CNJ\n');

const API_CONFIG = {
    hostname: 'api-publica.datajud.cnj.jus.br',
    path: '/api_publica_tjsp/_search',
    apiKey: 'APIKey cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=='
};

function consultarAPI(query) {
    return new Promise((resolve, reject) => {
        const postData = JSON.stringify(query);
        
        const options = {
            hostname: API_CONFIG.hostname,
            port: 443,
            path: API_CONFIG.path,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(postData),
                'Authorization': API_CONFIG.apiKey
            }
        };
        
        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', (chunk) => { data += chunk; });
            res.on('end', () => {
                try {
                    resolve(JSON.parse(data));
                } catch (e) {
                    reject(new Error('Erro ao processar resposta: ' + e.message));
                }
            });
        });
        
        req.on('error', (error) => reject(error));
        req.write(postData);
        req.end();
    });
}

async function buscarPrecatorios(valorMin = 50000, valorMax = 1000000, limite = 100) {
    console.log(`💰 Buscando precatórios entre R$ ${valorMin.toLocaleString('pt-BR')} e R$ ${valorMax.toLocaleString('pt-BR')}\n`);
    
    const query = {
        "query": {
            "bool": {
                "must": [
                    { "match": { "tribunal": "TJSP" } },
                    {
                        "bool": {
                            "should": [
                                { "match": { "assunto.nome": "precatório" } },
                                { "match": { "assunto.nome": "requisição" } },
                                { "match": { "classe.nome": "requisição" } }
                            ]
                        }
                    },
                    {
                        "range": {
                            "valorCausa": {
                                "gte": valorMin,
                                "lte": valorMax
                            }
                        }
                    }
                ]
            }
        },
        "size": limite,
        "_source": ["numeroProcesso", "tribunal", "valorCausa", "assunto", "classe", "orgaoJulgador", "dataAjuizamento"],
        "sort": [{ "valorCausa": { "order": "desc" } }]
    };
    
    try {
        const response = await consultarAPI(query);
        const processos = response.hits?.hits || [];
        console.log(`✅ ${processos.length} precatórios encontrados\n`);
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
                const credor = p.orgaoJulgador?.nome || p.classe?.nome || p.assunto?.nome || 'Credor TJ-SP';
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
                    console.log(`\n✅ ${importados} precatórios importados!`);
                    console.log(`💰 Valor total: R$ ${valorTotal.toLocaleString('pt-BR', {minimumFractionDigits: 2})}\n`);
                    db.close();
                    resolve({ importados, valorTotal });
                }
            });
        });
    });
}

if (require.main === module) {
    const valorMin = parseInt(process.argv[2]) || 50000;
    const valorMax = parseInt(process.argv[3]) || 1000000;
    const limite = parseInt(process.argv[4]) || 100;
    
    buscarPrecatorios(valorMin, valorMax, limite)
        .then(processos => importarParaBanco(processos))
        .then(() => process.exit(0))
        .catch(err => {
            console.error('Falha na busca:', err.message);
            process.exit(1);
        });
}

module.exports = { buscarPrecatorios, importarParaBanco };
