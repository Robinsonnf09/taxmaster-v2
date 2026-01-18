// esajScraper.js - Tax Master V3 - Versão Segura
const axios = require('axios');

const CNJ_API_URL = process.env.CNJ_API_URL || 'https://api-publica.datajud.cnj.jus.br';
const CNJ_API_KEY = process.env.CNJ_API_KEY;

if (!CNJ_API_KEY) {
    console.error('❌ CNJ_API_KEY não configurada! Configure no .env');
    process.exit(1);
}

async function buscarProcessosESAJ(params) {
    const { valorMin, valorMax, natureza, anoLoa, status, quantidade = 30 } = params;

    console.log('\n╔═══════════════════════════════════════════════════════╗');
    console.log('║  🔍 BUSCA API CNJ DataJud                            ║');
    console.log('╚═══════════════════════════════════════════════════════╝\n');

    try {
        const query = {
            size: quantidade * 2,
            query: { match_all: {} }
        };

        const response = await axios.post(
            `${CNJ_API_URL}/api_publica_tjsp/_search`,
            query,
            {
                headers: {
                    'Authorization': `APIKey ${CNJ_API_KEY}`,
                    'Content-Type': 'application/json'
                },
                timeout: 30000
            }
        );

        const hits = response.data?.hits?.hits || [];
        console.log(`   📊 Processos retornados: ${hits.length}`);

        const processados = hits.map(hit => processarDados(hit._source));

        return {
            processos: processados.slice(0, quantidade),
            stats: {
                total: hits.length,
                retornados: processados.length
            }
        };

    } catch (error) {
        console.error(`   ❌ Erro: ${error.message}`);
        return { processos: [], stats: { erro: error.message } };
    }
}

function processarDados(p) {
    return {
        numero: p.numeroProcesso || '',
        tribunal: 'TJ-SP',
        credor: p.partes?.[0]?.nome || 'Não informado',
        valor: p.valorCausa || 0,
        classe: p.classe?.nome || 'Não informado',
        natureza: 'Comum',
        anoLOA: new Date().getFullYear() + 1,
        status: 'Pendente',
        fonte: '✅ API CNJ DataJud'
    };
}

module.exports = { buscarProcessosESAJ };
