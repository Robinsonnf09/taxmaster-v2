// esajScraper.js - API CNJ DataJud MELHORADO
const axios = require('axios');

const CNJ_API_URL = process.env.CNJ_API_URL || 'https://api-publica.datajud.cnj.jus.br';
const CNJ_API_KEY = process.env.CNJ_API_KEY;

async function buscarProcessosESAJ(params) {
  const { valorMin, valorMax, natureza, anoLoa, quantidade = 50 } = params; // ✅ Reduzido para 50

  console.log('\n🔍 BUSCA NA API CNJ DATAJUD (OFICIAL)');
  console.log(`   URL: ${CNJ_API_URL}`);
  console.log(`   Quantidade: ${quantidade}`);
  console.log(`   Filtros: Valor ${valorMin || 0}-${valorMax || '∞'}, Natureza: ${natureza || 'Todas'}, ANO LOA: ${anoLoa || 'Todos'}`);

  if (!CNJ_API_KEY) {
    console.log('   ❌ CNJ_API_KEY não configurada no Railway\n');
    return { 
      processos: [], 
      stats: { erro: 'API Key não configurada' } 
    };
  }

  try {
    // Query ElasticSearch
    const query = {
      size: quantidade,
      query: {
        bool: {
          must: [],
          filter: []
        }
      },
      sort: [
        { 'dataAjuizamento': { order: 'desc' } }
      ]
    };

    // ✅ MELHORADO: Filtro de tribunal - testar múltiplos campos
    // Alguns índices usam 'tribunal', outros 'siglaTribunal', outros 'codigoTribunal'
    query.query.bool.should = [
      { term: { 'tribunal': 'TJSP' } },
      { term: { 'siglaTribunal': 'TJSP' } },
      { match: { 'tribunal': 'TJ-SP' } }
    ];
    query.query.bool.minimum_should_match = 1;

    // Filtro de valor
    if (valorMin || valorMax) {
      query.query.bool.filter.push({
        range: {
          'valorCausa': {
            gte: valorMin || 0,
            lte: valorMax || 999999999
          }
        }
      });
    }

    // Filtro de natureza
    if (natureza && natureza !== 'Todas') {
      query.query.bool.must.push({
        match: {
          'assunto': {
            query: natureza,
            operator: 'and'
          }
        }
      });
    }

    // ✅ MELHORADO: Filtro de ano LOA - validação mais robusta
    if (anoLoa && anoLoa !== 'Todos' && !isNaN(parseInt(anoLoa))) {
      const anoLoaInt = parseInt(anoLoa);
      const anoProcesso = anoLoaInt - 2; // LOA = ano processo + 2
      
      console.log(`   📅 Filtro ANO LOA: ${anoLoaInt} → Processos de ${anoProcesso}`);
      
      query.query.bool.filter.push({
        range: {
          'dataAjuizamento': {
            gte: `${anoProcesso}-01-01`,
            lte: `${anoProcesso}-12-31`,
            format: 'yyyy-MM-dd'
          }
        }
      });
    }

    console.log(`   📤 Enviando requisição...`);

    const response = await axios.post(
      `${CNJ_API_URL}/api_publica_tjsp/_search`,
      query,
      {
        headers: {
          'Authorization': `APIKey ${CNJ_API_KEY}`,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        timeout: 30000
      }
    );

    console.log(`   📥 Status: ${response.status}`);

    if (!response.data || !response.data.hits) {
      console.log('   ⚠️ Resposta vazia\n');
      return { processos: [], stats: { erro: 'Resposta vazia' } };
    }

    const hits = response.data.hits.hits;
    console.log(`   ✅ ${hits.length} processos encontrados`);

    // ✅ MELHORADO: Log do primeiro processo para debug
    if (hits.length > 0) {
      console.log(`   🔍 Primeiro processo (debug):`);
      console.log(`      Número: ${hits[0]._source.numeroProcesso}`);
      console.log(`      Tribunal: ${hits[0]._source.tribunal || hits[0]._source.siglaTribunal}`);
      console.log(`      Valor: ${hits[0]._source.valorCausa || 0}`);
    }

    const processos = hits.map(hit => {
      const p = hit._source;
      
      // Determinar natureza
      let naturezaFinal = 'Comum';
      const assuntoLower = (p.assunto || '').toLowerCase();
      
      if (assuntoLower.includes('tribut') || assuntoLower.includes('fiscal') || 
          assuntoLower.includes('iptu') || assuntoLower.includes('iss')) {
        naturezaFinal = 'Tributária';
      } else if (assuntoLower.includes('aliment')) {
        naturezaFinal = 'Alimentar';
      } else if (assuntoLower.includes('previd')) {
        naturezaFinal = 'Previdenciária';
      }

      // Extrair credor
      let credor = 'Não informado';
      if (p.polo && p.polo.ativo && p.polo.ativo.length > 0) {
        credor = p.polo.ativo[0].nome || 'Não informado';
      } else if (p.partes && p.partes.length > 0) {
        const autor = p.partes.find(parte => 
          parte.polo === 'ATIVO' || 
          parte.tipo === 'AUTOR' || 
          parte.tipo === 'EXEQUENTE'
        );
        if (autor) credor = autor.nome || 'Não informado';
      }

      // Calcular ano LOA
      let anoLOA = new Date().getFullYear() + 1;
      if (p.dataAjuizamento) {
        const match = p.dataAjuizamento.match(/(\d{4})/);
        if (match) anoLOA = parseInt(match[1]) + 2;
      }

      return {
        numero: p.numeroProcesso || 'Não informado',
        tribunal: 'TJ-SP',
        credor: credor,
        valor: p.valorCausa || 0,
        classe: p.classe || 'Não informado',
        assunto: p.assunto || 'Não informado',
        dataDistribuicao: p.dataAjuizamento || 'Não informado',
        comarca: p.orgaoJulgador?.comarca || p.comarca || 'São Paulo',
        vara: p.orgaoJulgador?.nome || 'Não informado',
        natureza: naturezaFinal,
        anoLOA: anoLOA,
        status: 'Em Análise',
        fonte: 'API CNJ DataJud (Dados REAIS)'
      };
    });

    console.log(`\n📊 RESULTADO:`);
    console.log(`   Total: ${processos.length} processos REAIS`);
    console.log(`   ✅ Fonte: API CNJ DataJud (OFICIAL)\n`);

    return {
      processos: processos,
      stats: {
        totalAPI: processos.length,
        final: processos.length,
        modo: 'API OFICIAL CNJ'
      }
    };

  } catch (error) {
    console.error(`   ❌ ERRO: ${error.message}`);
    
    if (error.response) {
      console.log(`   Status: ${error.response.status}`);
      
      // ✅ MELHORADO: Tratamento de erros mais detalhado
      if (error.response.status === 401) {
        console.log(`   ⚠️ API Key inválida`);
      } else if (error.response.status === 403) {
        console.log(`   ⚠️ Acesso negado`);
      } else if (error.response.status === 404) {
        console.log(`   ⚠️ Endpoint não encontrado`);
        console.log(`   Verifique se o índice 'api_publica_tjsp' existe`);
      } else if (error.response.status === 400) {
        console.log(`   ⚠️ Query inválida`);
        console.log(`   Resposta: ${JSON.stringify(error.response.data)}`);
      }
    }
    
    console.log('');

    return {
      processos: [],
      stats: { 
        erro: error.message,
        status: error.response?.status
      }
    };
  }
}

module.exports = { buscarProcessosESAJ };
