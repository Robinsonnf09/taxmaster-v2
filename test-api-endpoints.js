const API_KEY = 'cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==';
const BASE_URL = 'https://api-publica.datajud.cnj.jus.br/api_publica';

console.log('\n╔════════════════════════════════════════╗');
console.log('║  TESTANDO ENDPOINTS DATAJUD - CNJ     ║');
console.log('╚════════════════════════════════════════╝\n');

// Teste 1: Endpoint raiz (descobrir estrutura)
async function testarEndpointRaiz() {
    console.log('🧪 Teste 1: Endpoint Raiz...\n');
    
    const endpoints = ['', '/processos', '/v1', '/api'];
    
    for (const endpoint of endpoints) {
        try {
            const url = `${BASE_URL}${endpoint}`;
            console.log(`   Testando: ${url}`);
            
            const response = await fetch(url, {
                headers: {
                    'Authorization': `APIKey ${API_KEY}`,
                    'Content-Type': 'application/json'
                }
            });
            
            console.log(`   Status: ${response.status} ${response.statusText}`);
            
            if (response.ok) {
                const text = await response.text();
                console.log(`   Resposta: ${text.substring(0, 200)}...`);
            }
            
        } catch (error) {
            console.log(`   Erro: ${error.message}`);
        }
        console.log('');
    }
}

// Teste 2: Diferentes formatos de número de processo
async function testarFormatosProcesso() {
    console.log('\n🧪 Teste 2: Testando Formatos de Número...\n');
    
    const formatos = [
        '5000001-00.2024.8.05.0001',
        '50000010020248050001',
        '5000001002024805000',
        { numeroProcesso: '5000001-00.2024.8.05.0001' }
    ];
    
    for (const formato of formatos) {
        try {
            let url, options;
            
            if (typeof formato === 'string') {
                url = `${BASE_URL}/processos/${formato}`;
                options = {
                    method: 'GET',
                    headers: {
                        'Authorization': `APIKey ${API_KEY}`,
                        'Content-Type': 'application/json'
                    }
                };
            } else {
                url = `${BASE_URL}/processos`;
                options = {
                    method: 'POST',
                    headers: {
                        'Authorization': `APIKey ${API_KEY}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formato)
                };
            }
            
            console.log(`   Formato: ${JSON.stringify(formato)}`);
            console.log(`   URL: ${url}`);
            
            const response = await fetch(url, options);
            console.log(`   Status: ${response.status} ${response.statusText}`);
            
            if (response.ok || response.status === 404) {
                const text = await response.text();
                if (text) {
                    console.log(`   Resposta: ${text.substring(0, 150)}`);
                }
            }
            
        } catch (error) {
            console.log(`   Erro: ${error.message}`);
        }
        console.log('');
    }
}

// Teste 3: Testar com método POST
async function testarPOST() {
    console.log('\n🧪 Teste 3: Tentando POST...\n');
    
    try {
        const response = await fetch(`${BASE_URL}/processos/pesquisar`, {
            method: 'POST',
            headers: {
                'Authorization': `APIKey ${API_KEY}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                numeroProcesso: '5000001-00.2024.8.05.0001',
                tribunal: '8.05'
            })
        });
        
        console.log(`   Status: ${response.status} ${response.statusText}`);
        
        const text = await response.text();
        if (text) {
            console.log(`   Resposta: ${text}`);
        }
    } catch (error) {
        console.log(`   Erro: ${error.message}`);
    }
}

// Executar todos os testes
(async () => {
    await testarEndpointRaiz();
    await testarFormatosProcesso();
    await testarPOST();
    
    console.log('\n╔════════════════════════════════════════╗');
    console.log('║      ✅ TESTES CONCLUÍDOS!            ║');
    console.log('╚════════════════════════════════════════╝');
    console.log('\n💡 Analise os resultados acima para identificar');
    console.log('   o formato correto aceito pela API.\n');
})();
