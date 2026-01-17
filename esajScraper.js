// esajScraper.js - API CNJ DataJud (versão com filtros corretos)
const axios = require('axios');

const CNJ_API_URL = process.env.CNJ_API_URL || 'https://api-publica.datajud.cnj.jus.br';
const CNJ_API_KEY = process.env.CNJ_API_KEY || 'cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==';

function extrairAnoDoNumero(numeroProcesso) {
  // Formato CNJ: NNNNNNN-DD.AAAA.J.TR.OOOO
  // Posição 9-12 contém o ano
  if (!numeroProcesso || numeroProcesso.length < 13) return null;
  const ano = parseInt(numeroProcesso.substring(9, 13));
  return isNaN(ano) ? null : ano;
}

function calcularAnoLOA(numeroProcesso) {
  const anoAjuizamento = extrairAnoDoNumero(numeroProcesso);
  if (!anoAjuizamento) return new Date().getFullYear() + 1;
  return anoAjuizamento + 2; // LOA é geralmente ano + 2
}

function determinarNatureza(classe, assuntos) {
  const texto = (classe + ' ' + (assuntos || '')).toLowerCase();
  
  if (texto.includes('tribut') || texto.includes('fiscal') || texto.includes('iptu') || texto.includes('iss')) {
    return 'Tributária';
  }
  if (texto.includes('aliment')) {
    return 'Alimentar';
  }
  if (texto.includes('previd') || texto.includes('aposentad')) {
    return 'Previdenciária';
  }
  
  return 'Comum';
}

function processarHit(hit) {
  const p = hit._source;
  
  const numero = p.numeroProcesso || 'Não informado';
  const classe = p.classe?.nome || 'Não informado';
  const orgao = p.orgaoJulgador?.nome || 'Não informado';
  const assuntos = Array.isArray(p.assunto) ? p.assunto.map(a => a.nome).join(', ') : '';
  const dataAjuizamento = p.dataAjuizamento || p.dataHoraUltimaAtualizacao || 'Não informado';
  
  const anoLOA = calcularAnoLOA(numero);
  const natureza = determinarNatureza(classe, assuntos);
  
  // Tentar extrair valor (pode não existir)
  const valor = p.valorCausa || 0;
  
  return {
    numero: numero,
    tribunal: 'TJ-SP',
    credor: 'A definir',
    valor: valor,
    classe: classe,
    assunto: assuntos || orgao,
    dataDistribuicao: dataAjuizamento,
    comarca: 'São Paulo',
    vara: orgao,
    natureza: natureza,
    anoLOA: anoLOA,
    anoAjuizamento: extrairAnoDoNumero(numero),
    status: 'Em Análise',
    fonte: 'API CNJ DataJud'
  };
}

async function buscarProcessosESAJ(params) {
  const { valorMin, valorMax, natureza, anoLoa, quantidade = 50 } = params;

  console.log('\n🔍 BUSCA NA API CNJ DATAJUD (OFICIAL)');
  console.log(`   URL: ${CNJ_API_URL}`);
  console.log(`   Filtros solicitados:`);
  console.log(`     Valor: ${valorMin || 0} - ${valorMax || '∞'}`);
  console.log(`     Natureza: ${natureza || 'Todas'}`);
  console.log(`     ANO LOA: ${anoLoa || 'Todos'}`);
  console.log(`     Quantidade: ${quantidade}`);

  try {
    // Buscar quantidade maior para compensar filtros
    const query = {
      size: quantidade * 3,
      query: {
        match_all: {}
      },
      sort: [
        { 'dataHoraUltimaAtualizacao': { order: 'desc' } }
      ]
    };

    console.log(`   📤 Enviando requisição para CNJ...`);

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
    console.log(`   ✅ ${hits.length} processos retornados da API`);

    // Processar todos os hits
    const processados = hits.map(hit => processarHit(hit));
    
    console.log(`   🔍 Aplicando filtros locais...`);

    // Aplicar filtros
    const filtrados = processados.filter(p => {
      // Filtro de valor
      if (valorMin && p.valor > 0 && p.valor < valorMin) {
        return false;
      }
      if (valorMax && p.valor > 0 && p.valor > valorMax) {
        return false;
      }
      
      // Filtro de natureza
      if (natureza && natureza !== 'Todas' && p.natureza !== natureza) {
        return false;
      }
      
      // Filtro de ANO LOA
      if (anoLoa && anoLoa !== 'Todos') {
        const anoLoaNum = parseInt(anoLoa);
        if (!isNaN(anoLoaNum) && p.anoLOA !== anoLoaNum) {
          return false;
        }
      }
      
      return true;
    });

    // Limitar à quantidade solicitada
    const resultado = filtrados.slice(0, quantidade);

    console.log(`\n📊 RESULTADO FINAL:`);
    console.log(`   Retornados da API: ${hits.length}`);
    console.log(`   Processados: ${processados.length}`);
    console.log(`   Após filtros: ${filtrados.length}`);
    console.log(`   Retornando: ${resultado.length}`);
    
    if (resultado.length > 0) {
      console.log(`\n   📑 Distribuição por ANO LOA:`);
      const porAno = resultado.reduce((acc, p) => {
        acc[p.anoLOA] = (acc[p.anoLOA] || 0) + 1;
        return acc;
      }, {});
      Object.entries(porAno).forEach(([ano, qtd]) => {
        console.log(`      ${ano}: ${qtd} processos`);
      });
      
      console.log(`\n   📑 Distribuição por Natureza:`);
      const porNatureza = resultado.reduce((acc, p) => {
        acc[p.natureza] = (acc[p.natureza] || 0) + 1;
        return acc;
      }, {});
      Object.entries(porNatureza).forEach(([nat, qtd]) => {
        console.log(`      ${nat}: ${qtd} processos`);
      });
    }
    
    console.log(`   ✅ Fonte: API CNJ DataJud (OFICIAL)\n`);

    return {
      processos: resultado,
      stats: {
        totalAPI: hits.length,
        totalProcessados: processados.length,
        totalFiltrados: filtrados.length,
        totalRetornado: resultado.length,
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
