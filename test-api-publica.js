const API_KEY = 'cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==';
const API_BASE_URL = 'https://api-publica.datajud.cnj.jus.br/api_publica';

console.log('\n╔════════════════════════════════════════╗');
console.log('║  TESTANDO API PÚBLICA DATAJUD - CNJ   ║');
console.log('╚════════════════════════════════════════╝\n');

// Teste 1: Listar Tribunais
async function testarTribunais() {
    console.log('🧪 Teste 1: Listar Tribunais...\n');
    
    try {
        const response = await fetch(`${API_BASE_URL}/tribunais`, {
            headers: {
                'Authorization': `APIKey ${API_KEY}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ SUCESSO! Tribunais encontrados:');
            console.log(`   Total: ${data.length || 0} tribunais`);
            if (data.length > 0) {
                console.log(`   Exemplo: ${data[0].nome || data[0]}`);
            }
        } else {
            console.log('❌ Erro:', response.status, response.statusText);
        }
    } catch (error) {
        console.log('❌ Erro na requisição:', error.message);
    }
    
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
}

// Teste 2: Buscar Processo Específico
async function testarProcesso() {
    console.log('🧪 Teste 2: Buscar Processo...\n');
    
    // Número de processo de exemplo
    const numeroProcesso = '5000001-00.2024.8.05.0001';
    
    try {
        const response = await fetch(`${API_BASE_URL}/processos/${numeroProcesso}`, {
            headers: {
                'Authorization': `APIKey ${API_KEY}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ SUCESSO! Processo encontrado:');
            console.log('   Dados:', data);
        } else {
            console.log('⚠️  Processo não encontrado (pode não existir na base)');
            console.log('   Status:', response.status);
        }
    } catch (error) {
        console.log('❌ Erro na requisição:', error.message);
    }
    
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
}

// Executar testes
(async () => {
    await testarTribunais();
    await testarProcesso();
    
    console.log('╔════════════════════════════════════════╗');
    console.log('║      ✅ TESTES CONCLUÍDOS!            ║');
    console.log('╚════════════════════════════════════════╝\n');
})();
