// esajScraper.js - API CNJ DataJud (versão adaptada aos dados reais)
const axios = require('axios');

const CNJ_API_URL = process.env.CNJ_API_URL || 'https://api-publica.datajud.cnj.jus.br';
const CNJ_API_KEY = process.env.CNJ_API_KEY || 'cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==';

function processarHit(hit) {
  const p = hit._source;
  
  // Extrair dados que EXISTEM
  const numero = p.numeroProcesso || 'Não informado';
  const classe = p.classe?.nome || 'Não informado';
  const orgao = p.orgaoJulgador?.nome || 'Não informado';
  const dataAjuizamento = p.dataAjuizamento || p.dataHoraUltimaAtualizacao || 'Não informado';
  
  // Calcular ano LOA baseado no número do processo
  let anoLOA = new Date().getFullYear() + 1;
  if (numero && numero.length >= 20) {
    const anoAjuizamento = parseInt(numero.substring(9, 13));
    if (!isNaN(anoAjuizamento)) {
      anoLOA = anoAjuizamento + 2;
    }
  }
  
  // Determinar natureza baseada na classe
  let natureza = 'Comum';
  const classeLower = classe.toLowerCase();
  if (classeLower.includes('tribut') || classeLower.includes('fiscal')) {
    natureza = 'Tributária';
  } else if (classeLower.includes('aliment')) {
    natureza = 'Alimentar';
  } else if (classeLower.includes('previd')) {
    natureza = 'Previdenciária';
  }
  
  return {
    numero: numero,
    tribunal: 'TJ-SP',
    credor: 'A definir', // Não disponível na API
    valor: 0, // Não disponível na API
    classe: classe,
    assunto: orgao, // Usando órgão julgador como informação adicional
    dataDistribuicao: dataAjuizamento,
    comarca: 'São Paulo',
    vara: orgao,
    natureza: natureza,
    anoLOA: anoLOA,
    status: 'Em Análise',
    fonte: 'API CNJ DataJud'
  };
}

async function buscarProcessosESAJ(params) {
  const { natureza, quantidade = 50 } = params;

  console.log('\n🔍 BUSCA NA API CNJ DATAJUD (OFICIAL)');
  console.log(`   URL: ${CNJ_API_URL}`);
  console.log(`   Quantidade: ${quantidade}`);

  try {
    const query = {
      size: quantidade,
      query: {
        match_all: {}
      },
      sort: [
        { 'dataHoraUltimaAtualizacao': { order: 'desc' } }
      ]
    };

    console.log(`   📤 Enviando requisição...`);

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

    console.log(`   📥 Status: ${response.status}`);

    if (!response.data?.hits?.hits) {
      console.log('   ⚠️ Resposta vazia\n');
      return { processos: [], stats: { erro: 'Resposta vazia' } };
    }

    const hits = response.data.hits.hits;
    console.log(`   ✅ ${hits.length} processos encontrados`);

    // Processar sem filtros de valor (não disponível)
    const processos = hits
      .map(hit => processarHit(hit))
      .filter(p => {
        // Filtrar apenas por natureza se especificado
        if (natureza && natureza !== 'Todas') {
          return p.natureza === natureza;
        }
        return true;
      });

    console.log(`\n📊 RESULTADO FINAL:`);
    console.log(`   Total: ${processos.length} processos`);
    console.log(`   ✅ Fonte: API CNJ DataJud (OFICIAL)\n`);

    return {
      processos: processos,
      stats: {
        total: processos.length,
        modo: 'API OFICIAL CNJ'
      }
    };

  } catch (error) {
    console.error(`   ❌ ERRO: ${error.message}\n`);
    return {
      processos: [],
      stats: { erro: error.message }
    };
  }
}

module.exports = { buscarProcessosESAJ };
